from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid7


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    # TODO на время разработки показ ID события и его даты скрыты, чтобы не загромождать логи
    event_id: UUID = field(default_factory=uuid7, repr=False)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc), repr=False)
