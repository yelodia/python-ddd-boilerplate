class DomainError(Exception):
    """
    Base class for ALL exceptions and ALL domain.
    For all which can be responded to user as HTTP_400_BadRequest, for example.
    """


class NotFoundError(DomainError):
    """
    Base class for all something-not-found-like means errors.
    For all which can be responded to user as HTTP_404_NotFound, for example.
    """


class RateLimitError(DomainError):
    """Example of CROSS-DOMAIN error, which can used everywhere (inside any domains)."""

# Non-domain-specific errors, which can be used in any domain,
# but not related to business logic, so they are not
# DomainErrors.

class UnknownStorageError(Exception): pass
class UsecaseUnknownParamError(Exception): pass
