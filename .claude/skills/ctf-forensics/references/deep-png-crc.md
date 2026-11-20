# Deep: PNG CRC repair

Depth module for `ctf-forensics`. Open `../SKILL.md` for the
shared-file index first; this file is one named piece of the corpus -
never a finding by itself.

A chunk's stored CRC vs computed CRC mismatch names the tampered chunk; fixing length/type/data+CRC per the chunk layout restores parsing - the CRC32 is over type+data only.

## Pivot

Module read -> the technique file or class skill it names.
