from functools import reduce, partial
from mithrandir import __version__, Op, Monad, MonadSignatures as Sig


def test_version():
    assert __version__ == "1.0.0"


def multi_map_apply(items, funcs):
    result = []
    for i in items:
        counter = 0
        r = None
        while funcs[counter:]:
            r = funcs[counter:][0](i)
            counter += 1
        if r is not None:
            result.append(r)

    return result


def test_01():
    items = [1, 2, 3]
    funcs = [str, int, str]
    result = multi_map_apply(items, funcs)
    assert result

    items = []
    funcs = []
    result = multi_map_apply(items, funcs)
    assert not result


def test_02():
    hello = partial(print, "hello reasult")

    genesis = Monad()
    genesis.unwrap(hello)
    list_of_ten = list(range(10))

    res1 = genesis | Op.CONCAT(*list_of_ten) | Sig.UNWRAP

    print(res1)
    assert len(res1) == 10
    assert not genesis.unwrap()
    assert not genesis.pending()

    res2 = genesis | Op.CONCAT(*list_of_ten) | Sig.RESOLVE

    print(res2)
    assert isinstance(res2, Monad)
    assert (res2 | Sig.UNWRAP) == list_of_ten

    res3 = (
        # fmt off
        res2
        | Op.MAP(str)
        | Op.FILTER(lambda x: int(x) > 5)
    )

    print(res3)
    assert isinstance(res3, Monad)
    assert res3.pending()
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
        | Op.SORT()
        | Sig.RESOLVE
    )

    expected = [0, 2, 4, 6, 8, 10, 30, 54, 72, 90]
    assert res4.unwrap() == expected


# def test_02():
#     fchain = [(sig, f)]
#     items = []
#     final = []

#     start = 0
#     rem_chain = fchain[start:]

#     sub_f_chain = []

#     while rem_chain:
#         sig, func = rem_chain[0]

#         if len(rem_chain) < 2:
#             # resolve...
#             pass


#         nextfunc = rem_chain[1]

#         if sig == "Bind":
#             final = func(final)

#         if nextfunc[0] != "Bind":
#             # note: join stack
#             sub_f_chain.append(func)
#         else:
#             final = multi_map_apply(final, sub_f_chain)
#             sub_f_chain = []
