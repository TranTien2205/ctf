# Trap: load-order exec

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself.

The exec happens at LOAD, before your code inspects the result - the inspection must precede the load entirely, not follow it.

## Pivot

Module read -> the family file or class boundary it names.
