from abc import ABC, abstractmethod

from core.shop.entities import Product, Cart

"""
Памятка про CQC (Command-Query Separation Principle):
    Методы должны либо изменять состояние, либо возвращать данные, но не делать и то, и другое одновременно!
  
В противном случае, роль метода становится размытой и неочевидной, что может привести к
нежелательным side effects, трудно отслеживаемым багам и повышенной связанности кода.
    
Например:
    @ хотели что-то прочитать, схватили первый попавшийся метод с подходящим ответом
    @ оказалось, что попутно ещё и поменяли чье-то состояние, вызвав слом в другой части системы
    @ при этом взаимосвязь между этими событиями будет совершенно неочевидна
        Блин, работало же! Ничего не делал, а оно само сломалось! (правильно, потому что сделал кто-то другой)
    @ придётся проверять вообще все шаги во всех недавно менявшихся компонентах и искать между ними точки контакта
  
Да, от этого принципа можно отступать, но нужно:
    - четко понимать, для чего это делается это исключение и какие риски оно влечёт за собой
    - следить и контролировать, чтобы метод не превратился в big ball of mud
"""


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product: ...

    @abstractmethod
    async def get_many_by_ids(self, product_ids: list[int]) -> dict[int, Product]:  # пример batch-операции
        # Возвращает только найденные записи. Репозиторий не знает бизнес-контекст —
        # решение о том, как реагировать на пропуски, остаётся за вызывающим кодом.
        pass

    @abstractmethod
    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Product]: ...

    @abstractmethod
    async def create(self, product: Product) -> Product:
        # если за назначение ID отвечает БД, то на выходе нужен либо этот ID,
        # либо готовый, валидный объект с уже назначенным ID
        # TODO нарушение CQC, потенциальный источник нежелательных side effects
        pass

    @abstractmethod
    async def update(self, product: Product) -> None: ...

    @abstractmethod
    async def delete(self, product_id: int) -> None: ...


class CartRepository(ABC):
    @abstractmethod
    async def get_by_id(self, cart_id: int) -> Cart: ...

    @abstractmethod
    async def get_slice(self, offset: int = 0, limit: int = 20) -> list[Cart]: ...

    @abstractmethod
    async def create(self, cart: Cart) -> Cart:
        # если за назначение ID отвечает БД, то нужен валидный объект с уже назначенным ID
        # TODO нарушение CQC, потенциальный источник нежелательных side effects
        pass

    @abstractmethod
    async def update(self, cart: Cart) -> None: ...

    @abstractmethod
    async def delete(self, cart_id: int) -> None: ...

    @abstractmethod
    async def get_carts_with_product(self, product_id: int) -> list[Cart]: ...
