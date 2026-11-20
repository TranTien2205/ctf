# catch_warnings — a second gadget

`warnings.catch_warnings` reaches `__init__.__globals__` with
builtins — a fallback when _wrap_close is absent.

## The fallback

catch_warnings.__init__.__globals__ — builtins reachable.
