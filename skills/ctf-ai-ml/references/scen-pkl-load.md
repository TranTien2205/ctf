# Scenario: pickle load RCE

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

Challenge loads a supplied .pkl - inspect the loader's allowed ops first, build the GLOBAL+REDUCE chain inside them, verify the exec against the verbatim response.

## Pivot

Module read -> the family file or class boundary it names.
