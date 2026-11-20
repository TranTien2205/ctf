# Deep: The USN-0 volume signature

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`fsutil usn deletejournal` must walk the MFT and zero every record's last-USN field (Microsoft's own remark). So a volume where EVERY MFT record carries USN 0 was journal-deleted; a wrapped journal keeps current USNs with only the journal's own bounds moved. The MFT-wide read is the discriminator.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
