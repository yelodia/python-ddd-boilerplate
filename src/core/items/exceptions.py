from common.exceptions import DomainError


class ItemNotFoundError(DomainError):
    pass


class ItemAlreadyExistsError(DomainError):  # TODO: raise in create when unique constraint needed
    pass


class CannotEmptyTitleError(DomainError):
    pass


class TooLongTitleError(DomainError):
    pass
