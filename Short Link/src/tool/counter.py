from functools import wraps
import json
from collections import defaultdict
from typing import Callable


# warning
# 如果用 id() 来做键的话，会导致内存泄漏
# 不过deepseek说 str() 里面也含有 id 的信息？
# 保险起见，还是不要用 Counter 了

class Counter:
    """方法调用次数计数器"""

    def __init__(self, func: Callable):
        self.func = func
        self._counters = {}

    def __get__(self, instance, owner):
        """当调用方法时，返回一个被装饰后的方法，可以记录不同参数的调用次数"""
        if instance is None: return self

        if str(instance) not in self._counters: self._counters[str(instance)] = defaultdict(int)

        @wraps(self.func)
        def wrapper(*args, **kwargs):
            key = f'{args} | {kwargs}'
            self._counters[str(instance)][key] += 1
            return self.func(instance, *args, **kwargs)

        wrapper.show = lambda: print(json.dumps(self._counters[str(instance)], indent=4))
        wrapper.clear = lambda: self._counters[str(instance)].clear()

        return wrapper

    def __call__(self, *args, **kwargs):
        """通过类直接调用时报错"""
        raise TypeError("Counter 装饰的方法必须通过实例调用")
