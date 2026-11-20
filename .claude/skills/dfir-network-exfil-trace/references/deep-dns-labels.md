# Deep: DNS label arithmetic

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

63 bytes max per label, 253 total name. A 4-label name of ~50-char labels carries ~200 bytes/query minus encoding overhead (~75% for base32). Exfil rate = queries/sec x bytes/query — a 3/s query rate at 150 bytes/query is ~450 B/s, matching the measured fixture scale. This arithmetic bounds plausible volume for a claimed DNS channel.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
