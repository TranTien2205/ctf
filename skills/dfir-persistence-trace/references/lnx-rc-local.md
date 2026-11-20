# Linux: SysV and xdg

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/etc/rc.local` (needs the rc-local service present), `/etc/init.d/*` with `/etc/rc?.d/S*` symlinks (S## ordering = boot order), `/etc/xdg/autostart/*.desktop` + `~/.config/autostart/*.desktop`  -  `Exec=` is the command line.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
