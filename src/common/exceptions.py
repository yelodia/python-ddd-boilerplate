class DomainError(Exception):
    """Base class for domain exceptions."""


class NotFoundError(DomainError):
    """Base class for all not-found-like errors."""


class RateLimitError(DomainError):
    """Example of CROSS-DOMAIN error, which can used everywhere (inside any domains)."""


class AllFuckedUpError(DomainError):
    """Example of CROSS-DOMAIN error, which can used everywhere (inside any domains)."""
