from functools import partial
import pytest
from mithrandir import (
    __version__,
    Op,
    Monad,
    MonadSignatures as Sig,
)


def test_version():
    assert __version__ == "1.3.1"


def test_01():
    hello = partial(print, "hello reasult")

    genesis = Monad()
    genesis.unwrap(hello)
    list_of_ten = list(range(10))

    res1 = genesis | Sig.UNWRAP
    assert not res1

    res1 = genesis | Sig.RESOLVE
    assert not res1.unwrap()

    res1 = genesis | Op.CONCAT(*list_of_ten) | Sig.UNWRAP

    print(res1)
    assert len(res1) == 10
    assert not genesis.unwrap()
    assert not genesis.awaiting

    res2 = genesis | Op.CONCAT(*list_of_ten) | Sig.RESOLVE

    print(res2)
    assert isinstance(res2, Monad)
    assert (res2 | Sig.UNWRAP) == list_of_ten

    def print_and_return(d):
        print(d)
        return d

    res3 = (
        # fmt off
        res2
        | Op.MAP(str)
        | Op.BIND(print_and_return)
        | Op.FILTER(lambda x: int(x) > 5)
    )

    print(res3)
    assert isinstance(res3, Monad)
    assert res3.awaiting is False
    resolved = res3 | Sig.UNWRAP
    print(resolved)
    assert len(resolved) == 4

    res4 = (
        # fmt off
        genesis
        | Op.CONCAT(*list_of_ten)
        | Op.MAP(lambda x: x * 2)
        | Op.CONCAT(*list(range(0, 200, 3)))
        | Op.MAP(lambda x: [{"val": x}])
        | Op.FILTER(lambda x: x[0]["val"] % 2 == 0)
        | Op.FOLD(lambda v, x: [*v, str(x[0]["val"])], [])
        | Op.MAP(list)
        | Op.FLATTEN()
        | Op.DISTINCT(key=lambda x: x[0])
        | Op.MAP(int)
        | Op.VALIDATE(model=int)
        | Op.VALIDATE(test=lambda x: isinstance(x, int))
        | Op.SORT()
        | Op.JOIN(Monad(9999999))
        | Sig.RESOLVE
    )

    expected = [0, 2, 4, 6, 8, 10, 30, 54, 72, 90, 9999999]
    assert res4.unwrap() == expected

    with pytest.raises(TypeError):
        Monad(["1"]) | Op.VALIDATE(model=int) | Sig.RESOLVE

    no_fail_data = Monad(["1", 2]) | Op.VALIDATE(model=int, failfast=False) | Sig.UNWRAP
    assert no_fail_data == [2]
