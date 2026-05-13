from collections import defaultdict
from typing import Callable


class EventBus:
    __events: dict[type, list[Callable]] = defaultdict(list)

    @classmethod
    def register(cls, event: type, callback: Callable):
        cls.__events[event].append(callback)

    @classmethod
    def emit(cls, event: object):
        for callback in cls.__events[type(event)]:
            callback(event)


class RightClickEvent:
    """
    此处仅作演示，所以不携带任何属性
    实际上点击右键也不需要啥属性……
    """

    ...
