# Deep: mx-sec-usn

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

$J 0x100 (data overwrite/extend) and 0x200 (delete) records survive log clears because the journal is a filesystem structure — file-level operations during the lost window are recoverable from it until it wraps or is itself deleted.

## Evidence rule

The survivor's own row is the quote; this card only explains why it survives.

## Pivot

Next column in the parent `rec-*` module.
