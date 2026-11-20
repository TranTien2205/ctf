# Method: Dating the hole

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A record-id gap (4200,4310) dates itself only through neighbours: the timestamps of records 4199 and 4311 bound when deletion happened. The gap is never itself a timestamp.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
