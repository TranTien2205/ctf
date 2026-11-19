# The arg values — pointers vs immediates


An arg qword can be: a pointer (an address), an immediate (a number),
a null (0) — the gadget's pop puts it in the register literally; the
call interprets it.
