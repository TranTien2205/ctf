# First probe: sqli

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

The cheapest request that discriminates `sqli` from its
nearest neighbours: one syntax marker (a lone quote) then a true/false pair (AND 1=1 vs AND 1=2 shapes). Confirmed by a boolean or error delta; a bare 200 is inconclusive.

## What the probe is for

It separates this class from the confusable classes the same signal
admits - it is a routing instrument, not an exploit. If it returns
the class's oracle, open `../../web-sqli/`; if not, the
route was wrong - return to the table.

## Falsifier

The response that closes this class - stated in the module body and
recorded as a proved negative when it fires.
