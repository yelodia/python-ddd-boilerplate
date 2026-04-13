from application.event_bus_stuff import EventHandlersRegistry
from application.shop.event_handlers import (
    NewCartCreatedHandler,
    ProductWasAddedToCartHandler,
    ProductWasRemovedFromCartHandler,
    CartWasClearedHandler,
)
from core.shop.events import (
    NewCartCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
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
}
