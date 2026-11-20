# Deep dive: Deep: DynamicInfo semantics

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

magic 0x3 (version), ftCreate = registration FILETIME, ftLastRun = last trigger fire (a DISABLED task stops updating it  -  a frozen ftLastRun + enabled key is the 'disabled once' shape), dwTaskState (0=success-ish, task-state constants vary  -  the DWORD is recorded verbatim, the enum table is UNVERIFIED here), dwLastErrorCode = the last run's result, ftLastSuccessfulRun post-7 only.

## Use

Depth for when the row-level module is not enough  -  cite this file's
artifact and offset when the claim rests on the decoded detail.

## Pivot

Deep read done -> back to the scenario (`scen-*`) or the matrix.
