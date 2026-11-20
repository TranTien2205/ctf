# macOS: emond and periodic

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/etc/emond.d/rules/*.plist`  -  the event-monitor persistence (rare but real; a rule's `command` action is the payload); `/etc/periodic/` scripts run by the periodic machinery on older macs.

## Evidence rule

Quote the plist key/value  -  `ProgramArguments` verbatim; a plist that
merely exists in LaunchAgents is a candidate until the command is read.

## Pivot

macOS quiet -> the question index (`q-*`) for the next family.
