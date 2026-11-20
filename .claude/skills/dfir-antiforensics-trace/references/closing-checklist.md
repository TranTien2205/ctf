# Closing checklist

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Before reporting

- Clear-time vs intrusion-time distinguished in every timestamp cited.
- Every claim names artifact + field + verbatim row.
- Benign twins excluded (rotation/truncation/collection/reboot/attrib).
- Index values resolved; symbolic names read via message text where the
  docs are known-wrong (5013).
- Negatives quoted with the probe that produced them.

## Before closing

- Falsifier components quoted, not summarised.
- Recovery columns worked left-to-right, negatives recorded.
- Handoffs named: timestamps -> dfir-filesystem-timeline, persistence ->
  dfir-persistence-trace, execution -> dfir-execution-trace.
