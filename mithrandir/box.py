from enum import Enum
from typing import Any, TypeVar, List, Union, Callable
from asyncio import iscoroutine


T = TypeVar("T")


def auto_box(data: T) -> List[Union[T, Any]]:
    if isinstance(data, list):
        return data
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


class Box:
    """Box - a friendly term that
    makes sense to everyone instead of `Monad`
    It's like a simplified monad
    """

    def __init__(self, data: T = None):
        self.__wrapped = auto_box(data)

    def unwrap(self):
        return self.__wrapped

    async def effect(self, signal: BoxSignal, *args, **kwargs):
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
        data = list(map(func, self.__wrapped))
        return Box(data=data)

    def filter(self, pred: Callable):
        data = list(filter(pred, self.__wrapped))
        return Box(data=data)

    def tap(self, func: Callable):
        for item in self.__wrapped:
            func(item)

        return self

    def apppend(self, *other_boxs: List[T], model):
        data = [*self.__wrapped]
        for box in other_boxs:
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

            for item in self.__wrapped:
                if model:
                    valid_model = isinstance(model, item)
                if check:
                    valid_check = check(item)
                if failfast:
                    assert valid_check is True
                    assert valid_model is True
                    continue

                if valid_check and valid_model:
                    result.append(item)

            if failfast:
                return Box(data=self.__wrapped)
            return Box(data=result)

        except AssertionError as err:
            print("Validation failed >> ", err)
            raise err
