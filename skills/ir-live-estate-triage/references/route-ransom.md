# Route: ransomware shape

Routing module for `ir-live-estate-triage`. A live estate
already hit: services down, encrypted files, a note, a clock.
The router bounds the intake so evidence survives, then routes
to one dfir-* class.

Encrypted files + note -> antiforensics-trace (what
was destroyed/erased) + persistence-trace (how it
stayed) + execution-trace (what ran).

## Pivot

Signal named -> its sig-* module; evidence safe -> route-*.
