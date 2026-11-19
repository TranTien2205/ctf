# Theory — why enumeration is a property of authentication

## The information-theoretic view

An auth system is a function `f(username, password) -> response`. The
attacker wants `exists(username)`. If `f` is non-injective in the
username — if any response channel differs by whether the user exists —
`exists` is computable from `f`'s output. The defense is to make `f`'s
observable output independent of `exists` — which requires equalizing
EVERY channel: the text, the status, the redirect, the timing, the
cookie, the email, the lock. Equalizing all of them is hard; missing
one is the bug.

## The work-asymmetry is fundamental

`verify(password, hash)` is expensive BY DESIGN — a memory-hard hash
resists brute force. The same cost that resists the attacker also
creates the oracle: `exists=1` pays the cost, `exists=0` skips it.
You cannot both "hash only real users" and "leak nothing about
existence" without paying the hash cost on the miss — which is why the
fix (a dummy hash on the `None` arm) is a known but rarely-applied cost.

## The state-dependent response

An auth system's response depends on account STATE, not just existence:
`active`, `locked`, `pending`, `disabled`, `deleted`. Each state is a
different response — so even a "uniform" error for `nonexistent` may
differ from `locked`/`pending`/`disabled`, all of which confirm the
row exists. Existence leaks through the state space.

## The channel space is large

The attacker measures the full response envelope: body bytes, status,
headers, cookies, timing, and the SIDE EFFECTS (an email sent, a lock
set, an audit row). The defender must equalize all of it; the attacker
needs one channel. The asymmetry favors the attacker — one residual
channel is enough.

## Why it is a class, not a technique

"User enumeration" is a family of oracles over the same asymmetry —
the work and state differences between a real and a fake account. Each
channel is a technique; the class is the set. The budget belongs to the
class; a closed channel is a measurement, not a retry.

## The throttle as the dual finding

The same endpoint carries the dual question: is the guessing loop
bounded? A missing throttle makes any weak-credential attack feasible;
a bypassable throttle is a broken control. The class covers both
halves because they are measured on the same endpoint with the same
bounded-probe method.
