# Deep: IP fragmentation

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`ip.flags.mf==1`/`ip.frag_offset>0` fragments reassemble before dissection; counting `frame.len` counts them once each (fine) but counting PDU-level fields double-counts where the dissector reassembled — check `ip.fragment` overlap fields on weird sums.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
