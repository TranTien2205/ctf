# A char blacklist — avoid the byte

Blocked `'`/`"`/`(`/`)`/`_` — f-strings, format specs, hex/unicode
escapes, a docstring, `[::1]` avoid the literal byte.

## The byte

The byte is built from an escape/f-string, never typed literally.
