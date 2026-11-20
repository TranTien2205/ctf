# Linux: ld.so.preload

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/etc/ld.so.preload`  -  **measured absent on this box**: its mere existence is the finding; every dynamically-linked process loads what it names. Also `Environment=LD_PRELOAD=` inside a unit file  -  the scoped variant. `ldconfig`/glibc versions change resolution order; the file shape is the record.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
