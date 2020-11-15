from functools import partial
import asyncio  # noqa
import pytest  # noqa
import pytest_asyncio.plugin  # noqa
from mithrandir.box import Box
from mithrandir.op import op

pytestmark = pytest.mark.asyncio


def test_box():
    """Boxing and unboxing"""
    my_box = Box()
    assert my_box.unwrap() == []

    my_box = Box(1)
    assert my_box.unwrap() == [1]

    my_box = Box([1])
    assert my_box.unwrap() == [1]

    my_box = Box(None)
    assert my_box.unwrap() == []

    my_box = Box([None])
    assert my_box.unwrap() == []

    my_box = Box("abc")
    assert my_box.unwrap() == ["abc"]

    my_box = Box(["abc"])
    assert my_box.unwrap() == ["abc"]

    print("boxtype -->", type(my_box))
    print("boxtype --> unwraped", type(my_box.unwrap()))


def test_box_pure_transformer_chain():
    box = Box(data=list(range(5)))

    def inc_by_2(x):
        return x + 2

    def multi_by_3(x):
        return x * 3

    def only_even(x):
        return x % 2 == 0

    result = box.resolve()
    print(">>>>>>>>>", result)

    result = box.pipe(
        lambda x: list(map(inc_by_2, x)),
        lambda x: list(map(multi_by_3, x)),
        lambda x: list(filter(only_even, x)),
    ).resolve()

    assert result.unwrap() == [6, 12, 18]


async def test_async():
    box = Box(data=list(range(5)))

    async def inc_by_2(x):
        return x + 2

    async def multi_by_3(x):
        return x * 3

    def only_even(x):
        return x % 2 == 0

    transform_chain = box.pipe(
        op.map(inc_by_2),
        op.map(multi_by_3),
        op.filter(only_even),
    )

    assert isinstance(transform_chain, Box)
    assert transform_chain.has_effect
    result = await transform_chain.resolve()
    assert result.unwrap() == [6, 12, 18]
