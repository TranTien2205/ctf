# Aggregator: Question-to-module map

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

'first acted' -> q-first-action; 'who' -> q-who; 'which key' -> q-what-key; 'what created' -> q-what-created; 'secret read' -> q-secret-read; 'bucket' -> q-bucket; 'what left' -> q-exfil-what; 'console' -> q-console; 'MFA' -> q-mfa; 'logging tampered' -> q-disable-log; 'privesc' -> q-privesc; 'persistence' -> q-persistence; 'lateral' -> q-lateral; 'which region' -> q-region-scope.

## Use

An index - open the named family module for the detail; this file
only decides which one.

## Pivot

Index consulted -> the module it names.
