# The input format — what the read accepts


The read's format constrains the payload:

- gets: until newline — no 0x0a inside.
- read(n): n raw bytes — anything goes.
- scanf %s: whitespace-terminated.
- fgets: newline or n-1 — keeps the newline.

## The check

The read function's semantics bound the payload's shape.
