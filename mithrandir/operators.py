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


class Op:
    """Operator to perform on monad-binding"""

    @staticmethod
    def MAP(fn, *args, **kwargs):
        def __(x: Any):
            return fn(x, *args, **kwargs)

        return OperatorSignatures.MAP, __

    @staticmethod
    def FILTER(fn, *args, **kwargs):
        def __(x: Any):
            return bool(fn(x, *args, **kwargs))

        return OperatorSignatures.FILTER, __

    @staticmethod
    def FOLD(fn: Callable, default: Any):
        def __(d: List):
            return reduce(fn, d, default)

        return OperatorSignatures.FOLD, __

    @staticmethod
    def CONCAT(*args):
        def __(d: List):
            return [*d, *args]

        return OperatorSignatures.CONCAT, __

    @staticmethod
    def FLATTEN():
        def __(d: List):
            result = [item for sublist in d for item in sublist]
            return result

        return OperatorSignatures.FLATTEN, __

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

        return OperatorSignatures.DISTINCT, __

    @staticmethod
    def SORT(*, key=lambda x: x):
        def __(d: List):
            return sorted(d, key=key)

        return OperatorSignatures.SORT, __
