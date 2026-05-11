from typing import Any
from .model import ReputationScore


class DomainError: ...


class InfrastructureError: ...


class InvalidReservationStateError(DomainError):
    def __init__(self, info: str, status_from: Any, status_to: Any): ...


class InvalidSeatStateError(DomainError):
    def __init__(self, info: str, status_from: Any, status_to: Any): ...


class ReputationScoreOutOfRangeError(DomainError):
    def __init__(self, info: str, reputation_score: ReputationScore, to: int): ...


class DatabaseConnectionError(InfrastructureError):
    def __init__(self, info: str): ...


class PersistenceError(InfrastructureError):
    def __init__(self, info: str): ...


class DataIntegrityError(InfrastructureError):
    def __init__(self, info: str): ...


class ResourceNotFoundError(InfrastructureError):
    def __init__(self, info: str): ...


class MissingConfigurationError(InfrastructureError):
    def __init__(self, info: str): ...


class InvalidConfigurationError(InfrastructureError):
    def __init__(self, info: str): ...


class ExternalServiceUnavailableError(InfrastructureError):
    def __init__(self, info: str): ...


class ExternalServiceError(InfrastructureError):
    def __init__(self, info: str): ...
