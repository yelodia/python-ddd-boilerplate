from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.entity_base import Aggregate, ValueObject, Entity
from core.shop.events import (
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
    CartUpdated,
    ProductWasTakenFromShelf,
    ProductWasReturnedToShelf,
    ProductChanged,
)
from core.shop.exceptions import (
    WrongCartItemPcsError,
    CartIsFullError,
    BadDeliveryAddressError,
    ProductNotFoundError,
    NotEnoughStockError,
)


@dataclass(kw_only=True)
class Product(Entity):  # товар на полке магазина / товар на витрине
    name: str
    price: float
    description: str
    stock: int = 0  # количество единиц товара на полке
    _events: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        if self.stock < 0:
            raise ValueError('Количество товара на полке не может быть отрицательным')

    def take_from_shelf(self, pcs: int) -> None:
        """Уменьшает остаток на полке (покупатель положил товар в корзину)."""
        if pcs < 1:
            raise ValueError('Количество должно быть не менее 1')
        if self.stock < pcs:
            raise NotEnoughStockError(
                f'Недостаточно товара на полке: запрошено {pcs}, доступно {self.stock}'
            )
        self.stock -= pcs
        self._events.append(ProductWasTakenFromShelf(product_id=self.id, pcs=pcs))
        self._events.append(ProductChanged(product_id=self.id))

    def return_to_shelf(self, pcs: int) -> None:
        """Увеличивает остаток на полке (покупатель убрал товар из корзины)."""
        if pcs < 1:
            raise ValueError('Количество должно быть не менее 1')
        self.stock += pcs
        self._events.append(ProductWasReturnedToShelf(product_id=self.id, pcs=pcs))
        self._events.append(ProductChanged(product_id=self.id))

    def stock_replenishment(self, new_stock_qty: int) -> None:
        """Пополняет остаток на полке (условный "мерчендайзер" положил товар на полку)."""
        if new_stock_qty < 1:
            raise ValueError('Количество должно быть не менее 1')
        self.stock = new_stock_qty
        self._events.append(ProductChanged(product_id=self.id))

    def update(self, name: str, price: float, description: str) -> None:
        """Обновляет витринные данные товара и поднимает событие об изменении."""
        self.name = name
        self.price = price
        self.description = description
        self._events.append(ProductChanged(product_id=self.id))


@dataclass
class Cart(Aggregate):
    """
    Модель покупательской корзины
    С позиции бизнеса - это просто перечень товаров и их кол-во, которое покупатель ещё только намеревается приобрести.
    Перечень может спокойно меняться при соблюдении некоторых условий (инвариантов), до тех пор,
    пока покупатель не перейдёт к следующему шагу - оплате - тогда "корзина" уже трансформируется в "заказ" (см. Order).

    Это агрегат - потому что корзинка сама отвечает за своё содержимое и защищает её от недопустимых состояний.
    Поэтому все внешние манипуляции, влияющие на её состояния - строго только через агрегат (его методы)!
    Снаружи его допустимо только читать, но не изменять текущее состояние!
    """

    items: list[CartItem] = field(default_factory=list)
    delivery_address: DeliveryAddress | None = None
    created_at: datetime | None = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    _events: list = field(default_factory=list, init=False, repr=False)

    @property
    def total_amount(self) -> float:
        return sum(item.cost for item in self.items)

    def put_product(self, product: Product, pcs: int) -> None:
        if not product.is_persisted() or not product.id:
            # FIXME определиться в тем, как проверять наличие ID у сущности:
            #  через метод или напрямую сравнивать с None?
            raise ValueError('Нельзя положить в корзину товар, который ещё не записан в БД')

        if not issubclass(type(product), Product):
            raise TypeError(f'В корзину можно положить только товар, а не {type(product)}')

        if len(self.items) > 100:
            raise CartIsFullError('Корзина переполнена!')

        existed_item = next((x for x in self.items if x.product_id == product.id), None)

        if not existed_item:
            cart_item = CartItem(product_id=product.id, price=product.price, pcs=pcs)
            self.items.append(cart_item)

        if existed_item:
            existed_item.add(pcs)

        self._events.append(ProductWasAddedToCart(product_id=product.id, cart_id=self.id, pcs=pcs))
        self._events.append(CartUpdated(cart_id=self.id))

    """
    Альтернативный вариант, как можно реализовать бизнес-процедуру "положить товар в корзину":
    - корзине _кто-то_ просто сообщает ID товара, его цену и количество
    - корзина по прежнему проверяет собственные инварианты, но уже ничего не знает о товаре, просто требует 
    предоставить ей все необходимые данные.
    
    Остальную часть примера и бизнес-логики см. в сервисе Shopping.
    """

    def alternate_put_product(self, product_id: int, price: float, pcs: int) -> None:
        if len(self.items) > 100:
            raise CartIsFullError('Корзина переполнена!')

        existed_item = next((x for x in self.items if x.product_id == product_id), None)

        if not existed_item:
            cart_item = CartItem(product_id=product_id, price=price, pcs=pcs)
            self.items.append(cart_item)

        if existed_item:
            existed_item.add(pcs)

        self._events.append(ProductWasAddedToCart(product_id=product_id, cart_id=self.id, pcs=pcs))
        self._events.append(CartUpdated(cart_id=self.id))

    # TODO имплементировать уменьшение количества товара в корзине

    def remove_product(self, product_id: int) -> None:
        found_item = next((x for x in self.items if x.product_id == product_id), None)

        if not found_item:
            raise ProductNotFoundError(f'Товара с id {product_id} нет в корзине')

        self.items.remove(found_item)
        self._events.append(ProductWasRemovedFromCart(product_id=product_id, cart_id=self.id, pcs=found_item.pcs))
        self._events.append(CartUpdated(cart_id=self.id))

    def clear(self) -> None:
        for product_id, pcs in [(item.product_id, item.pcs) for item in self.items]:
            self._events.append(ProductWasRemovedFromCart(product_id=product_id, cart_id=self.id, pcs=pcs))
        self.items = []
        self._events.append(CartWasCleared(cart_id=self.id))
        self._events.append(CartUpdated(cart_id=self.id))

    def update_delivery_address(self, delivery_address: DeliveryAddress) -> None:
        if not issubclass(type(delivery_address), DeliveryAddress):
            raise TypeError(f'Адрес доставки должен быть типа {DeliveryAddress}, а не {type(delivery_address)}')

        self.delivery_address = delivery_address


@dataclass
class CartItem:
    product_id: int
    price: float
    pcs: int

    @property
    def cost(self) -> float:
        return self.pcs * self.price

    def __post_init__(self):
        if self.pcs < 1:
            raise WrongCartItemPcsError('Количество товаров должно быть 1 или больше')

    def add(self, pcs: int) -> None:
        if self.pcs < 1 or self.pcs + pcs > 10:
            raise WrongCartItemPcsError('Количество товаров в корзине должно быть не менее 1, но не более 10')

        self.pcs += pcs

    # TODO имплементировать уменьшение количества товара в корзине


@dataclass(frozen=True)
class DeliveryAddress(ValueObject):
    # объект-значение - потому что адрес просто коробка для нескольких полей из сущности Cart
    city: str
    street: str
    house: str
    apartment: int

    def __post_init__(self):
        if self.apartment < 1:
            raise BadDeliveryAddressError('Номер квартиры не может быть отрицательным или нулевым')


@dataclass
class Order:
    """
    Заказ - описывает покупательскую корзинку, перешедшую в стадию оплаты.
    С точки зрения бизнеса это уже другой объект со своими инвариантами и жизненным циклом:

        - ему не интересны правила старой "корзины", ему нужны лишь её данные о товарах, их количестве и т.п.

        - заказ уже никак не связан с товарами на витрине:
            - товар из корзины можно вернуть на полку
            - товар из заказа - нет, потому что он уже покидает пределы магазина

        - перечень товаров, их количество и стоимость фиксируются и защищается от изменений
            - отныне заказ может быть обработан либо целиком, либо отменён (тоже целиком)
            - нельзя отменить только часть заказа или что-то добавить в уже оплаченный заказ
            - потому что бизнес не хочет настолько усложнять собственные бизнес-процессы: кассу, склад, логистику и т.п.

        - "стоимость товаров" меняет свою роль:
            - это уже не просто "ценник на витрине" или "цена * количество"
            - теперь это базовые значения для всяких купонов и скидок!

        - к заказу могут применяться товарные акции ("2+1", "фигня в подарок от трёх тыщ" и т.п.)
            - некий акционный товар автоматически добавляется к составу заказа, хотя может иметь нулевую стоимость
        - к заказу могут применяться скидки и промоакции ("10% скидка на первую покупку" и т.п.)
            - не зависят от конкретных товаров, только от их общей стоимости или стоимости конкретной позиции заказа


        - статус имеет собственный жизненный цикл, который уже никак не зависит от жизненного цикла корзины
            - formed - сформирован, ожидает подтверждения (начальное состояние, последний шанс изменить состав)
            - confirmed - подтверждён, ожидает оплаты (это происходит всё ещё в магазине, но перечень уже зафиксирован)
            - paid - оплачен, ожидает передачи в службу доставки (это сообщит платёжный шлюз / эквайринг)
            - shipped - в пути (это сообщит служба логистики)
            - delivered - доставлен (это сообщит служба доставки/логистики)
            - cancelled - отменён (на любой стадии)

        - и т.п.
    """
