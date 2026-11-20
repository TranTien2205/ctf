# Module: Artifact: IFEO key layout

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`Image File Execution Options\<exe>`  -  Debugger (redirect), GlobalFlag bitmask, VerifierDlls, UseFilter+FilterFullPath (conditional debugger on matching path  -  the quieter variant), MinimumStackCommitInBytes, CpuPriorityClass. Per-EXE key, so the enum step lists which exes carry any.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
