# Trap: Tool-specific output formats

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

chainsaw `hunt -s <sigma>` REQUIRES `--mapping` and renders UTC by default; hayabusa is `dfir-timeline -t csv|json|jsonl -d <dir> -o <out>`, `--iso-8601` lowercase, LOCAL time unless `-U`. Absent here, but the traps are documented for the day they are installed.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
