from application.event_bus_interface import EventHandlersRegistry
from application.reports.event_handlers import StockReportRequestedHandler
from application.shop.event_handlers import (
    NewCartCreatedHandler,
    ProductWasAddedToCartHandler,
    ProductWasRemovedFromCartHandler,
    CartWasClearedHandler,
    ProductShelfEventHandler,
    StockReplenishmentRequestedHandler,
)
from core.shop.events import (
    NewCartCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
    ProductWasTakenFromShelf,
    ProductWasReturnedToShelf,
    TheMorningHasCome,
    StockReportRequested,
)

"""
Регистр доменных событий.

Здесь обработчики событий ассоциируются с конкретными событиями.

На одно событие может быть назначено несколько обработчиков, особенно если из разных доменов - это вполне ок, 
для того шина с регистром и существуют.

Один обработчик может быть заинтересован в нескольких событиях, это тоже нормальная история, но тогда он будет
обязан уметь работать со всеми типами событий, с которыми он связан. Единственное место,
где это явно декларируется - это данный регистр. Сигнатуры методов .handle() роли не играют и никак не учитываются 
шиной - она просто пинает обработчик каждый раз, когда в ней появляется объект подходящего события.

После создания в системе нового обработчика - его нужно обязательно добавить в этот реестр,
иначе он не будет работать, так как EventBus не будет знать о его существовании и не сможет его вызвать.

При создании нового события (пока ещё без обработчика) - добавлять его в реестр не обязательно, но желательно.
В целом ничего криминального не случится, но без регистрации в реестре про это событие потенциально можно забыть,
или что оно вообще существует в коде и что к нему нужно дописать обработчик.
"""
EVENT_HANDLERS: EventHandlersRegistry = {
    NewCartCreated: [NewCartCreatedHandler],
    ProductWasAddedToCart: [ProductWasAddedToCartHandler],
    ProductWasRemovedFromCart: [ProductWasRemovedFromCartHandler],
    CartWasCleared: [CartWasClearedHandler],
    ProductWasTakenFromShelf: [ProductShelfEventHandler],
    ProductWasReturnedToShelf: [ProductShelfEventHandler],
    TheMorningHasCome: [
        StockReplenishmentRequestedHandler,  # пополняет запасы товаров на полках (условный "мерчендайзер")
        # Раз уж событие "наступило утро" специально столь расплывчатое, то это хороший пример хотелки бизнеса,
        # чтобы с одного события стартовало сразу несколько разных бизнес-процессов из самых разных bounded context'ов.
        # Например:
        # - проверить, открыта ли касса (если нет - отправить уведомление ответственному сотруднику)
        # - зажечь уличную вывеску (допустим, она работает от умного реле с WiFi и имеет API для управления)
        # - запустить кофемашину для сотрудников (ну тут точно ssh-сессия на кофемашину с Linux внутри, 100%)
        # - и т.д.
    ],
    StockReportRequested: [StockReportRequestedHandler],  # отчёт триггерится отдельным событием, так хочет бизнес
}
