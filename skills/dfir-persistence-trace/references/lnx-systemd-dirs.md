# Linux: systemd unit search order

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/etc/systemd/system/` beats `/run/systemd/system/` beats `/usr/local/lib/systemd/system/` beats `/usr/lib/systemd/system/` (`man 5 systemd.unit`, verified). `.d/*.conf` drop-ins merge  -  a drop-in `ExecStartPost=` under `/etc/systemd/system/<unit>.d/` is the quieter persistence. Grep: `grep -rHE '^(ExecStart|ExecStartPre|Environment)='` over the dirs.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
