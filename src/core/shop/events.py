from dataclasses import dataclass

from core.domain_events import DomainEvent


@dataclass(frozen=True)
class NewCartCreated(DomainEvent):
    cart_id: int


@dataclass(frozen=True)
class ProductWasAddedToCart(DomainEvent):
    product_id: int
    cart_id: int
    pcs: int


@dataclass(frozen=True)
class ProductWasRemovedFromCart(DomainEvent):
    product_id: int
    cart_id: int
    pcs: int


@dataclass(frozen=True)
class CartWasCleared(DomainEvent):
    cart_id: int


@dataclass(frozen=True)
class ProductWasTakenFromShelf(DomainEvent):
    product_id: int
    pcs: int


@dataclass(frozen=True)
class ProductWasReturnedToShelf(DomainEvent):
    product_id: int
    pcs: int


@dataclass(frozen=True)
class TheMorningHasCome(DomainEvent):
    pass


@dataclass(frozen=True)
class StockReportRequested(DomainEvent):
    pass
