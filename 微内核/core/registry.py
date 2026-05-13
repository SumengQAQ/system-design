from __future__ import annotations
from typing import Type
from abc import ABC, abstractmethod


class PluginRegistry:
    _plugins: dict[str, Type[BasePlugin]] = {}
    _order: list[str] = []

    @classmethod
    def register(cls, plugin) -> None:
        if not plugin.name:
            raise ValueError(f"插件 {plugin.__name__} 需要 name 属性")
        cls._plugins[plugin.name] = plugin

    @classmethod
    def get(cls, plugin_name: str) -> Type[BasePlugin]:
        if plugin_name not in cls._plugins:
            raise ValueError(f"未找到 {plugin_name} 插件")
        return cls._plugins[plugin_name]

    @classmethod
    def get_all(cls) -> list[str]:
        return sorted(
            cls._plugins.keys(),
            key=lambda name: cls._plugins[name].priority,
            reverse=True,
        )


class BasePlugin(ABC):
    name: str
    priority: int = 0
    scope: str = "singleton"

    def __init_subclass__(cls, priority=0, scope="singleton", **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.priority = priority
        cls.scope = scope
        PluginRegistry.register(cls)

    @classmethod
    @abstractmethod
    def initialize(cls): ...
