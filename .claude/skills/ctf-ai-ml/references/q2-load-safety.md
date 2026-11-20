# Question: is it safe to load

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself.

The format's exec surface: pickle opcodes run, safetensors/onnx headers don't - pickletools or fickling decides before any load call.

## Pivot

Module read -> the family file or class boundary it names.
