# Linux: cron field discipline

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/var/spool/cron/crontabs/<user>`  -  command is field 6, NO user field (the file is per-user). `/etc/crontab` and `/etc/cron.d/*` carry a USER field before the command  -  `* * * * * root <cmd>`. Misreading field position on a /etc/crontab line names the user as the command (man 5 crontab, verified). `/etc/cron.{hourly,daily,weekly,monthly}` are run-parts DIRS  -  `ls -la` each.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
