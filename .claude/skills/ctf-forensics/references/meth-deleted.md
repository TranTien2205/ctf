# Deleted-file recovery

Depth module for `ctf-forensics`. Open `../SKILL.md` for the
shared-file index first; this file is one named piece of the corpus -
never a finding by itself.

Filesystem layer decides: ext unallocated+journal, NTFS $MFT remnants+$J, FAT root-dir remnants, plus container-level (recycle-bin, backups, snapshots) - the disk-image class skill carries the layouts.

## Pivot

Module read -> the shared file or class skill it names.
