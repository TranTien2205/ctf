# Field table: eventID / sharedEventID

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

eventID dedupes delivery; sharedEventID joins the two-account view of one call.

## Pivot

Field mapped -> the ev-* module for the call that carries it.
