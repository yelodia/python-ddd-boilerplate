from application.shop.ws_notifications import (
    CartChangedWsNotification,
    ProductChangedWsNotification,
    ProductCreatedWsNotification,
)
from application.ws_publisher_interface import WsEventsRegistry
from core.shop.events import CartUpdated, ProductCreated, ProductChanged

"""
Регистр событий для публикации в websocket'ы.

Здесь агрегатные доменные события ассоциируются с WS-уведомлениями, которые шина доставит
подключённым клиентам в момент publish().

Правило одно: здесь должны упоминаться только те события, о которых необходимо уведомить клиентов через 
websocket.

Рекомендация: паттерн "thin beacon" - WS-уведомление просто сообщает клиенту, что "штука изменилась", а
клиент уже сам решает, нужно ли ему перезапрашивать данные или нет.

Для него обычно достаточно просто сообщить что-то в духе "штука изменилась, ID штуки такой-то".
Проще всего для этого завести отдельное доменное событие с обобщённым смыслом ("штука КАК-ТО изменилась")
и разложить его там, где оно случается нежели, агрегировать нужные данные (ID) из кучи разрозненных бизнес-событий,
которые уже существуют в системе.

Это позволит избежать раздувания маппинга внутри объектов WS-уведомлений, а так же не будет усиливать связанность между
существующими доменными событиями и оповещениями по вебсокету, а значит будет проще отслеживать кто и когда что пушит.

WsEventsRegistry:
    ключ - тип доменного события
    значение - класс WsNotification (должен реализовать from_event())
"""

WS_EVENTS: WsEventsRegistry = {
    ProductChanged: ProductChangedWsNotification,
    ProductCreated: ProductCreatedWsNotification,
    CartUpdated: CartChangedWsNotification,
}
