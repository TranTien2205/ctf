# Trap: quantized weights

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself. A technique name is routing information, not a
finding.

int8/int4 weights perturb nonlinearly - the same delta isn't the same effect; dequantize first, perturb, requantize.

## Pivot

Module read -> the family file or class boundary it names.
