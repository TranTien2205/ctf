# Signature: `systemctl enable` shape

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`systemctl enable <unit>` creates the `.wants/` symlink  -  the symlink (not the unit) is what enables it; auditd on the symlink path, `journalctl -u systemd` for the reload.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
