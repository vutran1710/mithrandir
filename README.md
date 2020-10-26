---
description: Reasoning the logic flow with Magic
---

# Mithrandir

## Installation

As much simple as it could be, use `pip` , `pipenv` or `poetry` :

```
$ pip install mithrandir
```

{% hint style="info" %}
Remember to check out the latest version available
{% endhint %}

Once you have **Mithrandir** in your presence, let him be your guide...

{% code title="$ python" %}
```python
>> from mithrandir import Monad, Op, MonadSignature as Sig
>> magic = Monad(1) | Op.MAP(lambda x: x + 1)
>> print("magic = ", magic)
... "magic = Monad<async_mode=False>[2]"
>> # Give me your blessing...
>> print("blessed-value = ", magic.unwrap())
... "blessed-value = 2"
```
{% endcode %}

For more advanced tutorials and examples, check out the next parts of the document

