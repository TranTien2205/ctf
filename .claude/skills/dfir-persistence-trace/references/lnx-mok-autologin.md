# Linux: Display-manager autologin/session

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/etc/lightdm/lightdm.conf` `autologin-user`, `/etc/gdm3/daemon.conf` `AutomaticLogin`, `/etc/xdg/` session files  -  a changed login config that silently adds a user/session is persistence at the console layer; check the files exist before citing them.

## Evidence rule

Quote the file's line verbatim  -  a unit name alone is surface; the
`ExecStart=`/`Exec=`/crontab line is the record.

## Pivot

Linux clean -> macOS (`mac-*`) or back to the service/task families.
