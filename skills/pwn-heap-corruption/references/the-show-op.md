# The show op — the leak channel


show(i) reads ptr[i]'s contents — on a freed slot it prints the bin
metadata (fd/bk) sitting in the user area: the cheapest leak channel.

## Use

- show on a tcache'd chunk → mangled fd + (pos) — heap leak data.
- show on an unsorted chunk → main_arena address — the libc leak.
- show on a UAF-overlapped chunk → the overlapping object's fields.

## Falsifier

No show/read op exists: leaks need a different channel — a crash
oracle, a write-side inference, or an external disclosure.
