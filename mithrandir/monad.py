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

    # def __add__(self, obj):
    #     return self.add(obj)

    def add(self, obj):
        if isinstance(obj, list):
            return Monad(self.__d + obj)

        if isinstance(obj, Monad):
            data = obj.unwrap()
            return Monad(self.__d + data)

        return Monad(self.__d + [obj])

    # def __or__(self, arg: Union[Callable, MonadSignatures]):
    #     """Operator overloading"""
    #     if isinstance(arg, MonadSignatures):
    #         return getattr(self, arg.value)
    #     return self.bind(arg)

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

    # def __register__(self, sig: str, *args):
    #     self.callbacks.put((sig, *args))

    # # def reduce(self, func: Callable, default=None):
    # #     callbacks = self.__register__("reduce", func, default)
    # #     data = reduce(func, self.__d) if not callbacks else self.__d
    # #     return Monad(data, callbacks=callbacks)

    # async def future_resolve(self):
    #     data = (
    #         [await cor for cor in self.__d]
    #         if asyncio.iscoroutine(self.head())
    #         else self.__d
    #     )
    #     result = Monad(data, callbacks=self.callbacks)

    #     while not result.callbacks.empty():
    #         attr, *args = result.callbacks.get()
    #         result = getattr(result, f"_{attr}")(*args)
    #         if asyncio.iscoroutinefunction(args[0]):
    #             result = await result.future_resolve()

    #     return result

    # def head(self):
    #     return self.__d[0]

    # def consolidate(self):
    #     """Upon cosolidation, all callbacks will be discarded"""
    #     return Monad([self.__d], callbacks=self.callbacks)

    # def flatten(self):
    #     """flatten nesting data"""
    #     return Monad(self.__d[0], callbacks=self.callbacks)
