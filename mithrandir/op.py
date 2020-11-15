"""Operation on Box"""
from typing import Callable
import asyncio


class op:
    @staticmethod
    def map(func: Callable, *args, **kwargs):
        def _w(d):
            result = [func(i, *args, **kwargs) for i in d]
            return result

        async def _asw(d):
            result = [await func(i, *args, **kwargs) for i in d]
            return result

        return _w if not asyncio.iscoroutinefunction(func) else _asw

    @staticmethod
    def filter(func: Callable, *args, **kwargs):
        def _w(d):
            result = [i for i in d if func(i, *args, **kwargs) is True]
            return result

        async def _asw(d):
            result = [i for i in d if await func(i, *args, **kwargs) is True]
            return result

        return _w if not asyncio.iscoroutinefunction(func) else _asw

    @staticmethod
    def fold(func: Callable, *args, **kwargs):
        def _w(d):
            result = [i for i in d if func(i, *args, **kwargs) is True]
            return result

        async def _asw(d):
            result = [i for i in d if await func(i, *args, **kwargs) is True]
            return result

        return _w if not asyncio.iscoroutinefunction(func) else _asw
