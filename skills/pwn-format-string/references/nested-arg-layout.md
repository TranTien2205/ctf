# Nested argument layout — the callee's frame view


The printf call's args reflect the CALLER's frame at the call site: rsi..r9
then the caller's stack args — which include the caller's locals passed
by position plus whatever stack memory follows.

## The view

- %1-%6 (x64): the caller's register args to printf.
- %7+: the caller's stack-resident args + memory above.
- Your input buffer sits wherever the caller placed it.

## Falsifier

None — informational; the layout explains WHY the arg-offset is what it
is.
