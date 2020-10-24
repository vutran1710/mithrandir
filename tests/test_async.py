from typing import List, Dict
import asyncio  # noqa
import pytest  # noqa
import pytest_asyncio.plugin  # noqa
from mithrandir import __version__, Op, Monad, MonadSignatures as Sig

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function")
async def setup():
    pass


async def test_async():
    async def inc_by_2(n: int):
        return n + 2

    async def only_gt_10(n: int):
        return n > 10

    async def to_int(n: str):
        return int(n)

    def convert_to_map(final: Dict[str, int], val: int):
        final.update({f"{val}__key": val})
        return final

    async def convert_map_to_array(d: List[Dict]):
        return d[0].values()

    def only_less_than_30(n: int):
        return n < 30

    async_monad = await (
        # fmt off
        Monad(list(range(20)))
        | Op.MAP(inc_by_2)
        | Op.FILTER(only_gt_10)
        | Op.MAP(str)
        | Op.FILTER(lambda x: "2" in x)
        | Op.SORT(reverse=True)
        | Op.MAP(to_int)
        | Op.CONCAT(*list(range(50, 100, 3)))
        | Op.FOLD(convert_to_map, dict())
        | Op.BIND(convert_map_to_array)
        | Op.DISTINCT()
        | Op.FILTER(only_less_than_30)
        | Sig.RESOLVE
    )

    assert async_monad.unwrap() == [21, 20, 12]
