from typing import Generator

from ..database import Cursor
from pydantic import HttpUrl
from ..module import DatabaseModule

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


Database = MySQL
