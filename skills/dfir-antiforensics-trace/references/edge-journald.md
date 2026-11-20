# Edge: journald vacuuming vs tampering

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

systemd journal vacuums on size/time caps — 'missing early logs' on Linux is usually retention policy (`SystemMaxUse`, `MaxRetentionSec`). journald --file reads shipped journals; the config files in the bundle name the policy.

## Pivot

`corpus-index.md`; `meth-falsifier` when every shape is benign.
