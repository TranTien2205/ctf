# Reaching __builtins__ — the eval/exec home

`__builtins__` carries eval/exec/__import__/open — reach it through
a function's `__globals__`, a class's `__init__.__globals__`, or the
subclasses walk to a class that imports.

## The home

eval/exec/__import__/open live under __builtins__.

## Reachable

via __globals__, a class init, or the walk.

## The home

eval/exec/import/open under __builtins__.
