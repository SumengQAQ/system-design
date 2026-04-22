"""
理论上数据库连接池的写法应该和数据库操作配套，用策略模式+依赖注入
算了不改了先凑合用吧
"""

from contextlib import contextmanager
from .config import Config

config = Config()

import pymysql
from dbutils.pooled_db import PooledDB
import redis


class Redis:
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)


class MySQL:
    _pool = None
    database_config = config["database"]

    @classmethod
    def init_pool(cls):
        if cls._pool is None:
            cls._pool = PooledDB(
                creator=pymysql,
                maxconnections=10,
                host=cls.database_config["host"],
                user=cls.database_config["user"],
                password=cls.database_config["password"],
                database=cls.database_config["database"],
            )

    @classmethod
    def get_pool(cls) -> PooledDB:
        if cls._pool is None:
            cls.init_pool()
        return cls._pool  # pyright:ignore

    @classmethod
    def reload(cls) -> None:
        cls._pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            host=cls.database_config["host"],
            user=cls.database_config["user"],
            password=cls.database_config["password"],
            database=cls.database_config["database"],
        )


class Cursor:
    @staticmethod
    @contextmanager
    def mysql_cursor():
        pool = MySQL.get_pool()
        conn = pool.connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    @contextmanager
    def redis_cursor():
        yield Redis.r
