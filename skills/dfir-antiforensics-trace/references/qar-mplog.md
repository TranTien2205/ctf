# Quarantine/MPLog: MPLog-*.log — the survivor

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`C:\ProgramData\Microsoft\Windows Defender\Support\MPLog-*.log` survives a Security clear. Grep `DETECTION_ADD` — '2021-07-22T15:38:04.557Z DETECTION_ADD Ransom:Win32/Conti.ZA file:C:\ProgramData\badfile.exe'; `Engine:EMS scan`/`Engine:EMS detection` carrying `process:`, `pid:`, `sigseq=`; impact rows `ProcessImageName`, `TotalTime`, `Count`, `MaxTime`, `MaxTimeFile`, `EstimatedImpact` — `MaxTimeFile` names a path Defender touched and OUTLIVES the file (CrowdStrike, MPLog). `OriginalFileName` exposes a renamed executable.

## Evidence rule

A carved quarantine payload needs its own record: the decryption was run,
the carved offset named, and the hash computed from the carved bytes — quote
the hash output line.

## Pivot

Quarantine empty -> MPLog still names paths Defender touched; then 1116/1117
events if the channel survived.
