# Linux: authorized_keys

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`~/.ssh/authorized_keys` and `authorized_keys2`  -  the key COMMENT often names the operator/tooling. Options field before the key (`from=`, `command=`, `no-pty`) narrows what the key does  -  a `command=` option runs that on every key auth. Check every user's home, and `~root` explicitly.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
