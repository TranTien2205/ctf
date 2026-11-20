# Linux: at jobs and anacron

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/var/spool/cron/atjobs/` (pending at jobs  -  a deferred one-shot that resurfaces), `atq`/`at -c <id>` for content on a live box; `/etc/anacrontab` on systems with anacron  -  `period delay job-id command`, fires jobs missed while powered off.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
