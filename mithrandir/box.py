from typing import Any, TypeVar, List, Union, Callable


T = TypeVar("T")


def auto_boxing(data: T) -> List[Union[T, Any]]:
    if isinstance(data, list):
        return data
    return [data]


class Box:
    """Box - a friendly term that
    makes sense to everyone instead of `Monad`
    It's like a simplified monad
    """

    def __init__(self, data: T = None):
        self.__wrapped = auto_boxing(data)

    def unwrap(self):
        return self.__wrapped

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
