# Phase: what the checker needs

Method module for `ad-service-triage`. Attack-defense
service intake: find the flag store, the paths reaching it,
what the checker needs - in contest order, not jeopardy
order. Availability is scored; the flag rotates every tick.

The checker's requests must keep passing - read
them: endpoints, credentials, timing, response
shape. Breaking one costs the availability score.

## Exit

Named next step -> that module.
