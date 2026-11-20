# Class boundary

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

This class answers 'the app enforced its rules correctly and the
rules themselves were wrong' - an invariant the developers assumed
never checked. It does not answer: a missing authorization check
(idor), a parser disagreement (parser-differential), a mass-assigned
field (mass-assignment), or a concurrency window (race-condition).
The logic-flaw signature is a step skipped, replayed, reordered or
negative-valued that the code ACCEPTED.

## The one-sentence test

No parser was fooled, no type was confused - the request was legal by
every rule the app enforced, and the outcome is still impossible in
the business model.

## Pivot

Boundary applies -> route to the sibling, do not stretch the claim.
