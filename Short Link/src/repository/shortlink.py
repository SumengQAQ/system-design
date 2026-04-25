from typing import Generator

from ..database import Cursor
from pydantic import HttpUrl
from ..module import DatabaseModule

mysql_cursor, redis_cursor = Cursor.mysql_cursor, Cursor.redis_cursor

# TODO: 将 MySQL 类中的 exist 更名为 exists


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

    @staticmethod
    def update(short_code: str) -> None:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                update shortlink
                set access_count = access_count + 1
                where short_code = %s;
                """,
                (short_code,),
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
    def exist(long_url: HttpUrl) -> bool:
        with mysql_cursor() as cursor:
            cursor.execute(
                """
                select 1 from shortlink where long_url = %s;
                """,
                (long_url,),
            )
            return bool(cursor.fetchone()[0])


class Redis:
    @staticmethod
    def get(long_url: HttpUrl) -> str | None:
        with redis_cursor() as cursor:
            result = cursor.get(str(long_url))
            if result is None:
                return None
            return result if isinstance(result, str) else result.decode("utf-8")

    @staticmethod
    def set(long_url: HttpUrl, short_code: str, ex=None) -> bool:
        with redis_cursor() as cursor:
            return bool(cursor.set(str(long_url), short_code, ex=ex))

    @staticmethod
    def delete(long_url: HttpUrl) -> int:
        with redis_cursor() as cursor:
            return cursor.delete(str(long_url))

    @staticmethod
    def exists(long_url: HttpUrl) -> bool:
        with redis_cursor() as cursor:
            return cursor.exists(str(long_url)) > 0

    @staticmethod
    def expire(long_url: HttpUrl, seconds: int) -> bool:
        with redis_cursor() as cursor:
            return cursor.expire(str(long_url), seconds)

    @staticmethod
    def incr(long_url: HttpUrl) -> int:
        with redis_cursor() as cursor:
            return cursor.incr(str(long_url))


Database = MySQL
Cache = Redis
