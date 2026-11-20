# The SLA pressure

Method module for `ad-service-triage`. Attack-defense
service intake: find the flag store, the paths reaching it,
what the checker needs - in contest order, not jeopardy
order. Availability is scored; the flag rotates every tick.

Availability is scored continuously - every
change brackets against sla_check; an exploit
that DoSes your own service is a net loss.

## Exit

Named next step -> that module.
