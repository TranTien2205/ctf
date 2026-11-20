# Route: fld-dns-count-answers

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The field module is `fld-dns-count-answers.md`; this card answers where its reading feeds next.

## Primary question

`q-what-inside-dns.md` — the question this field most often answers.

## Supporting context

`chan-dns-inbound.md` — the channel/method/trap context that constrains how this field may be quoted.

## Direction check

Before reporting: which side sent it, over what window, wire or payload units. If the field's row cannot be quoted verbatim, the answer it feeds is not ready.

## Pivot

Field produced nothing usable after the filter shapes listed in its own module -> change artifact family per `../SKILL.md` Discipline.
