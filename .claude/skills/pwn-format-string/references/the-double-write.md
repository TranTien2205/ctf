# The double-write — pointer chains through two writes


When the arg can't hold your full pointer (alignment, truncation), a
first write can plant the pointer that a second write then uses.

## Steps

1. Write the pointer value into a writable slot (bss/stack var).
2. That slot is now an argument containing your pointer.
3. Second call: %N$s/%N$n at that slot's index → uses your pointer.

## Falsifier

The service is one-shot (can't do two calls) or no writable slot exists
at an arg position.
