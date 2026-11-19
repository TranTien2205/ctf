# Type confusion via overlap — the payoff


The overlap's value: writing object A's fields through object B's type —
a "name" buffer overlapping a "vtable" object writes a call target.

## The recipe

1. Overlap a data-carrying object (controllable bytes) with a
   pointer-carrying object (vtable/func-ptr/string-ptr).
2. Write via the data object → the pointer object's pointer now aims
   where you wrote.
3. Trigger the pointer's use → read/write/call redirected.

## Choosing the pair

- Small-data + function-pointer: exec redirect.
- Small-data + string-pointer: arbitrary read (print-the-pointer).
- Small-data + free-slot-pointer: free an arbitrary address (house of
  spirit style).

## Falsifier

No pointer-bearing object type is allocatable in the same size class:
the confusion pair can't form.
