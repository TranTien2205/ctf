# Linux: Shell rc files

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`~/.bashrc`, `~/.bash_profile`, `~/.profile`, `~/.bash_logout` (fires at LOGOUT  -  the anti-forensics-shaped rc), `/etc/profile`, `/etc/profile.d/*.sh`. `grep -rn 'curl\|wget\|base64\|/dev/tcp' <those paths>` is the fast triage.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
