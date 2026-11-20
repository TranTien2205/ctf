# Tokenizer internals

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

The tokenizer's vocab and merges sometimes hide a planted token - the special-tokens list and unused IDs are the check.

## Pivot

Module read -> the family file or class boundary it names.
