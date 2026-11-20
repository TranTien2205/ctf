# ${var:offset:1} — slice a char

`${PATH:0:1}` is `/`; `${HOME:1:1}` a letter — slice characters out
of an existing variable to build a command the filter never sees.

## The char

${var:o:1} slices a char from a live variable.
