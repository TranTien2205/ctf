# Attack shapes by store

Method module for `ad-service-triage`. Attack-defense
service intake: find the flag store, the paths reaching it,
what the checker needs - in contest order, not jeopardy
order. Availability is scored; the flag rotates every tick.

Injection reaching the table, LFI reaching the
file, IDOR reaching the field, SSRF reaching the
queue - the store type names the likely class.

## Exit

Named next step -> that module.
