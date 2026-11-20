# __import__ — build the name

`__import__('o'+'s')`, `__builtins__['__imp'+'ort__']` — the name is
built so a word blacklist never sees 'import'.

## The build

import built as a string — the blacklist sees the pieces.
