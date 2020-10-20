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
