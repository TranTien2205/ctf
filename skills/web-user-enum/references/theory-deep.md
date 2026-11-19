# Theory (deep) — the information-theoretic core

## Existence as a covert channel

`f(username, password) -> response` leaks `exists(username)` iff the
observable output is a function of `exists`. The defense requires the
output to be constant in `exists` — which means equalizing EVERY
channel: text, status, redirect, headers, cookies, timing, and every
side-effect (email, lock, audit). The attack surface is the union of
channels; the defense must cover all of them; the attacker needs one.

## The cost asymmetry is load-bearing

`verify(password, hash)` is expensive BY DESIGN — the memory-hard hash
is the brute-force defense. The same cost creates the oracle:
`exists=1` pays ~100-300ms, `exists=0` skips it. You cannot both "hash
only real users" and "leak nothing" without paying the cost on the miss
— and paying the cost on the miss is the known-but-rare fix (a dummy
hash on the `None` arm). The work-asymmetry is fundamental to the
KDF defense.

## The state-space leak

An auth system's response depends on account STATE —
`active`/`locked`/`pending`/`disabled`/`deleted`/`expired-password` —
not just `exists`. Each state is a different code path and a different
response. Even a "uniform" `exists=0` message may differ from every
`exists=1` state. The existence leaks through the state space — a
state-aware oracle enumerates each state.

## The side-channel theorem

When the response is a pure function `g(exists)` that returns a constant,
the SIDE EFFECTS still differ: `send_email(exists)`, `increment_counter
(exists)`, `write_audit(exists)`, `set_lock(exists)`. A "uniform" response
does not equalize the world — the send/lock/audit still fires
conditionally. The true oracle is the side-effect, not the response.

## The measurement as a hypothesis test

The oracle is a binary classifier: `H0: response|exists=0`, `H1:
response|exists=1`. The measurement is a hypothesis test — a repeated
sample where the two distributions differ on at least one channel. A
delta within noise fails to reject `H0` (unproven); a delta above noise
that tracks the username-class rejects `H0` (the oracle).

## The dual-bound on the loop

The same endpoint carries the dual question — is `f` rate-bounded? An
unbounded `f` makes any weak-credential attack feasible; the throttle
is the second property of the same function. The class measures both
because they are properties of one endpoint.

## Why coverage, not the headline

The `exists` oracle is a property of the account-touching FUNCTION, not
the URL — login, register, reset, check, mfa are different functions
with different oracles. The class is closed only when every function's
channels are measured — coverage, not the headline `/login`.
