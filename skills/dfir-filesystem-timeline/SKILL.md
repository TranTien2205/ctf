---
name: dfir-filesystem-timeline
description: >
  Action-oriented depth skill for Filesystem metadata timeline. Use after the router or tools/classify.py
  names this class; start with the first probe and record the expected signal. Do not use it as proof of a
  finding. Confusable classes: dfir-antiforensics-trace, dfir-execution-trace. Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, ntfs, timeline, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Filesystem metadata timeline

**Catalogue class.** This toolkit has never solved one. What follows is standard published
knowledge, not local experience - record what actually happens in `field-notes.md`.

## First probe
```bash
fls -o <part_offset> -m C: -r image.dd > body.txt    # bodyfile: BOTH timestamp sets
mactime -y -d -b body.txt | grep -i '<name_from_the_question>'
```

Expected signal, measured 2026-09-27 23:21 EDT (03:21Z) on a 16 MB `mkntfs -F` image whose inode 4 had its
`$STANDARD_INFORMATION` Created and Modified FILETIME patched to 2001-01-01 - three rows for one inode,
and the split is the answer:
```text
2001-01-01T00:00:00Z,2560,m..b,r/rr-xr-xr-x,48,0,4-128-1,"C:/$AttrDef"
2026-09-28T03:21:25Z,2560,.ac.,r/rr-xr-xr-x,48,0,4-128-1,"C:/$AttrDef"
2026-09-28T03:21:25Z,82,macb,r/rr-xr-xr-x,48,0,4-48-2,"C:/$AttrDef ($FILE_NAME)"
```
**Falsifier** - the observation that closes this class: `tools/forensics/artifact_inventory.py
--path <dir> --challenge <c>` reports no `mft`, `usn-journal` or `recycle-bin` family and there is
no image and no bodyfile, so ordering can only come from the event-log or registry families.

## Recognise and confirm

The question names a file and asks *when*, or asks for an order - created, modified, renamed, moved,
deleted, first seen, "how many seconds between"; *who ran it* is `../dfir-execution-trace/`.
`artifact_inventory.py` detects `$MFT` by name and by record header - `FILE` or `BAAD` at offset 0 plus
an update-sequence-array offset of 0x10..0x40 at offset 4 (`looks_like_mft_record`). Then fix the clock: measured on
one inode, `mactime -y` rendered `2026-09-28T04:50:26Z` where `istat` printed `2026-09-28 00:50:26 (EDT)`
for the same record - `-y` is UTC, `istat` is host-local; mactime.1 says `-z` and `-m` do not work with `-y`.

## $MFT record layout, and the 4+4 timestamps

| Field | Where | Measured on the test volume |
|---|---|---|
| Signature | offset 0, 4 bytes | `FILE`; `BAAD` = the driver failed the fixup |
| Update-sequence-array offset | `uint16` at 4 | 0x0030 |
| Update-sequence-array count | `uint16` at 6 | 3 (one USN plus two sector-end fixups) |
| First attribute offset | `uint16` at 0x14 | 0x0038 |
| Allocated size | `uint32` at 0x1C | 1024 - but read it from `fsstat` ("Size of MFT Entries: 1024 bytes"), never assume |

The last two bytes of every 512-byte sector inside a record are replaced by the update sequence number
and the originals kept in the array, so a parser reading a field straddling 0x1FE or 0x3FE without
reversing the fixup reads the USN, not the data. Attribute type codes read off `istat`:
`$STANDARD_INFORMATION` 16 (0x10), `$FILE_NAME` 48 (0x30), `$SECURITY_DESCRIPTOR` 80 (0x50), `$DATA`
128 (0x80), `$INDEX_ROOT` 144 (0x90). 0x10 and 0x30 each carry the same four FILETIMEs in the
same order - Created, File Modified, MFT Modified, Accessed - the 4+4 model; backdating utilities
write only 0x10, because 0x30 is maintained by the driver from the directory index. **The divergence
that proves a backdate is one inode showing different values in its `($FILE_NAME)` row and its plain
row** (`../ctf-forensics/windows.md:294-316`).

## $J: USN_RECORD_V2 and the full reason table

On disk the journal is an alternate data stream, `\$Extend\$UsnJrnl:$J`, with `:$Max` holding the
configured size; `fls -r -p` prints it in colon notation. Offsets (Microsoft Learn, USN_RECORD_V2):
RecordLength 0, MajorVersion 4 (must be 2), MinorVersion 6, FileReferenceNumber 8,
ParentFileReferenceNumber 16, Usn 24, TimeStamp 32 (FILETIME, UTC), Reason 40, SourceInfo 44,
SecurityId 48, FileAttributes 52, FileNameLength 56, FileNameOffset 58, FileName 60. The stdlib `parse_usn_record` at
`../ctf-forensics/windows.md:327-341` reads nine of them; add MinorVersion 6, Usn 24, SourceInfo 44 and SecurityId 48 when the question asks about USN order or source.

| Flag | Name | Flag | Name | Flag | Name | Flag | Name |
|---|---|---|---|---|---|---|---|
| 0x00000001 | DATA_OVERWRITE | 0x00000040 | NAMED_DATA_TRUNCATION | 0x00002000 | RENAME_NEW_NAME | 0x00080000 | OBJECT_ID_CHANGE |
| 0x00000002 | DATA_EXTEND | 0x00000100 | FILE_CREATE | 0x00004000 | INDEXABLE_CHANGE | 0x00100000 | REPARSE_POINT_CHANGE |
| 0x00000004 | DATA_TRUNCATION | 0x00000200 | FILE_DELETE | 0x00008000 | BASIC_INFO_CHANGE | 0x00200000 | STREAM_CHANGE |
| 0x00000010 | NAMED_DATA_OVERWRITE | 0x00000400 | EA_CHANGE | 0x00010000 | HARD_LINK_CHANGE | 0x00400000 | TRANSACTED_CHANGE |
| 0x00000020 | NAMED_DATA_EXTEND | 0x00000800 | SECURITY_CHANGE | 0x00020000 | COMPRESSION_CHANGE | 0x00800000 | INTEGRITY_CHANGE |
| | | 0x00001000 | RENAME_OLD_NAME | 0x00040000 | ENCRYPTION_CHANGE | 0x80000000 | CLOSE |

0x100 is first existence and survives log clearing; 0x200 is deletion whether or not the Recycle Bin
was used; 0x2 repeated on one file is one append per command, which dates each line of a history
file; 0x8000 fires when a timestamp is *set*, so it is the backdating fingerprint. A rename or move
emits **two** records - 0x1000 with the old name, 0x2000 with the new - sharing one FileReferenceNumber,
and that pair is the "was it moved" answer. `SourceInfo` at 44 flags
system-originated change (0x1 DATA_MANAGEMENT, 0x2 AUXILIARY_DATA, 0x4 REPLICATION_MANAGEMENT, 0x8 CLIENT_REPLICATION_MANAGEMENT): a scanner adding a checksum stream is not attacker activity.

## The other metafiles, and $Recycle.Bin

Inode numbers measured with `fls -r -p`: `$MFT` 0, `$MFTMirr` 1, `$LogFile` 2, `$Volume` 3,
`$AttrDef` 4, root 5 (`fsstat`), `$Bitmap` 6, `$Boot` 7, `$BadClus` 8, `$Secure` 9, `$UpCase` 10, `$Extend` 11.

| Metafile | Answers |
|---|---|
| `$LogFile` (2) | changes `$J` has already wrapped past; redo/undo records hold pre-change attribute values. No `$LogFile` parser is installed here, so day zero is `icat -o <off> image.dd 2-128-1 > logfile.bin` then `strings -el logfile.bin` for the UTF-16LE names |
| `$Boot` (7) | volume serial and cluster size, to tie a LNK `DriveSerialNumber` to this volume |
| `$Secure:$SDS` (9-128-2) | the security descriptor a file carried, when ownership follows a move |
| `$Extend` (11) | holds `$UsnJrnl`, `$ObjId`, `$Quota`, `$Reparse`; `$ObjId:$O` maps object ids to inodes and survives a rename |

Measured: on a freshly formatted volume `fls -r -p` listed `$ObjId:$O`, `$Quota:$Q`, `$Quota:$O` and
`$Reparse:$R` but **no** `$J` - the journal is created on first use, so its absence is not tampering.
`$Recycle.Bin\<SID>\` pairs `$I<6 chars>.<ext>` with `$R<same 6 chars>.<ext>`; matching those six characters restores the original name (recyclebinunit FORMAT.md):

| Offset | Size | Field |
|---|---|---|
| 0x00 | 8 | Header version: `01` = Vista/7/8, `02` = Windows 10 and later |
| 0x08 | 8 | Original size, int64 bytes |
| 0x10 | 8 | Deletion time, FILETIME, UTC even where Explorer showed local |
| 0x18 | 520 / 4 | v1: original path, `wchar[260]`; the record is a fixed 0x18+520 = **544 bytes** ("Total fixed size: 544 bytes", recyclebinunit FORMAT.md). v2: a 4-byte path character count including the terminator, then the path at 0x1C in UTF-16LE, so a v2 `$I` is only as long as its path |

The `$R` hex-payload trick is at `../ctf-forensics/windows.md:148-152`. Deleted *without* the bin:
`$J` reason 0x200, an `$MFT` record with the allocation flag clear, `fls` marking the entry `*`;
`icat` still extracts it until the record is reused, and `tsk_recover -e -o <offset> image.dd outdir`
pulls allocated and unallocated together.

## Shell artifacts that outlive the file

| Artifact | Fields that answer |
|---|---|
| `Zone.Identifier` ADS | `ZoneId=3` is URLZONE_INTERNET (Microsoft Learn, URLZONE: 0 LOCAL_MACHINE, 1 INTRANET, 2 TRUSTED, 3 INTERNET, 4 UNTRUSTED); `HostUrl` is the download source, `ReferrerUrl` the page. `../ctf-forensics/windows.md:255-262` shows only the live-host read (`Get-Content -Stream Zone.Identifier`); from an image the stream is an ADS row in `fls -r -p` and comes out with `icat -o <off> image.dd <inode>-128-<id>` |
| LNK `ShellLinkHeader` | 0x4C bytes: HeaderSize `0x0000004C` at 0, LinkCLSID `00021401-0000-0000-C000-000000000046` at 4, LinkFlags 0x14, FileAttributes 0x18, **CreationTime 0x1C, AccessTime 0x24, WriteTime 0x2C** (target FILETIMEs, zero when unset), FileSize 0x34 (MS-SHLLINK 2.1) |
| LNK `LinkInfo` / `VolumeID` | `LinkInfo` header (MS-SHLLINK 2.3): `LinkInfoSize` 0, `LinkInfoHeaderSize` 4 (0x1C, or >=0x24 when the Unicode offsets are present), `LinkInfoFlags` 8, `VolumeIDOffset` 12, `LocalBasePathOffset` 16, `CommonNetworkRelativeLinkOffset` 20, `CommonPathSuffixOffset` 24 - the target path is `LocalBasePath` concatenated with `CommonPathSuffix`. `VolumeID` (2.3.1): `VolumeIDSize` 0, `DriveType` 4 (0 UNKNOWN, 1 NO_ROOT_DIR, 2 REMOVABLE, 3 FIXED, 4 REMOTE, 5 CDROM, 6 RAMDISK), `DriveSerialNumber` 8, `VolumeLabelOffset` 12; `DriveType 2` with a serial not matching `$Boot` answers "removable media" |
| `DestList` in `<AppId>.automaticDestinations-ms` | OLE compound file under `%AppData%\Microsoft\Windows\Recent\AutomaticDestinations\`. 32-byte header: version 0 (1 = Win7, 3 and 4 = Win10), entry count 4, pinned count 8. Entry: droid volume GUID 8, droid file GUID 24, birth droid volume GUID 40, birth droid file GUID 56, hostname ASCII 72 (16 bytes), entry number 88, last-modified FILETIME 100, pin status 108 (-1 unpinned), then path size 112 / path 114 for v1, path size 128 / path 130 for v3+ (libyal/dtformats, Jump lists format). The birth droid GUIDs name the volume the file was *first* seen on |
| ShellBags | `UsrClass.dat\Local Settings\Software\Microsoft\Windows\Shell\BagMRU` and `\Shell\Bags`, plus `NTUSER.DAT\Software\Microsoft\Windows\Shell\BagMRU`; `NodeSlot` ties a `BagMRU` subkey to its `Bags` view settings. A `BagMRU` chain proves a folder was opened in Explorer and survives its deletion - the answer for "name the folder that is gone" |

## Sleuth Kit day zero, the merged timeline, and ext4

sleuthkit 4.12.0 is installed - `mmls`, `fsstat`, `fls`, `istat`, `icat`, `blkls`, `ffind`, `ifind`,
`tsk_recover`, `tsk_gettimes`, `mactime` - and an ordering question needs no `$MFT` parser.
```bash
mmls image.dd                          # partition table; take the NTFS start sector
fsstat -o <offset> image.dd            # MFT entry size, cluster size, volume serial
fls -o <offset> -r -p image.dd         # full paths; '*' = deleted, ':' = an ADS
istat -o <offset> image.dd <inode>     # SI and FN blocks printed separately
icat -o <offset> image.dd 9-128-2      # one stream by inode-type-id ($Secure:$SDS)
tsk_gettimes image.dd > body.txt       # whole image to bodyfile in one step
mactime -y -d -b body.txt > fs.csv     # ISO 8601 UTC, comma delimited
```
Bodyfile columns, established by patching a known FILETIME and reading which column moved:
`MD5|path|inode-type-id|mode|UID|GID|size|atime|mtime|ctime|crtime`; the `0` in column 1 is `fls` not
hashing. The `mactime -d` header is `Date,Size,Type,Mode,UID,GID,Meta,File Name`, `Meta` is the
inode-type-id and `Type` the `macb` mask, so a split timestamp set prints two rows.
```bash
python3 tools/forensics/timeline_merge.py --source fs.csv:Date:fs \
    --source events.jsonl:TimeCreated:evtx --source usn.csv:TimeStamp:usn --filetime \
    --challenge <c> --gap 600 --contains '<filename>' --answer '<value>'
```
Measured on the mactime CSV above: 42 rows read, 42 parsed, 0 unparsed, assumption `offset_to_utc` on
42 rows, window 2001-01-01T00:00:00+00:00 to 2026-09-28T03:21:25+00:00 - the backdated row sorting to
the front is what makes it visible. `--filetime` attaches to the `--source` it follows, so a raw `$J`
export of 100 ns ticks since 1601 merges beside an ISO column; `--answer` emits the `hooks.py
pre-flag` argv, and only if `--contains` actually matched.

ext4 has a creation time, ext3 does not, and `stat(2)` never exposes it - a Linux triage tarball
preserving only `mtime` and `atime` cannot answer a creation question. Measured with e2fsprogs debugfs
1.47.2 on an 8 MB `mkfs.ext4 -F` image, unmounted, no root:
```bash
debugfs -w -R "write local.txt evil.sh" e.img   # offline write; prints the new inode
debugfs -R "stat <13>" e.img                    # ctime, atime, mtime AND crtime
fls -r e.img                                    # confirms: r/r 13: evil.sh
```
`crtime` is printed only when that same output says `Size of extra inode fields: 32` (256-byte inodes);
on a 128-byte-inode filesystem the field does not exist. `fls -m` fills all four bodyfile columns on
ext4, and `../ctf-forensics/linux-forensics.md` has no inode-timestamp material to duplicate.

## Traps

- `../ctf-forensics/windows.md:344` comments `0x1000=NAMED_DATA_OVERWRITE`. Per Microsoft Learn that is
  wrong: 0x1000 is RENAME_OLD_NAME and NAMED_DATA_OVERWRITE is 0x10 - use the table above. Measured: `-m`
  takes a mandatory prefix, so `fls -m -r img` eats `-r` and emits `-r/evil.sh` unrecursed; the colon in
  `-m C:` is cosmetic (`-m C` gives `C/evil.sh`).
- FILETIME in `$I`, `$J`, LNK and `DestList` is UTC: a question quoting local time is quoting what
  Explorer rendered. And `$MFT` cannot prove deletion order, because records are reused and carry
  only the new file's times - `$J` is the ordering source, `$MFT` the state source.
- A resident `$DATA` attribute puts the whole body inside the 1024-byte record, so a small deleted file
  is recoverable from `$MFT` with no clusters. A ShellBag entry is inherited by a new folder of the same name, so it dates browsing, not creation.
- UNVERIFIED here: no `$MFT`, `$J`, `$I`, LNK, jump list or `UsrClass.dat` from a real Windows host
  has been parsed in this tree. Every offset above is from the cited specification; only the sleuthkit,
  mactime, debugfs and timeline_merge numbers were measured locally.

## Routing

Shares signals with `../dfir-antiforensics-trace/` (the divergence itself is the question) and
`../dfir-execution-trace/` (the file is only evidence a process ran); check those first. Depth, one file
at a time: `../dfir-sherlock-triage/filesystem-timeline.md`, then `../ctf-forensics/windows.md`. Signals
are in `knowledge/bug-classes.json`; classify with `python3 tools/classify.py`.

## Discipline

One artifact family per probe, three attempts, then pivot. Quote every answer with the artifact and
field it came from - `$I` deletion FILETIME, `$J` reason 0x100, the `($FILE_NAME)` bodyfile row -
because a bare timestamp with no artifact named is not an answer. Merge with
`tools/forensics/timeline_merge.py` rather than by hand and report its `unparsed` count; `field-notes.md`
grows on every solve, `proposed` awaiting review and `confirmed` checked.
