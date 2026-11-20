# Persistence misc: Alternative shell/value checks

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Beyond `Shell`/`Userinit`: SYSTEM `<set>\Control\Session Manager\KnownDLLs` (a planted same-name DLL shadows the listed one), `SvchostSplitThresholdInKB`-style tuning values that alter svchost grouping, `BootVerificationProgram` `ImagePath`/`GlobalFlag` (a boot-verification launcher; UNVERIFIED prevalence here).

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
