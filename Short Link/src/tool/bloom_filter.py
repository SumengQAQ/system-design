import mmh3
from bitarray import bitarray
import math
from pydantic import HttpUrl


class BloomFilter:
    """
    布隆过滤器，用于快速判断字符串是否已存在，可能误判

    Args:
        capacity(int): 预计存储的元素数量
        error_rate(float): 期望的误判率
    """

    def __init__(self, capacity: int, error_rate: float = 0.001):

        self.capacity = capacity
        self.error_rate = error_rate

        # 计算位数组大小
        self.size = self._get_size(capacity, error_rate)
        # 计算哈希函数数量
        self.hash_count = self._get_hash_count(self.size, capacity)

        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

    @staticmethod
    def _get_size(n: int, p: float) -> int:
        """计算位数组大小"""
        return int(-(n * math.log(p)) / (math.log(2) ** 2))

    @staticmethod
    def _get_hash_count(m: int, n: int) -> int:
        """计算哈希函数数量"""
        return int((m / n) * math.log(2))

    def _hashes(self, item: HttpUrl):
        """生成 k 个哈希值"""
        for i in range(self.hash_count):
            # 用 mmh3 生成不同的哈希值
            yield mmh3.hash(str(item), i) % self.size

    def add(self, item: HttpUrl):
        """添加元素"""
        for hash_val in self._hashes(item):
            self.bit_array[hash_val] = 1

    def contains(self, item: HttpUrl) -> bool:
        """检查元素是否存在（可能有误判）"""
        for hash_val in self._hashes(item):
            if not self.bit_array[hash_val]:
                return False
        return True
