# Timestomp: $STANDARD_INFORMATION vs $FILE_NAME

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Two timestamp sets per MFT FILE record: `$SI` (attr 0x10, user-writable via SetFileTime) and `$FN` (attr 0x30, kernel-maintained, updated only on rename/move). Stomping rewrites $SI but typically leaves $FN real — the DIVERGENCE is the proof. `FILE` record is 1024 bytes; `skills/ctf-forensics/windows.md:294-316` carries the layout; the split bodyfile row and column order `MD5|path|inode-type-id|mode|UID|GID|size|atime|mtime|ctime|crtime` are at `../dfir-filesystem-timeline/SKILL.md:145-148`.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
