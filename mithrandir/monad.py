from typing import Union
import asyncio
from functools import reduce
import operator
from enum import Enum
from queue import Queue


class MSigs(Enum):
    FUTURE_RESOLVE = "future_resolve"
    FLUSH = "flush"
    CONSOLIDATE = "consolidate"
    FLATTEN = "flatten"


class Monad:
    def __init__(self, data, callbacks=None):
        if isinstance(data, list):
            self.__d = data
        else:
            self.__d = [data]

        self.callbacks = Queue() if callbacks is None else callbacks

    def __or__(self, sig: Union[callable, MSigs]):
        """Operator overloading"""
        if isinstance(sig, MSigs):
            attr = sig.value
            return getattr(self, attr)()
        return self.map(sig)

    def __add__(self, obj):
        return self.add(obj)

    def __xor__(self, func):
        return self.filter(func)

    def __register__(self, sig: str, *args):
        self.callbacks.put((sig, *args))

    def map(self, func: callable):
        self.__register__("map", func)
        return Monad(self.__d, callbacks=self.callbacks)

    def filter(self, func: callable):
        self.__register__("filter", func)
        return Monad(self.__d, callbacks=self.callbacks)

    # def reduce(self, func: callable, default=None):
    #     callbacks = self.__register__("reduce", func, default)
    #     data = reduce(func, self.__d) if not callbacks else self.__d
    #     return Monad(data, callbacks=callbacks)
    def _map(self, func):
        return Monad(list(map(func, self.__d)), callbacks=self.callbacks)

    def _filter(self, func):
        return Monad(list(filter(func, self.__d)), callbacks=self.callbacks)

    def add(self, obj):
        if isinstance(obj, list):
            return Monad(self.__d + obj, callbacks=self.callbacks)
        if isinstance(obj, Monad):
            data = obj.flush()
            return Monad(self.__d + data, callbacks=self.callbacks)
        return Monad(self.__d + [obj], callbacks=self.callbacks)

    async def future_resolve(self):
        data = (
            [await cor for cor in self.__d]
            if asyncio.iscoroutine(self.head())
            else self.__d
        )
        result = Monad(data, callbacks=self.callbacks)

        while not result.callbacks.empty():
            attr, *args = result.callbacks.get()
            result = getattr(result, f"_{attr}")(*args)
            if asyncio.iscoroutinefunction(args[0]):
                result = await result.future_resolve()

        return result

    def head(self):
        return (self.__d + [None])[0]

    def flush(self):
        return self.__d

    def consolidate(self):
        """Upon cosolidation, all callbacks will be discarded"""
        return Monad([self.__d], callbacks=self.callbacks)

    def flatten(self):
        """flatten nesting data"""
        return Monad(self.__d[0], callbacks=self.callbacks)
