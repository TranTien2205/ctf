# os._wrap_close — the common gadget

`os._wrap_close` is in nearly every subclass list; its
`__init__.__globals__` carries `system`/`popen` — the standard
pyjail RCE gadget.

## The standard

_wrap_close.__init__.__globals__[system] — the common RCE.
