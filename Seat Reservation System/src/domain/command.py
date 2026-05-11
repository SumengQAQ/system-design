from __future__ import annotations
from typing import Callable


class Command:
    def __init__(self, cls: type):
        self.cls: type = cls
        self.command_list: list[Callable[[None], Callable]] = []

    def __call__(self, *args, **kwargs) -> Command: ...
    def _push(self, func: Callable) -> None: ...
