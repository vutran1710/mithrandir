from typing import Callable
from asyncio import gather
from asyncio import iscoroutinefunction as is_async, iscoroutine as is_awaiting
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
            attr = f"async_{args.value}" if self.__as else args.value
            return getattr(self, attr)()

        next_md = Monad(data=self.__d, cb=[*self.__c, args])
        next_md.__as = self.__as or args[2]
        return next_md

    def __str__(self):
        return f"Monad[async={self.__as}]<{self.__d}>"

    def resolve(self):
        """resolve all of function chain"""
        return Monad(data=self.__resolve_chain())

    async def async_resolve(self):
        """resolve all of function chain"""
        data = await self.__async_resolve_chain()
        return Monad(data=data)

    def unwrap(self, callback: Callable = None):
        """resolve and return value"""
        if not self.__c:
            return self.__d if not callback else callback(self.__d)
        return self.__resolve_chain()

    async def __async_resolve_chain(self):
        cursor = 0
        result = [*self.__d]
        cbs = self.__c

        while cbs[cursor:]:
            sig, func, awaiting = cbs[cursor:][0]

            if sig == OperatorSignatures.VALIDATE:
                result = func(result)

            if sig == OperatorSignatures.MAP:
                result = (
                    list(map(func, result))
                    if not awaiting
                    else [await func(x) for x in result]
                )

            if sig == OperatorSignatures.FILTER:
                result = (
                    list(filter(func, result))
                    if not awaiting
                    else [x for x in result if bool(await func(x))]
                )

            if sig == OperatorSignatures.CONCAT:
                result += func(result)

            if sig == OperatorSignatures.FOLD:
                result = [func(result)] if not awaiting else [await func(result)]

            if sig == OperatorSignatures.BIND:
                result = func(result) if not awaiting else await func(result)

            if sig == OperatorSignatures.FLATTEN:
                result = func(result)

            if sig == OperatorSignatures.DISTINCT:
                result = func(result)

            if sig == OperatorSignatures.SORT:
                result = func(result)

            cursor += 1

        return result

    def __resolve_chain(self):
        cursor = 0
        result = [*self.__d]
        cbs = self.__c

        if not cbs:
            return self.__d

        while cbs[cursor:]:
            sig, func, _ = cbs[cursor:][0]

            if sig == OperatorSignatures.VALIDATE:
                result = func(result)

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
