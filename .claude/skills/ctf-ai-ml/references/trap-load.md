# Trap: loading before inspecting

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

torch.load/pickle.load executes the file - inspect opcodes (pickle) or parse the header (safetensors/onnx) before any load call.

## Pivot

Module read -> the family file or class boundary it names.
