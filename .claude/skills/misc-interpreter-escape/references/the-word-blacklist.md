# A word blacklist — build the name

`getattr(obj, "attr"[::-1])`, `"at"+"tr"`, `chr()` joins — a word
blacklist sees the built string, never the source. pyjail_gen emits
a chr-join for a banned attribute name.

## The build

'at'+'tr', 'attra'[::-1], chr(95)+chr(95) — built, never typed.
