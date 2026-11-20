# Negative shapes - what a dead SSTI looks like

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

- the arithmetic marker renders literally: `{{7*7}}` in, `{{7*7}}`
  out - the value never reached the engine; recorded verbatim.
- the marker is stripped/encoded at input: the sanitizer names the
  boundary; try the alternate-context probes before closing.
- an error page names a DIFFERENT engine than guessed: the
  fingerprint was wrong, not the class - re-derive the engine.
- the engine evaluates only in a context you cannot reach (email
  template, admin render path): the injection point is proven but
  the render path is gated; that is a scope note, not a falsifier.

## Ledger lines

Each dead probe writes the marker sent, the verbatim response slice,
and which interpretation it killed - 'renders literal' closes the
parameter; 'engine is X not Y' re-arms it.

## Pivot

All contexts literal -> the class closes for this parameter; the next
parameter or the next class per decide.py.
