# torch.save zip layout

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

A torch.save file is a zip: data.pkl (the opcodes) + data/storage blobs - the pkl inside carries the exec risk.

## Pivot

Module read -> the family file or class boundary it names.
