# Defender: Exclusion keys — local vs policy

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Local writes (Add-MpPreference, Set-MpPreference, the API, a direct registry write) land under `HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions\{Paths,Extensions,Processes}`; policy pushes land under `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Exclusions\` with the same three subkeys. Scrutinise the NON-POLICY key first — the path tells who set it.

## Evidence rule

Defender events carry few fields — quote the message text and the event id
together; the symbolic name is documentation, the message is the record.

## Pivot

Defender channel empty -> MPLog + quarantine (`qar-*`) still hold the
evidence; exclusions still live in the hive.
