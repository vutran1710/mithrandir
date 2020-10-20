from typing import Union, Callable
import asyncio
from functools import reduce
import operator
from enum import Enum
from copy import copy
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

        self.__cb = [] if not cb else cb

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
        result = Monad([])
        data = None
        cb = [*self.__cb]

        if asyncio.iscoroutinefunction(func) or self.__cb:
            cb = [*self.__cb, (func, kwargs)]
            data = self.__d
        else:
            data = func(self.__d)
            model = kwargs.get("model")
            self.__confirm(data, model)
            
        result = Monad(data, cb=cb)
        return result

    def map(self, func: Callable, model=None):
        is_coro = asyncio.iscoroutinefunction(func)
        def sf(x):
            return [func(d) for d in x]
        async def asf(x):
            return [await func(d) for d in x]
        
        return self.bind(asf if is_coro else sf, model=model)

    def filter(self, func: Callable, model=None):
        is_coro = asyncio.iscoroutinefunction(func)
        def sf(x):
            return [d for d in x if func(d)]
        async def asf(x):
            return [d for d in x if await func(d)]
        
        return self.bind(asf if is_coro else sf, model=model)
    
    def reduce(self, func, default=None, model=None):
        """not supporting coroutine"""
        fn = lambda x: reduce(func, x, default)
        return self.bind(fn, model=model)

    async def resolve(self):
        if not self.__cb:
            return self

        func, kwargs = self.__cb[0]
        cb = self.__cb[1:]

        data = self.__d
        if asyncio.iscoroutinefunction(func):
            data = await func(data)
        else:
            data = func(data)

        self.__confirm(data, kwargs.get("model"))
        result = Monad(data, cb=cb)
        result = await result.resolve()
        return result
        
