# Check-then-act pattern

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

Read-balance, check, debit - a multi-request flow where state can change between check and act is the race precondition. Source shows it in three lines; black-box shows it as a double-spend shape.

## The signal's falsifier

A signal that disappears on re-request, or appears for a different
reason than the hypothesis needs, closes this route - go back to the
table with the next-strongest signal.

## Pivot

Signal confirmed -> the probe-* module for the candidate class, or
the pair-* module separating its nearest neighbour.
