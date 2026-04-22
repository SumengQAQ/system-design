import tomllib
from typing import Any, Type
import json
import os
from dotenv import dotenv_values
from abc import ABC, abstractmethod


class ConfigType(ABC):
    @staticmethod
    @abstractmethod
    def read() -> dict[str, Any]: ...


class Toml(ConfigType):
    @staticmethod
    def read() -> dict[str, Any]:
        with open(Config.PATH, "rb") as f:
            return tomllib.load(f)


class Env(ConfigType):
    """全部的值都为字符串"""

    @staticmethod
    def read() -> dict[str, Any]:
        return dotenv_values(".env")


class Config:
    """支持多种配置和热重载的配置管理器"""

    PATH = os.path.join(os.path.dirname(__file__), "../config.toml")

    __instance = None
    __initialization = False

    __slots__ = ("__config_type", "config")

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config_type: Type[ConfigType] = Toml):
        if Config.__initialization:
            return
        Config.__initialization = True

        if not os.path.exists(Config.PATH):
            raise FileNotFoundError(f"配置文件 {Config.PATH} 不存在")
        self.__config_type = config_type
        self.config = self.__config_type.read()

    def __getitem__(self, key: str) -> Any:
        if key not in self.config:
            raise KeyError(f"{key} 不存在")
        return self.config[key]

    def __str__(self):
        return json.dumps(self.config, indent=4, ensure_ascii=False)

    def reload(self):
        self.config = self.__config_type.read()
