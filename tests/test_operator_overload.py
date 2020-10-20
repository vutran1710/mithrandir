from typing import List
import asyncio  # noqa
import pytest  # noqa
import pytest_asyncio.plugin  # noqa
from mithrandir.monad import Monad, MonadSignatures as Sig, Validator

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function")
async def setup():
    pass


async def test_async():
    async def inc_by_2(n: int):
        return n + 2

    res = Monad([3, 9])

    data = await (
        res
        | inc_by_2
        | Validator(int)
        | Sig.RESOLVE
    )

    assert data.unwrap() == [5, 11]

    with pytest.raises(TypeError):
        data = await (
            res
            | inc_by_2
            | Validator(str)
            | Sig.RESOLVE
        )

        assert data.unwrap() == [5, 11]

