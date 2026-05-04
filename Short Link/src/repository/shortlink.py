from typing import Generator

from ..database import Cursor
from pydantic import HttpUrl
from ..module import DatabaseModule
# TODO: 缓存的模型也要加上

mysql_cursor, redis_cursor = Cursor.mysql_cursor, Cursor.redis_cursor


class MySQL(DatabaseModule):
    @staticmethod
    def save(short_code: str, long_url: HttpUrl) -> int:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                insert into shortlink (short_code, long_url)
                values (%s, %s);
                """,
                (short_code, long_url),
            )
            return cursor.lastrowid

    @staticmethod
    def get_long(short_code: str) -> str | None:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                select long_url
                from shortlink
                where short_code = %s;
                """,
                (short_code,),
            )
            if not (res := cursor.fetchone()):
                return None

            MySQL.update(short_code)
            return res[0]

    # NOTE: 这里为啥会报错 update 方法以不兼容的方式重写了 DatabaseModule ？？？
    @staticmethod
    def update(where_value: str) -> None:  # pyright: ignore
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                update shortlink
                set access_count = access_count + 1
                where short_code = %s;
                """,
                (where_value,),
            )

    @staticmethod
    def get_short(long_url: HttpUrl) -> str | None:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                select short_code
                from shortlink
                where long_url = %s;
                """,
                (long_url,),
            )
            result = cursor.fetchone()
            return result[0] if result else None

    @staticmethod
    def get_all() -> Generator[HttpUrl, None, None]:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                select long_url
                from shortlink;
                """
            )
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                yield row[0]

    @staticmethod
    def exists(key: str, value: str) -> bool:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                select 1 from shortlink where %s = %s;
                """,
                (key, value),
            )
            return bool(cursor.fetchone()[0])


class Redis:
    @staticmethod
    def get_long(key: str) -> str | None:
        with redis_cursor() as cursor:
            result = cursor.get(key)
            if result is None:
                return None
            return result if isinstance(result, str) else result.decode("utf-8")

    @staticmethod
    def get_short(key: str) -> str | None:
        with redis_cursor() as cursor:
            result = cursor.get(key)
            if result is None:
                return None
            return result if isinstance(result, str) else result.decode("utf-8")

    @staticmethod
    def set(key: str, value: str, ex=None) -> bool:
        with redis_cursor() as cursor:
            return bool(cursor.set(str(key), value, ex=ex))

    @staticmethod
    def delete(key: str) -> int:
        with redis_cursor() as cursor:
            return cursor.delete(key)

    @staticmethod
    def exists(key: str) -> bool:
        with redis_cursor() as cursor:
            return cursor.exists(key) > 0

    @staticmethod
    def expire(key: str, seconds: int) -> bool:
        with redis_cursor() as cursor:
            return cursor.expire(key, seconds)

    @staticmethod
    def incr(key: str) -> int:
        with redis_cursor() as cursor:
            return cursor.incr(key)


Database = MySQL
Cache = Redis


class ShortLinkRepository:
    @staticmethod
    def get_long(short_code: str) -> str | None:
        cached = Cache.get_long(f"short_code:{short_code}")
        if cached:
            return cached
        return Database.get_long(short_code)

    @staticmethod
    def get_short(long_url: HttpUrl) -> str | None:
        cached = Cache.get_short(f"long_url:{long_url}")
        if cached:
            return cached
        return Database.get_short(long_url)

    @staticmethod
    def save(short_code: str, long_url: HttpUrl) -> int:
        Cache.set(f"short_code:{short_code}", str(long_url))
        Cache.set(f"long_url:{long_url}", short_code)
        Cache.set(f"access_count:{short_code}", "0")
        return Database.save(short_code, long_url)

    @staticmethod
    def exists_long(long_url: HttpUrl) -> bool:
        cached = Cache.exists(f"long_url:{long_url}")
        if cached:
            return True
        return Database.exists("long_url", str(long_url))

    @staticmethod
    def exists_short(short_code: str) -> bool:
        cached = Cache.exists(f"short_code:{short_code}")
        if cached:
            return True
        return Database.exists("short_code", short_code)

    # TODO: 这边需要先更新缓存里面的 access_count ，然后每隔5分钟同步到数据库😭😭😭
    @staticmethod
    def increment(short_code: str) -> None:
        Cache.incr(f"short_code:{short_code}")
