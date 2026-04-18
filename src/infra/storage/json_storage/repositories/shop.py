from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from core.shop.entities import Product, Cart, CartItem, DeliveryAddress
from core.shop.exceptions import ProductNotFoundError, CartNotFoundError
from core.shop.repo_interfaces import ProductRepository, CartRepository
from infra.storage.json_storage.repositories._base_class import JsonRepositoryBase


class ProductInStorage(BaseModel):
    """
    Симулякр ORM-модельки - используется здесь только для того, чтобы чуть меньше возиться со словарями.

    Как и настоящие ORM - должен предъявлять требования к полям не строже, чем доменная сущность.

    Дефолтные значения могут быть заданы только для тех полей, которые могут отсутствовать в хранилище.
    Например, если хранилище не успело мигрировать или это особенность самого хранилища - просто не выдавать поле,
    если его значение None.

    "Чинить" данные на лету - не самая лучшая идея с точки зрения DDD, но в редких случаях
    это может быть оправдано. Например, чтобы при восстановлении доменного объекта из raw-данных быть уверенным,
    что полю X будет передано явное значение None, а не "данных для поля X нет => запуск дефолтной фабрики поля X".
    """
    id: int
    name: str
    price: float
    description: str
    stock: int = 0  # дефолт 0 — на случай старых записей без этого поля


class JsonProductRepository(ProductRepository, JsonRepositoryBase):
    def __init__(self, data_dir: str = "data") -> None:
        self._path = Path(data_dir) / "products.json"
        self._create_if_not_exists(self._path)

    async def get_by_id(self, product_id: int) -> Product:
        table = await self._load()

        raw_product = next((x for x in table.data if x["id"] == product_id), None)
        if not raw_product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")

        return self._to_domain(ProductInStorage(**raw_product))

    async def get_many_by_ids(self, product_ids: list[int]) -> dict[int, Product]:
        table = await self._load()
        ids_set = set(product_ids)
        return {
            record["id"]: self._to_domain(ProductInStorage(**record))
            for record in table.data
            if record["id"] in ids_set
        }

    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Product]:
        table = await self._load()
        return [
            self._to_domain(ProductInStorage(**product))
            for product in table.data[offset: offset + limit]
        ]

    async def create(self, product: Product) -> Product:
        table = await self._load()
        table.auto_increment_id += 1

        if product.id:
            raise ValueError("Product with ID is cannot be created. Use update method instead.")

        # теперь это правда доменная сущность, а не "просто DTO без ID"
        product.assign_to_id(table.auto_increment_id)

        # маппинг из доменной сущности в модель хранилища
        record = ProductInStorage(
            id=table.auto_increment_id,
            name=product.name,
            price=product.price,
            description=product.description,
            stock=product.stock,
        )

        table.data.append(record.model_dump(mode='json'))
        await self._save(table)

        return product

    async def update(self, product: Product) -> None:
        table = await self._load()

        if not product.id:
            raise ValueError("Product without ID is cannot be updated")

        updated_record = ProductInStorage(
            id=product.id,
            name=product.name,
            price=product.price,
            description=product.description,
            stock=product.stock,
        ).model_dump(mode='json')

        for idx, record in enumerate(table.data):
            if record["id"] == product.id:
                table.data[idx] = updated_record
                break

        await self._save(table)

    async def delete(self, product_id: int) -> None:
        table = await self._load()
        products = [record for record in table.data if record["id"] != product_id]
        table.data = products
        await self._save(table)

    @staticmethod
    def _to_domain(record: ProductInStorage) -> Product:
        return Product(
            id=record.id,
            name=record.name,
            price=record.price,
            description=record.description,
            stock=record.stock,
        )


class CartInStorage(BaseModel):
    """
    Симулякр ORM-модельки - используется здесь только для того, чтобы чуть меньше возиться со словарями.

    Как и настоящие ORM - должен предъявлять требования к полям не строже, чем доменная сущность.

    Дефолтные значения могут быть заданы только для тех полей, которые могут отсутствовать в хранилище.
    Например, если хранилище не успело мигрировать или это особенность самого хранилища - просто не выдавать поле,
    если его значение None.

    "Чинить" данные на лету - не самая лучшая идея с точки зрения DDD, но в редких случаях
    это может быть оправдано. Например, чтобы при восстановлении доменного объекта из raw-данных быть уверенным,
    что полю X будет передано явное значение None, а не "данных для поля X нет => запуск дефолтной фабрики поля X".

    P.S.: для created_at используется строковый ISO формат даты, т.к. в JSON нет аналога datetime.
    """
    id: int
    items: list[CartItemInStorage]
    delivery_address: DeliveryAddressInStorage | None
    created_at: str | None = None


class CartItemInStorage(BaseModel):
    product_id: int
    price: float
    pcs: int


class DeliveryAddressInStorage(BaseModel):
    city: str
    street: str
    house: str
    apartment: int


class JsonCartRepository(CartRepository, JsonRepositoryBase):
    def __init__(self, data_dir: str = "data") -> None:
        self._path = Path(data_dir) / "carts.json"
        self._create_if_not_exists(self._path)

    async def get_by_id(self, cart_id: int) -> Cart:
        table = await self._load()

        raw_cart = next((x for x in table.data if x["id"] == cart_id), None)
        if not raw_cart:
            raise CartNotFoundError(f"Cart with ID {cart_id} not found")

        return self._to_domain(CartInStorage(**raw_cart))

    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Cart]:
        table = await self._load()
        return [
            self._to_domain(CartInStorage(**cart))
            for cart in table.data[offset: offset + limit]
        ]

    async def create(self, cart: Cart) -> Cart:
        table = await self._load()
        table.auto_increment_id += 1

        if cart.id:
            raise ValueError("Cart with ID is cannot be created. Use update method instead.")

        # теперь это правда доменная сущность, а не "просто DTO без ID"
        cart.assign_to_id(table.auto_increment_id)

        # маппинг из доменной сущности в модель хранилища
        record = self._from_domain(table.auto_increment_id, cart)

        table.data.append(record.model_dump(mode='json'))
        await self._save(table)
        return cart

    async def update(self, cart: Cart) -> None:
        table = await self._load()

        if not cart.id:
            raise ValueError("Cart without ID is cannot be updated")

        # маппинг из доменной сущности в модель хранилища
        updated_record = self._from_domain(cart.id, cart)

        for idx, record in enumerate(table.data):
            if record["id"] == cart.id:
                table.data[idx] = updated_record.model_dump(mode='json')
                break

        await self._save(table)

    async def delete(self, cart_id: int) -> None:
        table = await self._load()
        carts = [record for record in table.data if record["id"] != cart_id]
        table.data = carts
        await self._save(table)

    @staticmethod
    def _to_domain(record: CartInStorage) -> Cart:
        """Преобразует запись из хранилища в доменную сущность Cart"""
        return Cart(
            id=record.id,
            items=[CartItem(
                product_id=cart_item.product_id,
                price=cart_item.price,
                pcs=cart_item.pcs,
            ) for cart_item in record.items],
            delivery_address=DeliveryAddress(
                city=record.delivery_address.city,
                street=record.delivery_address.street,
                house=record.delivery_address.house,
                apartment=record.delivery_address.apartment,
            ) if record.delivery_address else None,
            created_at=datetime.fromisoformat(record.created_at) if record.created_at else None,
            # fromisoformat() до Python 3.11 не понимает суффикс Z (только +00:00)!
        )

    @staticmethod
    def _from_domain(record_id: int, cart: Cart) -> CartInStorage:
        """Преобразует доменную сущность Cart в запись для хранилища"""
        return CartInStorage(
            id=record_id,
            items=[CartItemInStorage(
                product_id=cart_item.product_id,
                price=cart_item.price,
                pcs=cart_item.pcs,
            ) for cart_item in cart.items],
            delivery_address=DeliveryAddressInStorage(
                city=cart.delivery_address.city,
                street=cart.delivery_address.street,
                house=cart.delivery_address.house,
                apartment=cart.delivery_address.apartment,
            ) if cart.delivery_address else None,
            created_at=cart.created_at.isoformat() if cart.created_at else None,
        )
