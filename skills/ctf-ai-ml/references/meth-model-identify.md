# Model file identification

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

file + the format tells: pickle (opcodes), torch.save zip, safetensors header JSON, onnx protobuf, TF SavedModel dir, joblib. The format decides the safe-load path AND the attack surface.

## Pivot

Module read -> the family file or class boundary it names.
