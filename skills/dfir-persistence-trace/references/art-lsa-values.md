# Module: Artifact: LSA package values

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SYSTEM `<set>\Control\Lsa`: Security Packages / Authentication Packages / Notification Packages (multi-strings naming System32 DLLs); `Lsa\OSConfig` mirrors; `Lsa\Audit` for audit config; a foreign package name in any is the persistence AND credential-access overlap.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
