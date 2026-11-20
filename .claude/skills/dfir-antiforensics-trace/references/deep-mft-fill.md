# Deep: sdelete -c MFT-fill fingerprint

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Free-space clean: 'must also fill any existing free portions of the NTFS MFT with files that fit within an MFT record' — the signature is an $MFT full of many tiny equal-sized records created in a burst. Check the record-created times clustering to date the wipe.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
