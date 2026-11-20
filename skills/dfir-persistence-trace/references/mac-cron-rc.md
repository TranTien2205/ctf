# macOS: macOS cron + rc.common

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

macOS still ships crontab and `rc.common`-era hooks  -  the same field discipline as `lnx-cron-fields`; launchd is the primary mechanism but cron survives.

## Evidence rule

Quote the plist key/value  -  `ProgramArguments` verbatim; a plist that
merely exists in LaunchAgents is a candidate until the command is read.

## Pivot

macOS quiet -> the question index (`q-*`) for the next family.
