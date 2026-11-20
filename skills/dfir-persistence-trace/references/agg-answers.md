# Aggregator: Question-to-module map

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

'maintain access' -> q-maintain-access; 'what runs at startup' -> q-startup-runs; 'name the service/task' -> q-name-service; 'which registry key' -> q-registry-key; 'binary at logon' -> q-binary-at-logon; 'who created' -> q-who-created; 'when ran' -> q-when-run; 'survive reboot' -> q-survive-reboot; 'what command' -> q-what-command; 'deleted task' -> q-deleted-task; 'other user' -> q-second-user; 'persist vs ran' -> q-lateral-vs-local.

## Use

An index  -  open the named family module for the artifact detail; this
file only decides which one.

## Pivot

Index consulted -> the module it names.

## Cross-check

The module is one line in the sweep; the claim it feeds still needs
the verbatim record and the paired timestamps before it counts.
