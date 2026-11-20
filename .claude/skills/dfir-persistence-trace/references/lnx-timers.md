# Linux: systemd timers

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`*.timer` beside the unit  -  `OnCalendar=`/`OnBootSec=`/`OnUnitActiveSec=` schedule, `Unit=` names what fires. `grep -rHE 'OnCalendar|OnBootSec|^Unit=' --include='*.timer' /etc /usr/lib`. A timer + unit pair is the cron-equivalent shape.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
