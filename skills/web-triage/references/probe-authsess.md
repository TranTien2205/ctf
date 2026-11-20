# First probe: authsess

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

The cheapest request that discriminates `authsess` from its
nearest neighbours: decode the token completely (alg, kid, claims) before any modification. The first probe is the decode; the second is the alg/key family the decode names.

## What the probe is for

It separates this class from the confusable classes the same signal
admits - it is a routing instrument, not an exploit. If it returns
the class's oracle, open `../../web-auth-session/`; if not, the
route was wrong - return to the table.

## Falsifier

The response that closes this class - stated in the module body and
recorded as a proved negative when it fires.
