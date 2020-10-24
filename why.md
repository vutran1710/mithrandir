---
description: 'Because consistency, that''s why!'
---

# Why?

Let's start with the building block: the `Monad` itself

## Monad

```python
from mithrandir import Monad

bilbo = Monad("ring_lord")
sauron = Monad(["ring_dark_lord"])
elve = Monad()
```

Whatever data you are about to box with Monad, it will always keep the data in a `list`, unless the data is a **list** itself. Try to unwrap them one by one...

```python
print(bilbo.unwrap()) # -> ["ring_lord"]
print(sauron.unwrap()) # -> ["ring_dark_lord"]
print(elve.unwrap()) # -> []
```

### Why? 

Processing a single item is just an edge case of applying a processing-function over a list of items of a same type. In another word, it is still basically a mapping over a list of one-single item. That's why performing a Map with Monad is safe.

```python
from mithrandir import Op, MonadSignatures as Sig

def to_string_length(text: str) -> int:
    return len(text)
    
count = (
    bilbo
    | Op.MAP(to_string_length)
    | Sig.RESOLVE
)

print(count.unwrap()) # -> [9]
```

### Operator-overloading

Overloading the operator `|` might not be everyone's cup of tea, but generally speaking, it's **my choice,** so deal with it! The operator is just a syntactic-sugar for **Monad's binding function.**

