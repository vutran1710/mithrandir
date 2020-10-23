from typing import Callable
from enum import Enum
from .operators import OperatorSignatures


class MonadSignatures(Enum):
    UNWRAP = "unwrap"
    RESOLVE = "resolve"


class Monad:
    # Data
    __d = []

    # NOTE: function-chain
    __c = []

    # NOTE: async or not
    __as = False

    def __init__(self, data=None, cb=None):
        if data is not None:
            self.__d = data
            if not isinstance(data, list):
                self.__d = [data]

        self.__c = [] if not cb else cb

    def pending(self):
        return self.__c

    def __or__(self, args):
        """Operator-overloading for binding"""
        if isinstance(args, MonadSignatures):
            return getattr(self, args.value)()
        return Monad(data=self.__d, cb=[*self.__c, args])

    def __str__(self):
        return f"Monad[async={self.__as}]<{self.__d}>"

    def resolve(self):
        """resolve all of function chain"""
        return Monad(data=self.__resolve_chain())

    def unwrap(self, callback: Callable = None):
        """resolve and return value"""
        if not self.__c:
            return self.__d if not callback else callback(self.__d)
        return self.__resolve_chain()

    def __resolve_chain(self):
        cursor = 0
        result = [*self.__d]
        cbs = self.__c

        if not cbs:
            return self.__d

        while cbs[cursor:]:
            sig, func = cbs[cursor:][0]

            if sig == OperatorSignatures.MAP:
                result = list(map(func, result))

            if sig == OperatorSignatures.FILTER:
                result = list(filter(func, result))

            if sig == OperatorSignatures.CONCAT:
                result += func(result)

            if sig == OperatorSignatures.FOLD:
                result = [func(result)]

            if sig == OperatorSignatures.BIND:
                result = func(result)

            if sig == OperatorSignatures.FLATTEN:
                result = func(result)

            if sig == OperatorSignatures.DISTINCT:
                result = func(result)

            if sig == OperatorSignatures.SORT:
                result = func(result)

            cursor += 1

        return result
