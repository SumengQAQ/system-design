from abc import ABC, abstractmethod
from pydantic import HttpUrl


class DatabaseModule(ABC):
    @staticmethod
    @abstractmethod
    def save(short_code: str, long_url: HttpUrl) -> int:
        """将短链接及对应的长链接保存至数据库"""
        ...

    @staticmethod
    @abstractmethod
    def get_long(short_code: str) -> str | None:
        """短链接获取对应的长连接"""
        ...

    @staticmethod
    @abstractmethod
    def get_short(long_url: HttpUrl) -> str | None:
        """长链接获取对应的短链接"""
        ...

    @staticmethod
    @abstractmethod
    def update(where_value: str) -> None:
        """更新短链接的使用计数"""
        ...

    @staticmethod
    @abstractmethod
    def exist(long_url: HttpUrl) -> bool:
        """检查长链接对应的短链接是否存在"""
        ...
