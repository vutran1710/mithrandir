from typing import Union, Callable
import asyncio
from functools import reduce
import operator
from enum import Enum
from queue import SimpleQueue
from pydantic import BaseModel, ValidationError


class MonadSignatures(Enum):
    UNWRAP = "unwrap"
    MAP = "map"
    FILTER = "filter"
    REDUCE = "reduce"


class Monad:
    def __init__(self, data=None, cb=None):
        if data is None:
            self.__d = []
        elif isinstance(data, list):
            self.__d = data
        else:
            self.__d = [data]

        self.__cb = SimpleQueue() if not cb else cb

    def awaiting(self):
        if not self.__d:
            return False
        return asyncio.iscoroutine(self.__d[0])

    def __confirm(self, data, model):
        if model and data:
            for nth in data:
                if not isinstance(nth, model):
                    raise TypeError("data_type=", type(nth), "model_type=", model)

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

    def bind(self, func: Callable, *args, **kwargs):
        if self.awaiting():
            self.__cb.put((func, kwargs))
            return Monad(self.__d, cb=self.__cb)

        data = func(self.__d)
        model = kwargs.get("model")

        if model:
            self.__confirm(data, model)

        return Monad(data, cb=self.__cb)

    def map(self, func: Callable, model=None):
        gf = lambda x: list(map(func, x))
        return self.bind(gf, model=model)

    def filter(self, func: Callable, model=None):
        gf = lambda x: list(filter(func, x))
        return self.bind(gf, model=model)
    
    def reduce(self, func, default=None, model=None):
        gf = lambda x: reduce(func, x, default)
        return self.bind(gf, model=model)

    async def resolve(self):
        if self.__cb.empty():
            return self

        func, kwargs = self.__cb.get()

        data = self.__d
        if self.awaiting():
            data = [await c for c in self.__d]
            
        data = func(data)
        result = Monad(data, cb=self.__cb)
        result = await result.resolve()
        return result
