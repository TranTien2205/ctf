# Pickle RCE chain

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

Challenge supplies a loader endpoint or a crafted .pkl asks you to build it - the reduce chain is (module, callable, args) built from the target's own imports.

## Pivot

Module read -> the family file or class boundary it names.
