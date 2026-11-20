# First probe: hosthdr

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

The cheapest request that discriminates `hosthdr` from its
nearest neighbours: one canary in X-Forwarded-Host and X-Original-URL. Confirmed by the canary appearing in generated links or ACL decisions.

## What the probe is for

It separates this class from the confusable classes the same signal
admits - it is a routing instrument, not an exploit. If it returns
the class's oracle, open `../../web-host-header/`; if not, the
route was wrong - return to the table.

## Falsifier

The response that closes this class - stated in the module body and
recorded as a proved negative when it fires.
