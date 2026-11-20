# RF analysis flow

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Capture format (IQ/WAV/raw) -> demod candidate from the constellation -> symbol-rate estimate -> framing -> bit decode - each stage's output is the next stage's input.

## Pivot

Module read -> the shared file or class skill it names.
