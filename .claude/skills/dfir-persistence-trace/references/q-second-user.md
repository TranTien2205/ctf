# Question: Question: persistence under another user

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Per-user mechanisms live in NTUSER.DAT, Startup folder, HKCU Classes COM, `~/.config/systemd/user`, `~/.config/autostart`  -  enumerating only the admin/SYSTEM scope misses them. Every NTUSER.DAT in the bundle, not just the analyst's account.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.
