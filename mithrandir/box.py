"""Box class"""
from enum import Enum
from typing import TypeVar, List, Union, Callable
from asyncio import iscoroutine


T = TypeVar("T")


def auto_box(data: Union[T, List[T]]) -> List[T]:
    """convert any data to List Data"""
    if isinstance(data, list):
        return [f for f in data if f is not None]
    if data is None:
        return []
    return [data]


class BoxSignal(Enum):
    """Box available signatures"""

    MAP = "map"
    FILTER = "filter"
    TAP = "tap"
    APPEND = "append"
    VALIDATE = "validate"


class __BasicBox__:
    """Box - a friendly term that
    makes sense to everyone instead of `Monad`
    It's like a simplified monad
    """

    __wrapped: List[T]

    def __init__(self, data: T = None):
        self.__wrapped = auto_box(data)

    def unwrap(self) -> List[T]:
        return self.__wrapped


class Box(__BasicBox__):
    """Box with transformer apis"""

    async def effect(self, signal: BoxSignal, *args, **kwargs):
        """handle side-effects"""
        effected_box = getattr(self, signal.value)(*args, **kwargs)
        try:
            effects = effected_box.unwrap()

            if effects and iscoroutine(effects[0]):
                return Box(data=[await f for f in effects])

            return effected_box
        except Exception as err:
            print("Effect failure > ", err)
            return Box()

    def map(self, func: Callable):
        data = list(map(func, self.unwrap()))
        return Box(data=data)

    def filter(self, pred: Callable):
        data = list(filter(pred, self.unwrap()))
        return Box(data=data)

    def tap(self, func: Callable):
        for item in self.unwrap():
            func(item)

        return self

    def peek(self, func):
        func([x for x in self.unwrap()])
        return self

    def apppend(self, *boxes: List[__BasicBox__], model=None):
        if not model:
            raise ValueError("A validation model is required!")

        data = [*self.unwrap()]
        for box in boxes:
            data += box.unwrap()

        new_box = Box(data=data)
        return new_box.validate(model=model)

    def validate(
        self,
        check: Callable = None,
        model: Callable = None,
        failfast=True,
    ):
        try:
            valid_check, valid_model = True, True
            result = []
            original_data = self.unwrap()

            for item in original_data:
                if model:
                    valid_model = isinstance(item, model)

                if check:
                    valid_check = check(item)

                if failfast:
                    assert valid_check is True
                    assert valid_model is True

                if valid_check and valid_model:
                    result.append(item)

            if failfast:
                return Box(data=original_data)
            return Box(data=result)

        except AssertionError as err:
            print("Validation failed >> ", err)
            raise err
