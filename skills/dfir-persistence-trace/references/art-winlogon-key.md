# Module: Artifact: Winlogon key

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`Microsoft\Windows NT\CurrentVersion\Winlogon`  -  Shell (explorer.exe), Userinit (userinit.exe,), plus Notify (stale post-Vista), GinaDLL (XP-only), Taskman, System, VmApplet. Each non-default value is a loader override; quote the whole value string including commas.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
