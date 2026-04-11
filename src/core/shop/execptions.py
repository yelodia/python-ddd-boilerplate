from common.exceptions import DomainError, NotFoundError


class WrongCartItemPcsError(DomainError):
    pass


class CartIsFullError(DomainError):
    pass


class BadDeliveryAddressError(DomainError):
    pass


class ProductNotFoundError(NotFoundError):
    pass


class CartNotFoundError(NotFoundError):
    pass
