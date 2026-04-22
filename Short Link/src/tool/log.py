from loguru import logger
from typing import Callable
from functools import wraps
from ..config import Config

"""
别搞了，用FastAPI自带的中间件吧
"""
config = Config()


def log(func: Callable):
    _name = 'message'
    _config = config['log']
    _logger = logger.bind(category=_name)

    logger.add(
        f'{_config['path']}{_name}.log',
        filter=lambda record: record["extra"].get("category") == _name,
        format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}',
        level=_config['level'],
        rotation=_config['rotation'],
        compression="zip"
    )
    _logger = logger.bind(category=_name)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            _logger.info(f'{func.__name__} args={args} kwargs={kwargs}')
            return result
        except Exception as e:
            _logger.error(str(e))
            raise e

    return wrapper


class Logger:
    __instance: dict[str, 'Logger'] = {}
    __initialization: set[str] = set()
    __config = config['log']

    __slots__ = ('logger', 'name', 'level', 'rotation', 'file_handler')

    def __new__(cls, name: str):
        if name not in Logger.__instance:
            if not isinstance(name, str): raise TypeError("日志名必须是字符串")
            Logger.__instance[name] = super().__new__(cls)
        return Logger.__instance[name]

    def __init__(self, name: str):
        if name in Logger.__initialization: return

        self.file_handler = None
        self.logger = logger.bind(category=name)
        self.name = name
        self.level = self.__config['level']
        self.rotation = self.__config['rotation']

        Logger.__initialization.add(name)

    def enable_file_log(self):
        """启用文件日志"""
        if self.file_handler is None:
            self.file_handler = logger.add(
                f'{Logger.__config['path']}{self.name}.log',
                filter=lambda record: record["extra"].get("category") == self.name,
                format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}',
                level=self.level,
                rotation=self.rotation,
                compression="zip"
            )
            self.logger = logger.bind(category=self.name)

    def disable_file_log(self):
        """禁用文件日志"""
        if self.file_handler is not None:
            logger.remove(self.file_handler)
            self.file_handler = None

    def debug(self, text: str):
        self.logger.debug(text)

    def info(self, text: str):
        self.logger.info(text)

    def error(self, text: str):
        self.logger.error(text)

    def warning(self, text: str):
        self.logger.warning(text)

    def critical(self, text: str):
        self.logger.critical(text)
