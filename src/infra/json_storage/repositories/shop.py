from pathlib import Path

from pydantic import BaseModel

from core.shop.entities import Product, Cart, CartItem, DeliveryAddress
from core.shop.execptions import ProductNotFoundError, CartNotFoundError
from core.shop.repositories import ProductRepository, CartRepository
from infra.json_storage.repositories._base_class import JsonRepositoryBase


class ProductInStorage(BaseModel):
    # типа, симулякр ORM-модельки - нужен просто чтобы поменьше возиться со словарями
    # должен предъявлять требования к полям не строже, чем доменная сущность
    id: int
    name: str
    price: float
    description: str


class JsonProductRepository(ProductRepository, JsonRepositoryBase):
    def __init__(self, data_dir: str = "data") -> None:
        self._path = Path(data_dir) / "products.json"
        self._create_if_not_exists(self._path)

    async def get_by_id(self, product_id: int) -> Product:
        table = await self._load()

        product = next((x for x in table.data if x["id"] == product_id), None)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")

        return self._to_domain(ProductInStorage(**product))

    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Product]:
        table = await self._load()
        return [
            self._to_domain(ProductInStorage(**product))
            for product
            in table.data[offset: offset + limit]
        ]

    async def create(self, product: Product) -> Product:
        table = await self._load()
        table.auto_increment_id += 1

        if product.id:
            raise ValueError("Product with ID is cannot be created. Use update method instead.")

        record = ProductInStorage(
            id=table.auto_increment_id,
            name=product.name,
            price=product.price,
            description=product.description,
        )
        product_with_id = self._to_domain(record)

        table.data.append(record.model_dump(mode='json'))
        await self._save(table)

        return product_with_id

    async def update(self, product: Product) -> None:
        table = await self._load()

        if not product.id:
            raise ValueError("Product without ID is cannot be updated")

        updated_record = ProductInStorage(
            id=product.id,
            name=product.name,
            price=product.price,
            description=product.description,
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
            id=record.id,  # FIXME какая-то ошибка ожидаемых типов
            name=record.name,
            price=record.price,
            description=record.description,
        )


class CartInStorage(BaseModel):
    # типа, симулякр ORM-модельки - нужен просто чтобы поменьше возиться со словарями
    # должен предъявлять требования к полям не строже, чем доменная сущность
    id: int
    items: list[CartItemInStorage] = []
    delivery_address: DeliveryAddressInStorage | None = None


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

        cart = next((x for x in table.data if x["id"] == cart_id), None)
        if not cart:
            raise CartNotFoundError(f"Cart with ID {cart_id} not found")

        return self._to_domain(CartInStorage(**cart))

    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Cart]:
        table = await self._load()
        return [
            self._to_domain(CartInStorage(**cart))
            for cart
            in table.data[offset: offset + limit]
        ]

    async def create(self, cart: Cart) -> Cart:
        table = await self._load()
        table.auto_increment_id += 1

        if cart.id:
            raise ValueError("Cart with ID is cannot be created. Use update method instead.")

        record = CartInStorage(
            id=table.auto_increment_id,
            items=[CartItemInStorage(
                product_id=x.product_id,
                price=x.price,
                pcs=x.pcs,
            ) for x in cart.items],
            delivery_address=DeliveryAddressInStorage(
                city=cart.delivery_address.city,
                street=cart.delivery_address.street,
                house=cart.delivery_address.house,
                apartment=cart.delivery_address.apartment,
            ) if cart.delivery_address else None,
        )
        cart_with_id = self._to_domain(record)

        table.data.append(record.model_dump(mode='json'))
        await self._save(table)
        return cart_with_id

    async def update(self, cart: Cart) -> None:
        table = await self._load()

        if not cart.id:
            raise ValueError("Cart without ID is cannot be updated")

        updated_record = CartInStorage(
            id=cart.id,
            items=[CartItemInStorage(
                product_id=x.product_id,
                price=x.price,
                pcs=x.pcs,
            ) for x in cart.items],
            delivery_address=DeliveryAddressInStorage(
                city=cart.delivery_address.city,
                street=cart.delivery_address.street,
                house=cart.delivery_address.house,
                apartment=cart.delivery_address.apartment,
            ) if cart.delivery_address else None,
        ).model_dump(mode='json')

        for idx, record in enumerate(table.data):
            if record["id"] == cart.id:
                table.data[idx] = updated_record
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
        )
