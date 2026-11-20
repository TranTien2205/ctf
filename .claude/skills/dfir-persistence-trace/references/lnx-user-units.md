# Linux: systemd user units

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`~/.config/systemd/user/` beats `/etc/systemd/user/` beats `~/.local/share/systemd/user/` beats `/usr/lib/systemd/user/`  -  same grep over those four. `loginctl enable-linger` keeps user services running without a session.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
