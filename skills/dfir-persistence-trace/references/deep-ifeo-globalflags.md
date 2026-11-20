# Deep dive: Deep: IFEO GlobalFlag bits

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`GlobalFlag` under an IFEO key is a bitmask the OS reads: 0x100 FLG_APPLICATION_VERIFIER (VerifierDlls route), 0x200 FLG_MONITOR_SILENT_PROCESS_EXIT (SilentProcessExit route). The flag's presence decides which sibling mechanism is armed  -  read it, not just Debugger.

## Use

Depth for when the row-level module is not enough  -  cite this file's
artifact and offset when the claim rests on the decoded detail.

## Pivot

Deep read done -> back to the scenario (`scen-*`) or the matrix.
