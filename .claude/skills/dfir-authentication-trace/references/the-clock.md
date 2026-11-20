# The clock — UTC vs LOCAL

`hayabusa` renders LOCAL by default (`-U`); `chainsaw` is already
UTC (`--local` breaks it). FILETIME fields are UTC. A timestamp at
the wrong precision is graded wrong — keep the millisecond.

## UTC

hayabusa is LOCAL default; chainsaw UTC; FILETIME UTC.
