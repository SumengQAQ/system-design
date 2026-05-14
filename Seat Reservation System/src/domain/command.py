from __future__ import annotations
from typing import Callable, Any, TypeVar, Generic, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


class Command(Generic[T]):
    def __init__(self, cls: type[T]):
        self.cls: type[T] = cls
        self.command_list: list[Callable[[], None]] = []
        self._wrap_methods(cls)

    def _wrap_methods(self, cls: type[T]) -> None:
        for name in dir(cls):
            if name.startswith("_"):
                continue
            attr = getattr(cls, name)
            if callable(attr):
                setattr(cls, name, self._push(attr, name))

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        self.command_list.clear()
        instance = self.cls(*args, **kwargs)
        instance._command = self  # type: ignore
        return instance

    def _push(self, func: Callable[P, Any], name: str) -> Callable[P, Any]:
        from functools import wraps

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            instance = args[0] if args else None
            command_obj = getattr(instance, "_command", self) if instance else self
            undo_name = name + "_undo"
            undo_method = getattr(instance, undo_name, None) if instance else None
            if undo_method is None:
                undo_method = getattr(self.cls, undo_name, None)
            command_list_snapshot = list(command_obj.command_list)
            try:
                result = func(*args, **kwargs)
            except Exception:
                for undo_func in reversed(command_list_snapshot):
                    undo_func()
                raise
            if undo_method is not None:
                bound_args = args[1:]
                command_obj.command_list.append(lambda um=undo_method, ba=bound_args, kw=kwargs: um(*ba, **kw))
            return result

        return wrapper
