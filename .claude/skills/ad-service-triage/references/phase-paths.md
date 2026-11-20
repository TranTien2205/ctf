# Phase: paths to the store

Method module for `ad-service-triage`. Attack-defense
service intake: find the flag store, the paths reaching it,
what the checker needs - in contest order, not jeopardy
order. Availability is scored; the flag rotates every tick.

Every code path that reads or writes the flag
store - legit checker path vs attacker-reachable
path. The difference is the bug.

## Exit

Named next step -> that module.
