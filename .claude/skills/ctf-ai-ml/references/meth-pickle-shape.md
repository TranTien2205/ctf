# Pickle attack shape

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

A .pkl executes opcodes at LOAD time - malicious GLOBAL/REDUCE opcodes run arbitrary callables. Detection: disassemble the opcode stream (pickletools) before any load; exploitation: the challenge's own load is the sink.

## Pivot

Module read -> the family file or class boundary it names.
