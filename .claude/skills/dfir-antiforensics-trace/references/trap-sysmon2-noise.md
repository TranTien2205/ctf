# Trap: Sysmon 2 fires legitimately

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Installers and archivers rewrite creation times constantly — Microsoft: 'it does not necessarily indicate malicious activity'. Require Previous/Creation divergence PLUS context ($FN divergence, odd process, odd path) before calling timestomp.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
