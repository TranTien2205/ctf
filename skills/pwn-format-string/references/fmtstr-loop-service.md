# The loop service — multi-call exploitation


A looping service (menu-driven, reconnect, read-loop) gives many format
calls: call 1 leaks, call 2 writes, call 3 confirms — the clean case.

## Steps

1. Call 1 — the leak: %p dump, name the addresses.
2. Call 2 — the write: plant pointer + %n composition.
3. Call 3 — read-back verify: %N$s on the slot confirms the value.
4. Each call is independent — N re-measured if the site changed.

## Advantages

- Leaked values usable in the NEXT call's payload.
- Failed writes retryable (idempotent slots).
- Stage separation — verify each before the next.

## Falsifier

State resets between calls (fresh process, new stack): the leak of call 1
is stale by call 2.
