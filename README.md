# Mithrandir

free-form monad & other crazy implementations

### Features
- async/await
- operator-overloading

```python
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
