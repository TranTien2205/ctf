# Stego channel enumeration

Depth module for `ctf-forensics`. Open `../SKILL.md` for the
shared-file index first; this file is one named piece of the corpus -
never a finding by itself.

Per carrier: image (LSB bit-planes, palette, EXIF, appended data), audio (LSB, spectrogram, phase, echo), document (white text, metadata, hidden streams), container (slack, alternate streams) - each channel gets its own check.

## Pivot

Module read -> the shared file or class skill it names.
