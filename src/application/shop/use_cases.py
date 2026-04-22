from application.event_bus_interface import EventBus
from application.shop.commands import (
    ShowAllProductsCmd,
    CreateProductCmd,
    UpdateProductCmd,
    CreateEmptyCartCmd,
    ShowAllCartsCmd,
    PutProductToCartCmd,
    ShowCartCmd,
    RemoveProductFromCartCmd,
    ClearCartCmd,
)
from application.uow_interface import UowFactory
from application.use_case_base import UseCase
from core.shop.entities import Product, Cart
from core.shop.events import NewCartCreated, ProductCreated
from core.shop.repo_interfaces import ProductRepository, CartRepository
from core.shop.services import Shopping


class UpdateProductUseCase(UseCase):
    def __init__(self, repo: ProductRepository, uow: UowFactory, event_bus: EventBus):
        self.repo = repo
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, cmd: UpdateProductCmd) -> Product:
        async with self.uow():
            product = await self.repo.get_by_id(cmd.product_id)
            product.update(name=cmd.name, price=cmd.price, description=cmd.description)
            await self.repo.update(product)

        for event in product._events:
            await self.event_bus.publish(event)

        return product


class ShowAllProductsUseCase(UseCase):
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def execute(self, cmd: ShowAllProductsCmd) -> list[Product]:
        return await self.repo.get_slice(cmd.offset, cmd.limit)


class CreateProductUseCase(UseCase):
    def __init__(self, repo: ProductRepository, uow: UowFactory, event_bus: EventBus):
        self.repo = repo
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, cmd: CreateProductCmd) -> Product:
        new_product = Product(
            # да, мы создаем продукт без объявления ID,
            # потому что он будет сгенерирован в момент записи в БД
            name=cmd.name,
            price=cmd.price,
            description=cmd.description,
        )
        async with self.uow():
            product = await self.repo.create(new_product)

        await self.event_bus.publish(ProductCreated(product_id=product.id))

        return product


class ShowAllCartsUseCase(UseCase):
    def __init__(self, repo: CartRepository):
        self.repo = repo

    async def execute(self, cmd: ShowAllCartsCmd) -> list[Cart]:
        return await self.repo.get_slice(cmd.offset, cmd.limit)


class ShowCartUseCase(UseCase):
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    async def execute(self, cmd: ShowCartCmd) -> tuple[Cart, dict[int, Product]]:
        cart = await self.cart_repo.get_by_id(cmd.cart_id)

        product_ids = [item.product_id for item in cart.items]
        products_by_id = await self.product_repo.get_many_by_ids(product_ids)

        # TODO в данном конкретном юзкейсе это бессмысленно, но в других сценариях может понадобится более сложная
        #  логика обработки пропусков, например:
        #  - если пропущенных товаров нет, то всё ок, просто не отображаем их в интерфейсе,
        #  - если есть - то это уже повод для тревоги, потому что корзина содержит товары, которых нет в каталоге, и
        #  нужно разбираться, как такое могло произойти, и что с этим делать.
        missing = [pid for pid in product_ids if pid not in products_by_id]
        if missing:
            raise ValueError(f"Товары из корзины не найдены в каталоге: {missing}")

        # прежде в products_by_id был список товаров, а теперь словарь - да, это всё ещё DDD
        # потому что это всё ещё простая, плоская структура с использованием нативных типов данных
        # просто из словаря удобнее доставать продукты по ключу (product_id), вместо ручного обхода списка каждый раз
        return cart, products_by_id


class CreateEmptyCartUseCase(UseCase):
    def __init__(self, repo: CartRepository, uow: UowFactory, event_bus: EventBus):
        self.repo = repo
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, cmd: CreateEmptyCartCmd) -> Cart:
        empty_cart = Cart()
        async with self.uow():
            persisted_cart = await self.repo.create(empty_cart)

        # TODO единственная категория "особых" событий - "первое создание объекта в системе"
        #  по-хорошему, генерация таких событий должна происходить внутри домена, а здесь - только их пуш в шину.
        #  Но т.к. в данном bounded context не домен контролирует выдачу ID, то генерацией события
        #  пришлось озадачить юзкейс, хотя по смыслу - это событие не является "событием оркестрации"
        await self.event_bus.publish(NewCartCreated(cart_id=persisted_cart.id))

        return persisted_cart


class PutProductToCartUseCase(UseCase):
    """
    Образец альтернативной организации юзкейса, когда бизнес-логика вынесена в доменный сервис (Shopping).
     - юзкейс всё ещё отвечает за оркестрацию:
        - добыть штуки из хранилища
        - пнуть сервис и дать ему штуки, чтобы он выполнил какую-то логику
        - не глядя сохранить штуки обратно в хранилище (ведь сервис мог поменять их состояния):
            - обязательно обернуть в транзакцию, ведь даже внутри одной штуки могут быть;
            задействованы несколько таблиц БД, например;
        - опубликовать в шину события:
            - в простых случаях событий может и не быть вовсе;
            - в случаях посложнее - может быть достаточно одного события в конце юзкейса;
            - в сложных случаях - юзкейс должен собрать события со всех потроганных сущностей;
            и опубликовать их в шину, потому что сущности тоже могут генерировать события!
    - абсолютно вся бизнес-логика вынесена в доменные сервисы и сущности
    """

    def __init__(
            self,
            cart_repo: CartRepository,
            product_repo: ProductRepository,
            uow: UowFactory,
            event_bus: EventBus,
    ):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, cmd: PutProductToCartCmd) -> Cart:
        async with self.uow():
            cart = await self.cart_repo.get_by_id(cmd.cart_id)
            product = await self.product_repo.get_by_id(cmd.product_id)

            Shopping.put_product_to_cart(product, cart, cmd.pcs)

            await self.cart_repo.update(cart)
            await self.product_repo.update(product)

        for event in product._events:
            await self.event_bus.publish(event)

        for event in cart._events:
            await self.event_bus.publish(event)

        return cart


class RemoveProductFromCartUseCase(UseCase):
    def __init__(
            self,
            cart_repo: CartRepository,
            product_repo: ProductRepository,
            uow: UowFactory,
            event_bus: EventBus,
    ):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, cmd: RemoveProductFromCartCmd) -> Cart:
        async with self.uow():
            cart = await self.cart_repo.get_by_id(cmd.cart_id)
            cart.remove_product(cmd.product_id)
            await self.cart_repo.update(cart)

        # ProductWasRemovedFromCart уходит в шину — хендлер вернёт товар на полку
        # CartUpdated уходит в шину — шина сама пошлёт WS-уведомление клиентам корзины
        for event in cart._events:
            await self.event_bus.publish(event)

        return cart


class ClearCartUseCase(UseCase):
    def __init__(self, cart_repo: CartRepository, uow: UowFactory, event_bus: EventBus):
        self.cart_repo = cart_repo
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, cmd: ClearCartCmd) -> Cart:
        async with self.uow():
            cart = await self.cart_repo.get_by_id(cmd.cart_id)
            cart.clear()
            await self.cart_repo.update(cart)

        # ProductWasRemovedFromCart × N + CartWasCleared + CartUpdated уходят в шину
        for event in cart._events:
            await self.event_bus.publish(event)

        return cart
