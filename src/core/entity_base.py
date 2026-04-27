from dataclasses import dataclass, field

from core.domain_events import EventsEngine


# Запрещаем dataclass автоматически генерировать __eq__ метод,
#  потому что мы хотим сравнивать сущности строго только по id, а не по всем полям - этого требует DDD
@dataclass(eq=False)
class Entity:
    id: int | None = field(default=None)
    events: EventsEngine = field(default_factory=EventsEngine, init=False, repr=False)

    def assign_to_id(self, value: int) -> None:
        """
        Устанавливает ID для сущности.
        ID может быть установлен только один раз и не может быть изменён после установки.

        Это исполнения фундаментального правила DDD, что ID сущности не могут "просто так" менять ID.

        Если этого потребует бизнес, то значит эта операция должна быть явно описана конкретным юзкейсом:
            - взять "старый" объект из хранилища,
            - переложить его данные в "новый" объект (которому будет назначен новый ID!),
            - "новый" объект записать в хранилище,
            - "старый" объект удалить из хранилища,
        а не просто обновить атрибут "где-то под капотом", потому что тогда это может привести к путанице и ошибкам!

        Данный же метод служит единственной цели: чтобы без особой инженерной головомойки СОЗНАТЕЛЬНО переводить объект
        из состояния "я пока просто коробка с данными, ещё ни разу не бывавшая в хранилище"
        в состояние "я полноценная сущность с ID, которая может полноценно участвовать в бизнес-логике",
        просто как альтернатива муторной ручной перепаковки объекта в "такой же объект, только теперь с ID"
        внутри репозиториев и НЕ БОЛЕЕ ТОГО!
        """
        if self.id:
            raise ValueError('ID is already set and cannot be changed')

        if value is None:
            raise ValueError('ID cannot be None')

        if not isinstance(value, int):
            raise TypeError(f'ID must be an integer, got {type(value)}')

        self.id = value

    def is_persisted(self) -> bool:
        # TODO определиться, какой вариант лучше - отдельный готовый метод с бизнесовым названием
        #  или просто по месту проверять на None (if not some.id: ...), потому что и так понятно что значит проверка?
        return self.id is not None

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                f'Cannot comparing entities two different types: '
                f'{type(self)} and {type(other)}'
            )

        if not self.is_persisted() or not other.is_persisted():
            raise ValueError(
                'Cannot compare non-persisted entities. '
                'Make sure both objects have non-None id.'
            )

        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


# Агрегат - это то же, что и Entity. Просто может содержать в себе
# вложенные Entity и ValueObjects, а так же сам командует ими.
@dataclass(kw_only=True, eq=False)
class Aggregate(Entity):
    pass


# Сообщаем dataclass, чтобы он сделал класс иммутабельным,
# т.е. защищённым от любых изменений после его инициализации - этого требует DDD
@dataclass(frozen=True, eq=False)
class ValueObject:
    events: EventsEngine = field(default_factory=EventsEngine, init=False, repr=False)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                f'Cannot comparing value objects two different types: '
                f'{type(self)} and {type(other)}'
            )

        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
