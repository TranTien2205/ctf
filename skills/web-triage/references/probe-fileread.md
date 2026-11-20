# First probe: fileread

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

The cheapest request that discriminates `fileread` from its
nearest neighbours: an absolute path to a known-readable file first (/etc/passwd, the app's own file), traversal second. Confirmed by file bytes; a 400 says the check, not the class, is wrong.

## What the probe is for

It separates this class from the confusable classes the same signal
admits - it is a routing instrument, not an exploit. If it returns
the class's oracle, open `../../file-read-primitives/`; if not, the
route was wrong - return to the table.

## Falsifier

The response that closes this class - stated in the module body and
recorded as a proved negative when it fires.
