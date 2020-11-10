from functools import partial
import asyncio  # noqa
import pytest  # noqa
import pytest_asyncio.plugin  # noqa
from mithrandir.box import Box, BoxOp

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

    assert box.map(inc_by_2).map(str).unwrap() == ["2", "3", "4", "5", "6"]
    assert box.unwrap() == [0, 1, 2, 3, 4]

    transformed = (
        box.map(inc_by_2)
        .peek(print)
        .map(multi_by_3)
        .peek(print)
        .filter(only_even)
        .peek(print)
        .map(str)
        .tap(partial(print, "value is >"))
        .validate(model=str)
    )

    assert transformed.unwrap() == ["6", "12", "18"]

    assert transformed.validate(
        check=lambda x: len(x) < 2, failfast=False
    ).unwrap() == ["6"]

    with pytest.raises(AssertionError):
        transformed.validate(check=lambda x: len(x) < 2).unwrap()

    with pytest.raises(ValueError):
        box2 = Box("9")
        box3 = Box(10)
        transformed.join(box2, box3)

    box2 = Box("9")
    box3 = Box(10)

    with pytest.raises(AssertionError):
        transformed.join(box2, box3, model=str)

    box3 = Box("10")
    big_box = transformed.join(box2, box3, model=str)
    assert big_box.unwrap() == ["6", "12", "18", "9", "10"]


async def test_box_side_effect():
    box = Box(1)

    async def inc_by_2(x):
        return x + 2

    def mul_by_3(x):
        return x * 3

    def fail_effect(x):
        raise Exception("DummyException")

    data = await box.effect(BoxOp.MAP, inc_by_2)
    assert data.unwrap() == [3]

    data = await box.effect(BoxOp.MAP, mul_by_3)
    assert data.unwrap() == [3]

    data = await box.effect(BoxOp.MAP, fail_effect)
    assert data.unwrap() == [1]
