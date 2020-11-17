import asyncio  # noqa
import pytest  # noqa
import pytest_asyncio.plugin  # noqa
from mithrandir.box import Box
from mithrandir.op import op, compose

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

    with pytest.raises(ValueError):
        my_box.resolve = 5

    with pytest.raises(ValueError):
        my_box.has_effect = 1

    with pytest.raises(ValueError):
        Box([1, "a"], validator=str)


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
        op.map(multi_by_3),
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

    async def greater_than_ten(x):
        return x > 10

    transform_chain = box.pipe(
        op.map(inc_by_2),
        op.map(multi_by_3),
        op.filter(only_even),
        op.filter(greater_than_ten),
        op.each(lambda x: print(">>>>>>>>>>>>>>>> x=", x)),
    )

    assert isinstance(transform_chain, Box)
    assert transform_chain.has_effect

    result = await transform_chain.resolve()
    assert result.unwrap() == [12, 18]

    folding = transform_chain.pipe(
        op.fold(lambda a, b: a + b),
    )

    result = await folding.resolve()
    assert result.unwrap() == [30]

    async def async_sum(a, b):
        return a + b

    folding = transform_chain.pipe(op.fold(async_sum, initial=2))

    assert isinstance(folding, Box)

    result = await folding.resolve()
    assert result.unwrap() == [32]
    result = await result.pipe(op.fold(async_sum, initial=2)).resolve()
    assert result.unwrap() == [34]

    result = await transform_chain.pipe(
        op.fold(async_sum, initial=2),
        op.fold(async_sum, initial=2),
    ).resolve()
    assert result.unwrap() == [34]

    result = (
        await transform_chain.pipe(op.fold(async_sum, initial=2))
        .pipe(op.fold(async_sum, initial=2))
        .resolve()
    )
    assert result.unwrap() == [34]

    assert Box().pipe(op.fold(sum)).resolve().unwrap() == []
    assert (await Box().pipe(op.fold(async_sum)).resolve()).unwrap() == []


async def test_switch_map():
    from functools import partial

    async def inc_by_2(x):
        return x + 2

    async def multi_by_3(x):
        return x * 3

    def only_even(x):
        return x % 2 == 0

    async def greater_than_ten(x):
        return x > 10

    async def ping(x):
        print("Hello x", x)

    box = Box(data=list(range(3)))

    true_func = compose(
        op.map(inc_by_2),
        op.map(multi_by_3),
    )

    false_func = compose(
        op.map(multi_by_3),
        op.filter(only_even),
    )

    branching = op.if_else(True, true_func, false_func)
    assert callable(branching)
    test = await branching([1, 2])
    assert test == [9, 12]

    branching = op.if_else(False, true_func, false_func)
    test = await branching([1, 2])
    assert test == [6]

    result = await box.pipe(
        branching,
        op.map(str),
    ).resolve()

    assert result.unwrap() == ["0", "6"]

    result = await box.pipe(
        op.map(multi_by_3),
        op.map(multi_by_3),
        op.each(ping),
        op.if_else(
            lambda x: x[0] > 0,
            op.map(inc_by_2),
            op.filter(greater_than_ten),
        ),
        op.map(str),
    ).resolve()

    assert result.unwrap() == ["18"]
