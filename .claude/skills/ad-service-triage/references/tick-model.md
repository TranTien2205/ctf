# The tick model

Method module for `ad-service-triage`. Attack-defense
service intake: find the flag store, the paths reaching it,
what the checker needs - in contest order, not jeopardy
order. Availability is scored; the flag rotates every tick.

Flag rotates every tick (~minutes) - an exploit
grabs this tick's flag, a patch protects NEXT
tick. Stealing an old flag scores zero.

## Exit

Named next step -> that module.
