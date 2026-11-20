# Non-ASCII rounds — utf8 drift

A round with wide chars or utf8 — parse bytes, decode per field;
a len() on bytes vs chars splits differently.

## Bytes vs chars

Parse bytes, decode per field — len() differs.
