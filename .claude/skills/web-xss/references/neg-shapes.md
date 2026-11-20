# Negative shapes - what a dead XSS looks like

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

- the reflection is output-encoded per context: `<` becomes
  `&lt;` verbatim in the body - the context is defended; try the
  OTHER contexts before closing (attribute, JS-string, DOM).
- the payload reflects only in the attacker's own session: self
  -XSS - no victim, no impact claim; recorded as scope, not a
  finding.
- the marker is stripped entirely: the sanitizer removes, not
  encodes - probe which byte sequences survive before calling it
  defended.
- CSP blocks execution while injection lands: the injection is
  proven, execution is not - the claim is 'injectable but
  blocked', with the CSP header quoted.

## Ledger lines

'context body: < encoded', 'context attr: " survives', 'bot: no
callback' - each context gets its own negative line; closing one
context does not close the parameter.

## Pivot

All contexts dead -> web-csrf (no script needed) or the self-XSS
scope note.
