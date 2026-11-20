# Class boundary - what XSS is not

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

XSS is a request value reaching a browser-executable context
with a viewer that renders it. It is NOT: SSTI (server-side
evaluation - the marker evaluates before the browser sees it),
CSRF (no script needed - the request itself is the payload),
HTML-injection-without-script (content injection, weaker - still
worth a report at its own grade), or self-XSS (payload only fires in
the attacker's own session - no victim, no impact claim).

## Evidence chain

1. Context: where the reflection lands (body / attribute / JS
   string / DOM sink) decides the payload grammar.
2. Sanitizer boundary: which bytes/sequences the app strips or
   encodes - measured per-context, not assumed.
3. Execution: the proof is the bot-visible marker or the exfil
   record - a payload that merely RENDERS is a candidate.

## Pivot

Boundary applies -> web-csrf (no script needed), web-ssti
(server-side), or the self-XSS caveat (no viewer).
