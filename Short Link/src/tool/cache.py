from collections import OrderedDict
from typing import Any, Callable
from functools import wraps


# note
# 为啥要手写缓存？用现成的!
# 不行！实例unhashable😭


class LRUCache:
    """LRUCache 装饰器"""

    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache = OrderedDict()

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(instance, *args, **kwargs) -> Any:
            key = repr(args) + repr(kwargs)

            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]

            result = func(instance, *args, **kwargs)
            self.cache[key] = result
            if len(self.cache) > self.maxsize: self.cache.popitem(last=False)

            return result

        return wrapper

# class LRUCache:
#
#     def __init__(self, max_size: int):
#         if max_size <= 0: raise ValueError('容量必须为自然数')
#         self._max_size = max_size
#         self._cache: OrderedDict = OrderedDict()
#
#     def add_to_cache(self, key: Any, value: Any) -> None:
#         if self._max_size == len(self._cache):
#             self._cache.popitem(last=False)
#         self._cache[key] = value
#
#     def update_obj(self, key: Any) -> None:
#         if key not in self._cache: raise KeyError('缓存中没有此对象')
#         self._cache.move_to_end(key)
#
#     def search(self, key: Any) -> bool:
#         return key in self._cache
#
#     def get(self, key: Any) -> Any:
#         if key not in self._cache: raise KeyError('缓存中没有此对象')
#         return self._cache[key]
