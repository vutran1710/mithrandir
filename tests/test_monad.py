from typing import List
import asyncio  # noqa
import pytest  # noqa
import pytest_asyncio.plugin  # noqa
from mithrandir.monad import Monad, MonadSignatures as Sig

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function")
async def setup():
    pass


async def test_01():
    def inc_by_2(n: int):
        return n + 2

    def multiply_by_2(n: int):
        return n * 2

    def only_more_than_15(n: int):
        return n > 15

    def int_to_range(n: List[int]):
        return list(range(n[0]))

    def gather_to_set(a: set, b: int):
        a.add(b)
        return a

    res = Monad()
    print(res)
    assert res.unwrap() == []
    res = res.add(3)
    print(res)
    assert res.unwrap() == [3]
    res = res.add(5)
    print(res)
    assert res.unwrap() == [3, 5]
    res = Monad(8).add(res)
    print(res)
    assert res.unwrap() == [8, 3, 5]
    
    data = res \
        .map(inc_by_2) \
        .sync_resolve()
    
    print(data)
    assert data.unwrap() == [10, 5, 7]

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .sync_resolve()
    
    print(data)
    assert data.unwrap() == [20, 10, 14]

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .filter(only_more_than_15) \
        .sync_resolve()
    
    print(data)
    assert data.unwrap() == [20]

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .filter(only_more_than_15) \
        .bind(int_to_range) \
        .sync_resolve()

    print(data)
    assert len(data.unwrap()) == 20

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .filter(only_more_than_15) \
        .bind(int_to_range) \
        .reduce(gather_to_set, default=set()) \
        .sync_resolve()

    print(data)
    assert len(data.unwrap()) == 1
    assert len(data.unwrap()) == 1
    assert isinstance(data.unwrap()[0], set)
