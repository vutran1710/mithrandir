"""Box class"""
from typing import TypeVar, List, Union, Callable
import asyncio


T = TypeVar("T")


def auto_box(data: Union[T, List[T]]) -> List[T]:
    """convert any data to List Data"""
    if isinstance(data, list):
        return [f for f in data if f is not None]
    if data is None:
        return []
    return [data]


class Box:
    """Box - a friendly term that
    makes sense to everyone instead of `Monad`
    It's like a simplified monad
    """

    def __init__(
        self,
        data: T = None,
        pipe: List[Callable] = None,
        effect: bool = False,
        validator: Callable = None,
    ):
        self.__wrapped = auto_box(data)
        self.__pipe = pipe or []
        self.__effect = effect
        if validator:
            self.__validate_data(validator)

    def __repr__(self):
        return f"Box<data={self.__wrapped}, pipe={self.__pipe}, effect={self.__effect}>"

    def __validate_data(self, validator: Callable):
        for item in self.__wrapped:
            if not isinstance(item, validator):
                msg = f"Invalid data-type: item={item} not instance of {validator}"
                raise ValueError(msg)

    def unwrap(self) -> List[T]:
        return self.__wrapped

    def pipe(self, *func):
        func_has_effect = next(
            (bool(f) for f in func if asyncio.iscoroutinefunction(f)), False
        )
        effect = self.__effect or func_has_effect
        return Box(data=self.__wrapped, pipe=[*self.__pipe, *func], effect=effect)

    @property
    def has_effect(self) -> bool:
        return self.__effect

    @has_effect.setter
    def has_effect(self, _):
        raise ValueError("this property is read-only")

    @property
    def resolve(self) -> Callable:
        if self.__effect:
            return self.__async_resolve
        return self.__sync_resolve

    @resolve.setter
    def resolve(self, _):
        raise ValueError("this property is read-only")

    def __sync_resolve(self):
        data = self.__wrapped

        for func in self.__pipe:
            data = func(data)

        return Box(data=data)

    async def __async_resolve(self):
        data = self.__wrapped

        for func in self.__pipe:
            if asyncio.iscoroutinefunction(func):
                data = await func(data)
            else:
                data = func(data)

        return Box(data=data)
