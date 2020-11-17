"""Operation on Box"""
from typing import Callable, List, NewType, TypeVar, Union, Any
import asyncio
from mithrandir.box import auto_box

T = TypeVar("T")
Boxed = NewType("Boxed", List[T])


class op:
    @staticmethod
    def if_else(
        condition: Union[Callable, Any],
        tru_func: Callable,
        fals_func: Callable,
    ):
        """simple branching"""
        is_async = asyncio.iscoroutinefunction(tru_func) or asyncio.iscoroutinefunction(
            fals_func
        )

        def sync_ifelse(boxed: Boxed):
            check = condition(boxed) if callable(condition) else bool(condition)
            return tru_func(boxed) if check else fals_func(boxed)

        async def async_ifelse(boxed: Boxed):
            check = condition(boxed) if callable(condition) else bool(condition)
            result = await (tru_func(boxed) if check else fals_func(boxed))
            return result

        return sync_ifelse if not is_async else async_ifelse

    @staticmethod
    def each(func: Callable, *args, **kwargs):
        """for each loop, return the original result"""

        def sync_each(boxed: Boxed):
            for nth in boxed:
                func(nth, *args, **kwargs)
            return boxed

        async def async_each(boxed: Boxed):
            for nth in boxed:
                await func(nth, *args, **kwargs)
            return boxed

        return sync_each if not asyncio.iscoroutinefunction(func) else async_each

    @staticmethod
    def map(func: Callable, *args, **kwargs):
        """not lazy, func takes single item in Box as first param"""

        def sync_map(boxed: Boxed):
            result = [func(i, *args, **kwargs) for i in boxed]
            return result

        async def async_map(boxed: Boxed):
            result = [await func(i, *args, **kwargs) for i in boxed]
            return result

        return sync_map if not asyncio.iscoroutinefunction(func) else async_map

    @staticmethod
    def filter(func: Callable, *args, **kwargs):
        """not lazy, func takes single item in Box as first param, must return a bool"""

        def syncfilter(boxed: Boxed):
            result = [i for i in boxed if func(i, *args, **kwargs) is True]
            return result

        async def asyncfilter(boxed: Boxed):
            result = [i for i in boxed if await func(i, *args, **kwargs) is True]
            return result

        return syncfilter if not asyncio.iscoroutinefunction(func) else asyncfilter

    @staticmethod
    def fold(func: Callable, *args, **kwargs):
        """just like reduce"""

        def sync_fold(boxed: Boxed):
            if not boxed:
                return boxed

            item_list = boxed[1:] if kwargs.get("initial") is None else boxed
            result = kwargs.pop("initial", boxed[0])

            for val in item_list:
                result = func(result, val, *args, **kwargs)

            return auto_box(result)

        async def async_fold(boxed: Boxed):
            if not boxed:
                return boxed

            item_list = boxed[1:] if kwargs.get("initial") is None else boxed
            result = kwargs.pop("initial", boxed[0])

            for val in item_list:
                result = await func(result, val, *args, **kwargs)

            return auto_box(result)

        return sync_fold if not asyncio.iscoroutinefunction(func) else async_fold


# ====================================================================
# INDEPENDENT FUNCTIONS
# ====================================================================


def compose(*funcs):
    """compose functions into one"""
    is_async = next((True for f in funcs if asyncio.iscoroutinefunction(f)), False)

    def sync_hoc(*args, **kwargs):
        result = None
        for idx, func in enumerate(funcs):
            result = func(*args, **kwargs) if idx == 0 else func(result)
        return result

    async def async_hoc(*args, **kwargs):
        result = None
        for idx, func in enumerate(funcs):
            result = func(*args, **kwargs) if idx == 0 else func(result)
            if asyncio.iscoroutine(result):
                result = await result

        return result

    return sync_hoc if not is_async else async_hoc
