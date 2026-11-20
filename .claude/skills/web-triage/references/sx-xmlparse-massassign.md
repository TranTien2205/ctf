# Signal cell: xml-parse / massassign

Routing module for `web-triage`. This file discriminates - it says which bug class a signal raises and which probe separates the candidates. It never proves a class; proof belongs to the depth skill the route names.

Whether the `xml-parse` signal raises or rules out `massassign`.

## Read

Map the observed signal's strength against this class: does this
signal ever appear when this class is the bug, and does its absence
close the class? Strong-raise, weak-raise, neutral, or rules-out -
state which, with the one-line reason.

## Route

If strong-raise: `probe-massassign` names the discriminating
request, then `../../web-mass-assignment/` owns the depth. If
rules-out: the observation closes this class for this challenge;
record it and move to the next-strongest signal's row.
