# repr/str — the object leak

`repr(obj)`/`str(obj)` leak the object's class and address — recon
when the call is blocked but a dunder still runs.