# Defender: Defender 5001/5010/5012 — protection off

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`..._RTP_DISABLED` / `..._ANTISPYWARE_DISABLED` / `..._ANTIVIRUS_DISABLED`. No data fields — the MESSAGE TEXT is the whole answer and the three differ: 5001 'Real-time protection is disabled', 5010 'Scanning for malware and other potentially unwanted software is disabled', 5012 'Scanning for viruses is disabled'. Which one fired says which switch was thrown.

## Evidence rule

Defender events carry few fields — quote the message text and the event id
together; the symbolic name is documentation, the message is the record.

## Pivot

Defender channel empty -> MPLog + quarantine (`qar-*`) still hold the
evidence; exclusions still live in the hive.
