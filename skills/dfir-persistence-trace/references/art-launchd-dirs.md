# Module: Artifact: launchd dir set

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Four scopes again: /Library/LaunchDaemons (root@boot), /Library/LaunchAgents (all users@login), ~/Library/LaunchAgents, /System/Library/* (Apple)  -  plus overrides in /private/var/db/com.apple.xpc.launchd/disabled*.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
