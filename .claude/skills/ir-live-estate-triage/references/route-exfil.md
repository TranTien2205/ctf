# Route: data-taken shape

Routing module for `ir-live-estate-triage`. A live estate
already hit: services down, encrypted files, a note, a clock.
The router bounds the intake so evidence survives, then routes
to one dfir-* class.

Evidence of bulk reads + outbound volume ->
network-exfil-trace for the channel + filesystem
for what was touched.

## Pivot

Signal named -> its sig-* module; evidence safe -> route-*.
