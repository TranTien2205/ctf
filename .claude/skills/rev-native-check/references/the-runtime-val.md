# The run-time value — the unfalsifiable compare


A compare against a value computed at run time from unobservable
state (a random nonce, a time-seeded value, a hardware input) can't
be replicated — the check protects nothing you can forge.

## The route

Patch the jump, or find where the computed value is ALSO observable
(a leak, a seed).
