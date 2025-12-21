class DomainError(Exception):
    """Base class for domain errors."""


class UserAlreadyExists(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class ActivationCodeExpired(DomainError):
    pass


class ActivationCodeInvalid(DomainError):
    pass


class UserAlreadyActive(DomainError):
    pass
