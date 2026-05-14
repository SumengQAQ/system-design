from typing import Any


class DomainError(Exception):
    """业务异常"""


class InfrastructureError(Exception):
    """基础设施异常"""


class InvalidReservationStateError(DomainError):
    """预约状态异常"""

    def __init__(self, info: str, status_from: Any, status_to: Any):
        self.info = info
        self.status_from = status_from
        self.status_to = status_to
        super().__init__(f"{info}: {status_from} -> {status_to}")


class InvalidSeatStateError(DomainError):
    """座位状态异常"""

    def __init__(self, info: str, status_from: Any, status_to: Any):
        self.info = info
        self.status_from = status_from
        self.status_to = status_to
        super().__init__(f"{info}: {status_from} -> {status_to}")


class ReputationScoreOutOfRangeError(DomainError):
    """信用分异常"""

    def __init__(self, info: str, score_value: int, to: int):
        self.info = info
        self.score_value = score_value
        self.to = to
        super().__init__(f"{info}: score={score_value}, attempt to={to}")


class DatabaseConnectionError(InfrastructureError):
    """数据库连接异常"""

    def __init__(self, info: str):
        self.info = info
        super().__init__(f"Database connection error: {info}")


class PersistenceError(InfrastructureError):
    def __init__(self, info: str):
        self.info = info
        super().__init__(f"Persistence error: {info}")


class DataIntegrityError(InfrastructureError):
    def __init__(self, info: str):
        self.info = info
        super().__init__(f"Data integrity error: {info}")


class ResourceNotFoundError(DomainError):
    """资源未找到"""

    def __init__(self, info: str):
        self.info = info
        super().__init__(f"Resource not found: {info}")


class MissingConfigurationError(InfrastructureError):
    """配置项缺失"""

    def __init__(self, info: str):
        self.info = info
        super().__init__(f"Missing configuration: {info}")


class InvalidConfigurationError(InfrastructureError):
    def __init__(self, info: str):
        self.info = info
        super().__init__(f"Invalid configuration: {info}")


class ExternalServiceUnavailableError(InfrastructureError):
    """未找到服务"""

    def __init__(self, info: str):
        self.info = info
        super().__init__(f"External service unavailable: {info}")


class ExternalServiceError(InfrastructureError):
    """服务不可用"""

    def __init__(self, info: str):
        self.info = info
        super().__init__(f"External service error: {info}")
