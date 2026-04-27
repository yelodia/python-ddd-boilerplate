"""
Раз уж это in-memory хранилища, то можно не заморачиваемся и просто складировать доменные объекты AS IS в словаре.
Словарь - всего-навсего для лаконичного и быстрого поиска нужного экземпляра по ID.
Никаких мапперов, никаких промежуточных моделей.
"""
from core.shop.entities import Product, Cart
from core.shop.exceptions import ProductNotFoundError, CartNotFoundError
from core.shop.repo_interfaces import ProductRepository, CartRepository


class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._auto_increment_id = 0

    async def get_by_id(self, product_id: int) -> Product:
        product = self._products.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        return product

    async def get_many_by_ids(self, product_ids: list[int]) -> dict[int, Product]:
        return {pid: self._products[pid] for pid in product_ids if pid in self._products}

    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Product]:
        products = sorted(self._products.values(), key=lambda p: p.id)
        return products[offset:offset + limit]

    async def create(self, product: Product) -> Product:
        if product.id:
            raise ValueError("Product with ID is cannot be created. Use update method instead.")

        self._auto_increment_id += 1

        product.assign_to_id(self._auto_increment_id)
        self._products[self._auto_increment_id] = product

        return product

    async def update(self, product: Product) -> None:
        if not product.id:
            raise ValueError("Product without ID is cannot be updated")

        self._products[product.id] = product

    async def delete(self, product_id: int) -> None:
        self._products.pop(product_id, None)


class InMemoryCartRepository(CartRepository):
    def __init__(self) -> None:
        self._carts: dict[int, Cart] = {}
        self._auto_increment_id = 0

    async def get_by_id(self, cart_id: int) -> Cart:
        cart = self._carts.get(cart_id)
        if not cart:
            raise CartNotFoundError(f"Cart with ID {cart_id} not found")
        return cart

    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Cart]:
        carts = sorted(self._carts.values(), key=lambda c: c.id)
        return carts[offset:offset + limit]

    async def create(self, cart: Cart) -> Cart:
        if cart.id:
            raise ValueError("Cart with ID is cannot be created. Use update method instead.")

        self._auto_increment_id += 1

        cart.assign_to_id(self._auto_increment_id)
        self._carts[self._auto_increment_id] = cart

        return cart

    async def update(self, cart: Cart) -> None:
        if not cart.id:
            raise ValueError("Cart without ID is cannot be updated")

        self._carts[cart.id] = cart

    async def delete(self, cart_id: int) -> None:
        self._carts.pop(cart_id, None)

    async def get_carts_with_product(self, product_id: int) -> list[Cart]:
        return [
            cart for cart in self._carts.values()
            if any(item.product_id == product_id for item in cart.items)
        ]
