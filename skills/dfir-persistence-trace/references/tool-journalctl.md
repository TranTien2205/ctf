# Tool route: journalctl/grep for Linux

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`journalctl -u <unit> --no-pager` on a live-rootfs journal, or grep the shipped `journal/` files; `grep -F '/etc/cron.d' /var/log/audit/audit.log` for the change record.

## Evidence rule

Tool output is the excerpt to quote; the record field inside it is the
evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
