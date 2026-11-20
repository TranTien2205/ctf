# Linux: Where the change is recorded

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

auditd `/var/log/audit/audit.log`  -  `type=SYSCALL` joined to `type=PATH name="/etc/cron.d/..."` on syscall number; `journalctl -u <unit>` for systemd; `CRON[` lines in `/var/log/syslog` (or `journalctl -u cron`) for cron firing. The mechanism record proves presence; these prove WHEN.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
