from typing import Union, Callable
import asyncio
from functools import reduce
import operator
from enum import Enum
from queue import Queue


class MonadSignatures(Enum):
    UNWRAP = "unwrap"
    MAP = "map"


class Monad:
    def __init__(self, data=None):
        if data is None:
            self.__d = []
        elif isinstance(data, list):
            self.__d = data
        else:
            self.__d = [data]

    def unwrap(self):
        return self.__d

    def __str__(self):
        return f"{self.__d}"

    def add(self, obj):
        if isinstance(obj, list):
            return Monad(self.__d + obj)

        if isinstance(obj, Monad):
            data = obj.unwrap()
            return Monad(self.__d + data)

        return Monad(self.__d + [obj])

    def bind(self, func: Callable):
        data = func(self.__d)
        return Monad(data)

    def map(self, func: Callable):
        data = list(map(func, self.__d))
        return Monad(data)

    def filter(self, func: Callable):
        data = list(filter(func, self.__d))
        return Monad(data)

    def reduce(self, func, default):
        data = reduce(func, self.__d, default)
        return Monad(data)
