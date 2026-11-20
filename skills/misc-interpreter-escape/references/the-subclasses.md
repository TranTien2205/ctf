# The __subclasses__ walk — enumerate at run time

`().__class__.__base__.__subclasses__()` lists every live subclass —
the gadget's index differs per build; enumerate it at run time,
never hard-code from a different interpreter.

## Enumerate

The live list, by name — never a hard-coded index.

## Live

The index differs per build — enumerate, do not hard-code.

## By name

Find the gadget by name in the live list.
