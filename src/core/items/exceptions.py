"""
Place to define all exceptions, specific-related to these bounded-context.

You can use any shared class from core.exceptions as parent, or just inherits from DomainError directly.

For DDD it absolute doesn't matter, but can help you classifies errors types on infrastructure layer easy and correctly.

For example: we have few errors, which means "something was not found". Does not have any reasons
to mapping each error to http status_code personally - just return 404 for any "not found" error and job is done, amigo!
"""

from core.exceptions import DomainError, NotFoundError


class ItemNotFoundError(NotFoundError):
    pass


class ItemAlreadyExistsError(DomainError):  # TODO: raise in create when unique constraint needed
    pass


class TitleCannotBeEmptyError(DomainError):
    pass


class TitleTooLongError(DomainError):
    pass


class IAmTeapotError(DomainError):
    """Just example error which should be responded with specific HTTP code."""
