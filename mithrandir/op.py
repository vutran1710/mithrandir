"""Operation on Box"""
from typing import Callable, List, NewType, TypeVar
import asyncio

T = TypeVar("T")
Boxed = NewType("Boxed", List[T])


class op:
    @staticmethod
    def map(func: Callable, *args, **kwargs):
        def _w(d: Boxed):
            result = [func(i, *args, **kwargs) for i in d]
            return result

        async def _asw(d: Boxed):
            result = [await func(i, *args, **kwargs) for i in d]
            return result

        return _w if not asyncio.iscoroutinefunction(func) else _asw

    @staticmethod
    def filter(func: Callable, *args, **kwargs):
        def _w(d: Boxed):
            result = [i for i in d if func(i, *args, **kwargs) is True]
            return result

        async def _asw(d: Boxed):
            result = [i for i in d if await func(i, *args, **kwargs) is True]
            return result

        return _w if not asyncio.iscoroutinefunction(func) else _asw

    @staticmethod
    def fold(func: Callable, *args, **kwargs):
        def _w(d: Boxed):
            if not d:
                return d

            item_list = d[1:] if kwargs.get("initial", None) is None else d
            result = kwargs.pop("initial", d[0])

            for val in item_list:
                result = func(result, val, *args, **kwargs)

            return result

        async def _asw(d: Boxed):
            if not d:
                return d

            item_list = d[1:] if kwargs.get("initial", None) is None else d
            result = kwargs.pop("initial", d[0])

            for val in item_list:
                result = await func(result, val, *args, **kwargs)

            return result

        return _w if not asyncio.iscoroutinefunction(func) else _asw
