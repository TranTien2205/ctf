# Module: Artifact: SilentProcessExit layout

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`SilentProcessExit\<exe>`: ReportingMode (1 launch monitor / 2 dump / 4 notify), MonitorProcess (the payload, %e/%i substitution), MonitorCommandLine, DumpFolder, DumpType, LocalDump  -  needs the IFEO GlobalFlag 0x200 twin to arm.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
