# Event: Clear-command signatures

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Hunt in Sysmon 1 / 4688 / PowerShell 4104 CommandLine: `wevtutil cl Security` (any channel name), `wevtutil sl ... /ca:` (ACL change), `Clear-EventLog -LogName`, `Remove-EventLog`, `auditpol /clear /y` ('Deletes the per-user audit policy for all users, resets (disables) the system audit policy for all subcategories' - Microsoft Learn, auditpol clear), `sc config eventlog start=disabled`, `Set-Service -Name EventLog -Status Stopped`. ATT&CK T1070.001 / T1562.002.

## Query shape

```bash
python3 tools/forensics/evtx_query.py --input <channel>.jsonl \
  --event-id <id> --challenge <name> --class dfir-antiforensics-trace \
  --hypothesis-id h1 --evidence-kind class [--answer FIELD]
```

## Evidence rule

Quote the event id, channel, timestamp, and the answering field verbatim.
A clear-time timestamp answers 'when was it cleared' — never 'when did the
intrusion start'.

## Pivot

Clear/disable events clean -> the deletion/timestomp families; all clean ->
the falsifier block in `../SKILL.md`.
