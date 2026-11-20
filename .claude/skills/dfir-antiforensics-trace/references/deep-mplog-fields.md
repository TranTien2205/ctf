# Deep: MPLog field guide

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Lines are timestamped ISO: `DETECTION_ADD <threat> file:<path>`; `Engine:EMS scan|detection` rows carry `process:`, `pid:`, `sigseq=`; impact rows carry `ProcessImageName`, `TotalTime`, `Count`, `MaxTime`, `MaxTimeFile` (a path Defender touched — survives file deletion), `EstimatedImpact`; `OriginalFileName` exposes renames. `skills/ctf-forensics/windows.md:457-479` covers the DetectionHistory binaries.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
