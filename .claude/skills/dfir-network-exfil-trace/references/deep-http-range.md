# Deep: Range and chunked transfers

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`Range:`/`Content-Range` split a download or upload into pieces — sum `content_range.total` or the per-part lengths for true size. Chunked transfer-encoding has no content_length; the reassembled export is the only honest size.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
