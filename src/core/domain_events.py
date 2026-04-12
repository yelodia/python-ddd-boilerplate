from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid7


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid7, init=False)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc), init=False)
