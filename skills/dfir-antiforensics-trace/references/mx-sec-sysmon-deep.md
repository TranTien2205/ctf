# Deep: mx-sec-sysmon

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sysmon survives a Security clear because it is a different channel with its own log file — clearing Security writes a 1102 there and leaves Sysmon/Operational untouched. The process story during the lost window is therefore intact unless Sysmon was separately killed (check evt-sysmon4/16 for that half).

## Evidence rule

The survivor's own row is the quote; this card only explains why it survives.

## Pivot

Next column in the parent `rec-*` module.
