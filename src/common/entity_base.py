from dataclasses import dataclass, field


# Запрещаем dataclass автоматически генерировать __eq__ метод,
#  потому что мы хотим сравнивать сущности строго только по id, а не по всем полям - этого требует DDD
@dataclass(eq=False)
class Entity:
    id: int | None = field(default=None)

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
@dataclass(kw_only=True)
class Aggregate(Entity):
    pass


# Сообщаем dataclass, чтобы он сделал класс иммутабельным,
# т.е. защищённым от любых изменений после его инициализации - этого требует DDD
@dataclass(frozen=True)
class ValueObject:
    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                f'Cannot comparing value objects two different types: '
                f'{type(self)} and {type(other)}'
            )

        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
