# Module: Artifact: .wants symlinks

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/etc/systemd/system/<target>.wants/<unit>` symlinks are what `systemctl enable` writes  -  the UNIT can exist without being enabled; enumerate symlinks, not just unit files.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
