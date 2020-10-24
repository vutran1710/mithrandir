from asyncio import iscoroutinefunction as is_async
from typing import Callable, List, Any
from functools import reduce
from enum import Enum


class OperatorSignatures(Enum):
    MAP = "map"
    FILTER = "filter"
    CONCAT = "concat"
    FOLD = "fold"
    FLATTEN = "flatten"
    DISTINCT = "distinct"
    SORT = "sort"
    BIND = "bind"
    VALIDATE = "validate"


class Op:
    """Operator to perform on monad-binding"""

    @staticmethod
    def BIND(fn, *args, **kwargs):
        def __(d: List[Any]):
            return fn(d, *args, **kwargs)

        return OperatorSignatures.BIND, __, is_async(fn)

    @staticmethod
    def MAP(fn, *args, **kwargs):
        def __(x: Any):
            return fn(x, *args, **kwargs)

        return OperatorSignatures.MAP, __, is_async(fn)

    @staticmethod
    def FILTER(fn, *args, **kwargs):
        def __(x: Any):
            return fn(x, *args, **kwargs)

        return OperatorSignatures.FILTER, __, is_async(fn)

    @staticmethod
    def FOLD(fn: Callable, default: Any):
        def __(d: List):
            return reduce(fn, d, default)

        return OperatorSignatures.FOLD, __, False

    @staticmethod
    def CONCAT(*args):
        def __(d: List):
            return [*d, *args]

        return OperatorSignatures.CONCAT, __, False

    @staticmethod
    def FLATTEN():
        def __(d: List):
            result = [item for sublist in d for item in sublist]
            return result

        return OperatorSignatures.FLATTEN, __, False

    @staticmethod
    def DISTINCT(*, key=lambda x: x):
        def __(d: List):
            found = set()
            result = []

            for item in d:
                identity = key(item)
                if identity in found:
                    continue
                result.append(item)
                found.add(identity)

            return result

        return OperatorSignatures.DISTINCT, __, False

    @staticmethod
    def SORT(*, key=lambda x: x, **kwargs):
        def __(d: List):
            return sorted(d, key=key, **kwargs)

        return OperatorSignatures.SORT, __, False

    @staticmethod
    def VALIDATE(test: Callable = None, model=None, failfast=True):
        def __(d: List):
            if not test and not model:
                return d
            result = []
            for item in d:
                test_validate, model_validate = True, True
                if test:
                    test_validate = test(item)
                if model:
                    model_validate = isinstance(item, model)
                if not test_validate or not model_validate:
                    if failfast:
                        raise TypeError
                    continue
                result.append(item)
            return result

        return OperatorSignatures.VALIDATE, __, False
