# Mithrandir

free-form monad & other crazy implementations

### Features
- async/await
- operator-overloading

### Examples
On sync-mode:
```python
list_of_ten = list(range(10))

data = (
    Monad([])
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

assert data == [0, 2, 4, 6, 8, 10, 30, 54, 72, 90]
```

On `async`, simply add `await` before everything
```python
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
```

### Usage
- Refer `tests`


### Coverage
```
Coverage report: 98%
-------
Total	86	2	0	98%
mithrandir/__init__.py	1	0	0	100%
mithrandir/monad.py	85	2	0        98%
-------
coverage.py v5.3, created at 2020-10-20 15:25 +0700
```
