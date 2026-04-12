from application.shop.commands import (
    ShowAllProductsCmd,
    CreateProductCmd,
    CreateEmptyCartCmd,
    ShowAllCartsCmd,
    PutProductToCartCmd,
    ShowCartCmd,
)
from common.use_case_base import UseCase, UowFactory
from core.shop.entities import Product, Cart
from core.shop.repo_interfaces import ProductRepository, CartRepository


class ShowAllProductsUseCase(UseCase):
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def execute(self, cmd: ShowAllProductsCmd) -> list[Product]:
        return await self.repo.get_slice(cmd.offset, cmd.limit)


class CreateProductUseCase(UseCase):
    def __init__(self, repo: ProductRepository, uow: UowFactory):
        self.repo = repo
        self.uow = uow

    async def execute(self, cmd: CreateProductCmd) -> Product:
        new_product = Product(
            # да, мы создаем продукт без объявления ID,
            # потому что он будет сгенерирован в момент записи в БД
            name=cmd.name,
            price=cmd.price,
            description=cmd.description,
        )
        async with self.uow():
            product_with_id = await self.repo.create(new_product)

        return product_with_id


class ShowAllCartsUseCase(UseCase):
    def __init__(self, repo: CartRepository):
        self.repo = repo

    async def execute(self, cmd: ShowAllCartsCmd) -> list[Cart]:
        return await self.repo.get_slice(cmd.offset, cmd.limit)


class ShowCartUseCase(UseCase):
    def __init__(self, repo: CartRepository):
        self.repo = repo

    async def execute(self, cmd: ShowCartCmd) -> Cart:
        return await self.repo.get_by_id(cmd.cart_id)


class CreateEmptyCartUseCase(UseCase):
    def __init__(self, repo: CartRepository, uow: UowFactory):
        self.repo = repo
        self.uow = uow

    async def execute(self, cmd: CreateEmptyCartCmd) -> Cart:
        empty_cart = Cart()
        async with self.uow():
            persisted_cart = await self.repo.create(empty_cart)

        return persisted_cart


class PutProductToCartUseCase(UseCase):
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository, uow: UowFactory):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.uow = uow

    async def execute(self, cmd: PutProductToCartCmd) -> Cart:
        async with self.uow():
            cart = await self.cart_repo.get_by_id(cmd.cart_id)
            product = await self.product_repo.get_by_id(cmd.product_id)

            cart.put_product(product, cmd.pcs)

            async with self.uow():
                await self.cart_repo.update(cart)

            return cart
