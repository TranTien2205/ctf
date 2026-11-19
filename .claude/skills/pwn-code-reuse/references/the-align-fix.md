# The alignment fix — where the ret goes


The alignment ret goes BETWEEN the last arg-pop and the call target —
its job: make rsp 16-byte-aligned at the call's entry.

## The test

Count the qwords from the call site to the ret-addr the call will
see: if rsp at the function's entry isn't 0 mod 16, insert a ret.

## The rule of thumb

One ret usually fixes it; two if the count was odd-and-off.
