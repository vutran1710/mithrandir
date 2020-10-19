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
        .map(inc_by_2)
    
    print(data)
    assert data.unwrap() == [10, 5, 7]

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2)
    
    print(data)
    assert data.unwrap() == [20, 10, 14]

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .filter(only_more_than_15)
    
    print(data)
    assert data.unwrap() == [20]

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .filter(only_more_than_15) \
        .bind(int_to_range)

    print(data)
    assert len(data.unwrap()) == 20

    data = res \
        .map(inc_by_2) \
        .map(multiply_by_2) \
        .filter(only_more_than_15) \
        .bind(int_to_range) \
        .reduce(gather_to_set, set())

    print(data)
    assert len(data.unwrap()) == 1
    assert len(data.unwrap()) == 1
    assert isinstance(data.unwrap()[0], set)

    # res |= inc_by_2
    # print(res)
    # assert res.unwrap() == [10, 5, 7]

    # # sync-chain of multi synchronous binds
    # chained = res | inc_by_2 | multiply_by_2
    # print(chained)
    # assert chained.unwrap() == [24, 14, 18]
    # # using monad-signature
    # unwrapped_chain_result = res | inc_by_2 | multiply_by_2 | Sig.UNWRAP
    # assert unwrapped_chain_result == [24, 14, 18]
    # # filter
    # chained ^= only_more_than_15
    # print(chained)
    # assert chained.unwrap() == [24]

    # unwrapped_chain_result = (
    #     # fmt off
    #     res
    #     | Sig.MAP(inc_by_2)
    #     | Sig.MAP(multiply_by_2)
    #     | Sig.MAP(only_more_than_15)
    #     | Sig.UNWRAP
    # )
    # assert unwrapped_chain_result == [24]
    # # original monad remain untouched
    # assert res.unwrap() == [10, 5, 7]

    # assert isinstance(res, Monad)
    # print(res.unwrap())
    # assert res.head() == 5
