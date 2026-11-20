# Deep: Beyond -z credentials

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

For protocols the tap misses: `-Y 'http.authorization'` for Basic headers, `ftp.request.command=="PASS"`, `imf`/`smtp` AUTH lines, SNMP `snmp.community`. Each is a quoted field, same rule.

## Evidence rule

The deep card refines interpretation; the quotable row still comes from the base question's own probe.

## Pivot

`q-cleartext-creds.md` for the procedure; `meth-answer-shape` for the reporting checklist.
