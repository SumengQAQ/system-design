from pydantic import BaseModel
from typing import Callable, ClassVar
import random
from ..repository import Database
from ..module import DuplicateError, NotFoundError, FailedCreateError, EncodeRequest
from ..tool import LRUCache, BloomFilter


def random_string(length: int) -> str:
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=length))


class ShortLink(BaseModel):
    """短链接转换器"""

    max_id: int = 0

    bloom_filter: ClassVar[BloomFilter] = BloomFilter(capacity=2048)

    @classmethod
    def init_bloom_filter(cls):
        """真·只能初始化一次😋"""
        for long_url in Database.get_all():
            cls.bloom_filter.add(long_url)
        del cls.init_bloom_filter

    @classmethod
    @LRUCache()
    def encode(
        cls,
        encode_request: EncodeRequest,
        random_method: Callable[[int], str] = random_string,
    ) -> str:
        """将长链接转为短链接"""

        # TODO: 这部分直接上Redis

        # NOTE:
        # 先看看布隆过滤器里面有没有这个长链接，如果一定没有，那就直接生成/自定义一个，不需要查数据库了
        # 剩下的情况就是可能有，就需要查一遍数据库，有的话就直接返回；确实没有的话，就生成一个
        # 生成的新的短链接都需要加入布隆过滤器
        if not cls.bloom_filter.contains(encode_request.long_url):
            if encode_request.custom_code:
                Database.save(encode_request.custom_code, encode_request.long_url)
            else:
                for _ in range(5):
                    short_url = random_method(6)
                    if not Database.get_long(short_url):
                        Database.save(short_url, encode_request.long_url)
                        return short_url
                raise FailedCreateError

        # note
        # 如果缓存/数据库中有这个长链接了，直接返回相应的短链接

        if Database.exist(encode_request.long_url):
            return Database.get_short(encode_request.long_url)  # pyright: ignore

        # note
        # 先看看用户有没有自定义短链接，如果有自定义短链接且数据库中已有此短链接，则抛出异常
        if encode_request.custom_code and Database.get_long(encode_request.custom_code):
            raise DuplicateError

        if encode_request.custom_code:
            print(f"指定的短链接是{encode_request.custom_code}")
            Database.save(encode_request.custom_code, encode_request.long_url)
            return encode_request.custom_code

        # note
        # 用户没有自定义短链接，则随机给一个字符串作为短链接
        for _ in range(5):
            short_url = random_method(6)
            if not Database.get_long(short_url):
                Database.save(short_url, encode_request.long_url)
                cls.bloom_filter.add(encode_request.long_url)
                return short_url
        raise FailedCreateError

    @classmethod
    @LRUCache()
    def decode(cls, short_code: str) -> str:
        """将短链接转为长链接"""

        # note
        # 先看看缓存中有没有，如果缓存中有，就直接返回
        # 否则，去数据库搜索，如果数据库中没有，则抛出异常
        # if self._cache.search(short_code):
        #     res = self._cache.get(short_code)
        #     self._cache.update_obj(short_code)
        # else:
        #     if res := get_long(short_code):
        #         self._cache.add_to_cache(short_code, res)
        #     else:
        #         raise NotFoundError

        if not (res := Database.get_long(short_code)):
            raise NotFoundError

        return res

    # def __str__(self):
    #     return (
    #         f'max_size = {self.max_size}\n'
    #         f'map_dict = {json.dumps(self.map_dict, indent=4, ensure_ascii=False)}\n'
    #         f'cache_dict = {json.dumps(self.cache_dict, indent=4, ensure_ascii=False)}'
    #     )
