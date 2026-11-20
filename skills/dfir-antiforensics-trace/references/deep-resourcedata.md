# Deep: ResourceData inner structure

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

After RC4: [security descriptor][8-byte length][original bytes], original at bsd+0x14, wrapped in WIN32_STREAM_ID records so ADS streams (Zone.Identifier!) survive. Carve the length-prefixed region, hash it — the hash answers 'what was the deleted file' without any surviving copy on the volume.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
