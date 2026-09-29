---
name: dfir-antiforensics-trace
description: >
  Action-oriented depth skill for Anti-forensics and log tampering trace. Use after the router or
  tools/classify.py names this class; start with the first probe and record the expected signal. Do not
  use it as proof of a finding. Confusable classes: dfir-filesystem-timeline, dfir-persistence-trace.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, evtx, defender, anti-forensics, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Anti-forensics and log tampering trace

**Catalogue class.** This toolkit has never solved one. What follows is standard published knowledge, not local experience - record what actually happens in `field-notes.md`.

## First probe

The record-identifier gap: no EVTX parser is installed on this box, and this needs none.

```bash
python3 -u - <<'PY'
import struct, glob
for p in sorted(glob.glob('**/*.evtx', recursive=True)):
    b = open(p, 'rb').read()
    if b[:8] != b'ElfFile\x00': continue
    nxt = struct.unpack_from('<Q', b, 0x18)[0]              # next record identifier
    ids, o = [], 0x1000                                     # chunks at 0x1000 + n * 0x10000
    while o + 512 <= len(b) and b[o:o+8] == b'ElfChnk\x00':
        ids.append(struct.unpack_from('<QQ', b, o + 0x18))  # chunk first id, last id
        o += 0x10000
    if not ids:                                             # header only: truncated, carved, or a stub
        print(p, 'next_id=%d chunks=0 (no ElfChnk at 0x1000 - truncated, not a clear)' % nxt); continue
    gaps = [(ids[i][1], ids[i+1][0]) for i in range(len(ids)-1) if ids[i+1][0] != ids[i][1] + 1]
    print(p, 'next_id=%d oldest=%d newest=%d gaps=%s' % (nxt, ids[0][0], ids[-1][1], gaps))
PY
```

The `if not ids` guard is load-bearing, not defensive: without it the loop raises `IndexError: list index out of range` on the first header-only `.evtx` and aborts the whole glob, so one truncated channel hides every other one. Measured here - the three 44-byte stubs under `tools/forensics/fixtures/evtx-only/` carry a valid `ElfFile\x00` magic and no chunk, and the unguarded version dies on `Application.evtx` before reaching `Security.evtx`.

Measured 2026-09-28 against two EVTX files synthesised here to the libyal libevtx header layout, because the only `.evtx` under `tools/forensics/fixtures/` are 44-byte magic stubs:
```text
Cleared.evtx next_id=4 oldest=1 newest=3 gaps=[]
Gapped.evtx  next_id=4401 oldest=4102 newest=4400 gaps=[(4200, 4310)]
```
and against the stubs themselves: `Application.evtx next_id=0 chunks=0 (no ElfChnk at 0x1000 - truncated, not a clear)`, three times.
`oldest=1` on a channel that should hold months of history is a clear. A non-empty `gaps` list is surgical record deletion, which writes no 1102 at all: 109 records vanished
between identifiers 4200 and 4310, and that pair dates the hole against the records either side of it.

**Falsifier** - the observation that closes this class: every `.evtx` reports `gaps=[]` with `oldest` consistent with retention; the clear-and-disable sweep

```bash
python3 tools/forensics/evtx_query.py --input converted.jsonl --challenge <c> \
    --event-id 1102 --event-id 104 --event-id 1100 --event-id 4719 --event-id 1013
```

reports `"matched": 0` (both `--input` and `--challenge` are required by its argparse, so neither can be dropped); and `python3 tools/forensics/artifact_inventory.py
--path <bundle> --challenge <c>` names no `registry-transaction-log`, `recycle-bin` or Defender tree. Nothing was erased; the emptiness is collection scope, and the
question belongs to `../dfir-execution-trace/` or `../dfir-filesystem-timeline/`.

## Recognise and confirm

The question says *erased*, *cleared*, *wiped*, *hid*, *covered their tracks* - or, the usual disguise, asks for a value out of an artifact that turns out to be empty. Every such
question has two answers: **when the erasure happened** (an event or a gap) and **what survived it** (the recovery table below). Confirm the first before spending a probe on the
second.

## Clearing and disabling: the events each one writes

| ID | Channel | Fields that answer |
|---|---|---|
| 1102 | Security, provider `Microsoft-Windows-Eventlog` | `UserData/LogFileCleared`: `SubjectUserName`, `SubjectDomainName`, `SubjectUserSid`, `SubjectLogonId` |
| 104 | System and any non-Security channel, same provider | **`Channel`** - which log - plus `BackupPath`, `SubjectUserName`, `SubjectDomainName` |
| 1100 | Security | logging service shut down; a 1100 with no 4609 (Windows shutting down) is a service stop, not a reboot |
| 4719 | Security | audit policy changed - `SubcategoryGuid`, `AuditPolicyChanges`, `SubjectUserName`; Microsoft ranks it **High**, one occurrence worth investigating (Microsoft Learn, Appendix L) |
| 6005 / 6006 | System, provider `EventLog` | log service started / stopped; 7034 / 7035 / 7036 from Service Control Manager say the same for `EventLog` and `Sysmon64` |
| 4 | Sysmon/Operational | Sysmon service state changed - **cannot be filtered out by config** |
| 16 | Sysmon/Operational | `ServiceConfigurationChange`, "logs changes in the Sysmon configuration - for example when the filtering rules are updated", also unfilterable (Microsoft Learn, Sysmon) |

Command lines to hunt in Sysmon 1 / 4688 / 4104: `wevtutil cl Security`, `Clear-EventLog -LogName`, `Remove-EventLog`, `auditpol /clear /y` ("Deletes the per-user audit policy for
all users, resets (disables) the system audit policy for all subcategories" - Microsoft Learn, auditpol clear), `sc config eventlog start=disabled`, `Set-Service -Name EventLog
-Status Stopped` (ATT&CK T1070.001, T1562.002). A config-only Sysmon kill writes 16 and no 4.

EVTX layout, for reading the file rather than its records (libyal libevtx format documentation): file header `ElfFile\x00` at 0x00, first and last chunk number at 0x08 and 0x10,
**next record identifier at 0x18**, header size 128 at 0x20, minor and major version at 0x24 and 0x26, block size 4096 at 0x28, chunk count at 0x2A, flags and CRC32 at 0x78 and
0x7C. Chunk at `0x1000 + n*0x10000`: `ElfChnk\x00` at +0x00, first and last record **number** at +0x08 and +0x10, first and last record **identifier** at +0x18 and +0x20, free
space at +0x30. Record: `\x2a\x2a\x00\x00` at +0x00, size +0x04, identifier +0x08, written FILETIME +0x10. Identifier, not number, is the monotonic counter.

## Timestomping, deletion and wiping

| Artifact | Field that answers |
|---|---|
| Sysmon 2 `FileCreateTime` | `PreviousCreationUtcTime` is the real creation time, `CreationUtcTime` the planted one; plus `TargetFilename`, `Image`, `ProcessGuid` |
| `$STANDARD_INFORMATION` vs `$FILE_NAME` | the divergence itself - `$FILE_NAME` is attribute `0x30` and `$STANDARD_INFORMATION` is `0x10` in a 1024-byte `FILE` record (`../ctf-forensics/windows.md:294-316`); the split bodyfile row that prints it, and the column order `MD5\|path\|inode-type-id\|mode\|UID\|GID\|size\|atime\|mtime\|ctime\|crtime`, are at `../dfir-filesystem-timeline/SKILL.md:145-148` |
| `$J` reason `0x8000 BASIC_INFO_CHANGE` | Microsoft's definition is "a user has either changed one or more file or directory attributes (for example, the read-only, hidden, system, archive, or sparse attribute), **or one or more time stamps**" (`USN_RECORD_V2`), so `0x8000` alone is not backdating - a `+H +S` attrib call sets the same bit. Pair it with the `$FILE_NAME` divergence or a Sysmon 2. `0x200 FILE_DELETE` is deletion with or without the Recycle Bin |
| `$Recycle.Bin\<SID>\$I*` | original path plus deletion FILETIME; the matching `$R*` holds the bytes |
| Sysmon 23 `FileDelete` | **archived** - the file is copied into `ArchiveDirectory`, "Name of directories at volume roots", default `Sysmon`, so `C:\Sysmon`. Fields `TargetFilename`, `Image`, `Hashes`, `IsExecutable`, `Archived` |
| Sysmon 26 `FileDeleteDetected` | logged, **not** archived - same fields, no copy of the bytes |
| Sysmon 28 `FileBlockShredding` | "detects and blocks file shredding from tools such as SDelete" - names the shredder (Microsoft Learn, Sysmon) |
| `EFSTMPWP` at a volume root | `cipher.exe /w` free-space wipe: `../ctf-forensics/windows.md:548-566` |
| `HKU\<SID>\SOFTWARE\Sysinternals\SDelete\EulaAccepted` = 1 | proof sdelete ran under that SID; the key's last-written time dates it |
| a `$J` burst of `AAA.AAA`, `BBB.BBB`, ... | sdelete "renames the file 26 times, each time replacing each character of the file's name with a successive alphabetic character. For instance, the first rename of `foo.txt` would be to `AAA.AAA`" (Microsoft Learn, SDelete) - 26 rename pairs (`0x1000` + `0x2000`) on one FileReferenceNumber names one wiped file |
| an `$MFT` full of tiny equal-sized records | `sdelete -c` "must also fill any existing free portions of the NTFS MFT with files that fit within an MFT record" - the free-space-wipe fingerprint |

The sub-second tell: `SetFileTime` takes a FILETIME in 100 ns ticks, so a value built from a formatted date string lands on an exact second. Four `$STANDARD_INFORMATION` stamps
ending `.0000000` beside a `$FILE_NAME` set with seven nonzero digits is a planted time. UNVERIFIED here - no real `$MFT` has been parsed in this tree.

## Defender: the interference, and the quarantine that hands the sample back

Exclusions sit in two places and the difference answers "who set it": local writes (`Add-MpPreference`, `Set-MpPreference`, the API, a direct registry write) land under
`HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions\{Paths,Extensions,Processes}`; policy pushes land under `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Exclusions\` with
the same three subkeys. Scrutinise the non-policy key first. `Microsoft-Windows-Windows Defender/Operational`, symbolic names verbatim from Microsoft Learn:

| ID | Symbolic name | Fields |
|---|---|---|
| 1006 / 1116 | `MALWAREPROTECTION_MALWARE_DETECTED` / `..._STATE_MALWARE_DETECTED` | `Name`, `ID`, `Severity`, `Category`, `Path` |
| 1007 / 1117 | `..._MALWARE_ACTION_TAKEN` / `..._STATE_MALWARE_ACTION_TAKEN` | `User`, `Name`, `Path` - pair with 1006/1116 for detected-then-quarantined |
| 1008 / 1119 | `..._MALWARE_ACTION_FAILED` / `..._STATE_MALWARE_ACTION_CRITICALLY_FAILED` | remediation did **not** happen: the file is still on disk |
| **1013** | `MALWAREPROTECTION_MALWARE_HISTORY_DELETE` | "The antimalware platform deleted history of malware" - `Time`, `User`. The tamper event for DetectionHistory |
| 1015 / 1120 | `..._BEHAVIOR_DETECTED` / `..._THREAT_HASH` | `Name`, `Path`; 1120 gives `Threat Resource Path` and `Hashes`, only when the `ThreatFileHashLogging` policy is set |
| 5001 / 5010 / 5012 | `..._RTP_DISABLED` / `..._ANTISPYWARE_DISABLED` / `..._ANTIVIRUS_DISABLED` | no data fields, so the **message text is the whole answer** and the three differ: 5001 "Real-time protection is disabled", 5010 "Scanning for malware and other potentially unwanted software is disabled", 5012 "Scanning for viruses is disabled". Which one fired says which switch was thrown |
| 5004 | `MALWAREPROTECTION_RTP_FEATURE_CONFIGURED` | `Feature` (On Access, Behavior monitoring, Network Inspection System), `Configuration` |
| **5007** | `MALWAREPROTECTION_CONFIG_CHANGED` | Microsoft documents exactly two fields, `Old value` and `New value`, described only as "Old/New antivirus configuration value" - it does **not** document a path field. In practice `New value` carries the full changed registry value path, so an `Add-MpPreference` exclusion reads as `HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths\<path>`. Read the string, do not assume the shape |
| 5013 | message "Tamper protection blocked a change" | "states which setting change was blocked"; the docs label it `MALWAREPROTECTION_SCAN_CANCELLED`, a documentation error - quote the message, not the symbolic name |

`MPLog-*.log` under `C:\ProgramData\Microsoft\Windows Defender\Support\` survives a Security clear. Grep for `DETECTION_ADD` - `2021-07-22T15:38:04.557Z DETECTION_ADD
Ransom:Win32/Conti.ZA file:C:\ProgramData\badfile.exe`; `Engine:EMS scan` and `Engine:EMS detection` carrying `process:`, `pid:`, `sigseq=`; and the impact rows `ProcessImageName`,
`TotalTime`, `Count`, `MaxTime`, **`MaxTimeFile`**, `EstimatedImpact`, where `MaxTimeFile` names a path Defender touched and outlives the file (CrowdStrike, MPLog).
`OriginalFileName` exposes a renamed executable. DetectionHistory binaries: `../ctf-forensics/windows.md:457-479`.

**The quarantine store answers "hash the payload" after the file is gone.** `C:\ProgramData\Microsoft\Windows Defender\Quarantine\{Entries,ResourceData,Resources}`; every chunk is
obfuscated with a 256-byte RC4 key hardcoded in `mpengine.dll` beginning `1E 87 78 1B 8D BA A8 44 CE 69` (ernw/quarantine-formats). An `Entries` file is three separately
RC4-encrypted sections: `QuarantineEntryFileHeader` 60 bytes - `MagicHeader[4]`, `Unknown[4]`, `_Padding[32]`, `Section1Size`, `Section2Size`, `Section1CRC`, `Section2CRC`,
`MagicFooter[4]`; section 1 - `Id[16]`, `ScanId[16]`, `Timestamp`, `ThreatId`, `One`, `DetectionName`; section 2 - `EntryCount` then `EntryOffsets[]`, each resource giving
`DetectionPath`, `FieldCount`, `DetectionType`, field ids `PhysicalPath` 0x0C, `DetectionContext` 0x0D, `CreationTime` 0x0F, `LastAccessTime` 0x10, `LastWriteTime` 0x11 (Fox-IT,
Reverse Reveal Recover). ERNW's independent table puts that header at 0x3C bytes with data1 length at 0x28 and data2 length at 0x2C, data1 holding a GUID at 0x00, a timestamp at
0x20 and a null-terminated UTF-8 malware type at 0x34, data2 holding paths as null-terminated UTF-16LE. A decrypted `ResourceData` file is a binary security descriptor at 0x00, an
8-byte length at `bsd+0x08`, and the original bytes at `bsd+0x14`, wrapped in `WIN32_STREAM_ID` structures so `Zone.Identifier` survives too. Carve that length from `bsd+0x14`,
hash it, and that is the answer.

## Shadow copies, journals and hives: what outlives the erase

- `vssadmin delete shadows /for=c: /all /quiet`, `/oldest`, or `/shadow=<ShadowID>` (Microsoft Learn). It removes only *client-accessible* copies and the docs point
  at `diskshadow` for the rest, so a `diskshadow` command line is the second form to grep for. Read what remains with libvshadow: `vshadowinfo -o <byte offset>
  image.raw`, then `vshadowmount -o <byte offset> image.raw /mnt/vss`, the byte offset being the `mmls` sector offset times 512. `libvshadow-utils` is in the rank-1
  apt line in `../dfir-sherlock-triage/toolchain.md` and is **not installed today** - yet a shadow copy is often where the pre-clear `Security.evtx` still lives.
- `fsutil usn deletejournal /d c:` disables the journal and returns I/O control while it drains, `/n` returns only after. Microsoft's remark: disabling "must access
  all the records in the master file table (MFT) and set the last USN attribute to 0 (zero)", so a volume whose MFT records all carry USN 0 was journal-deleted
  rather than merely wrapped.
- Registry base block: `regf` at 0x00, **primary sequence number at 0x04, secondary at 0x08**. Equal is clean; unequal, or a bad checksum at 0x1FC, is dirty, and the
  `.LOG1`/`.LOG2` replay then holds values the primary hive no longer has. **The log the attacker's deleted value sits in depends on the Windows version, and the
  common statement of this rule is the wrong one for a Sherlock host.** Vista through Windows 8 use `.LOG1` normally and switch to `.LOG2` only after a write error to
  the primary; Windows 8.1 and later "regularly swap the transaction log file being used (`.LOG1` to `.LOG2` and vice versa)", and recovery applies entries from
  **both** logs, earliest first (msuhanov, Windows registry file format specification). So on Windows 10 or 11 never replay `.LOG1` alone and conclude the value is
  gone. regipy's signature is `apply_transaction_logs(hive_path, primary_log_path, secondary_log_path=None, restored_hive_path=None)` - there is no
  `transaction_log_path` parameter. regipy is rank 4 in `../dfir-sherlock-triage/toolchain.md` and absent here, though `artifact_inventory.py` still names the family
  `registry-transaction-log`.
- Registry hiding (dfir.ru, Hiding data in the registry): a **null byte embedded in a value name** via the native API, which `regedit.exe` and `reg.exe` cannot open
  because the Win32 API treats it as a terminator - `RegDelNull` "scans the registry for null embedded entries", and an offline hive parser reading the raw name
  bytes sees it regardless; **`CmpFailPrimarySave` set to 3**, forcing writes into the transaction logs only, invisible to any offline parser that does not replay
  them; **duplicate names built on character 0x9F**, distinct under Latin-1 and colliding under Windows-1252; and **`RegReplaceKeyA()`** hive swapping, where the
  edited primary file takes effect only at reboot. That article documents no oversized-value trick, so do not claim one.
- PowerShell history at `%AppData%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt` (ATT&CK T1070.003): deleting it leaves a `$J` `0x200` record
  naming it, and transcripts elsewhere.

## Recovery order - reach for these, in this order

| Destroyed | 1st | 2nd | 3rd | 4th |
|---|---|---|---|---|
| Security cleared (1102, or a gap) | Sysmon/Operational | prefetch + Amcache | `$J` 0x100/0x200 | a shadow copy's older `Security.evtx` |
| Every EVTX cleared, Sysmon too | prefetch `.pf` | `Amcache.hve` | MPLog + DetectionHistory | SRUM, browser SQLite |
| One file deleted | Sysmon 23 archive under `C:\Sysmon` | `$Recycle.Bin` `$I`/`$R` | `$J` 0x200 | unallocated `$MFT` record, resident `$DATA` |
| File wiped (EFSTMPWP, sdelete) | stop carving | `$MFT` name and times | quarantine `ResourceData` | LNK, jump list, MPLog `MaxTimeFile` |
| Timestamps changed | `$FILE_NAME` | `$J` 0x8000 | Sysmon 2 `PreviousCreationUtcTime` | prefetch run times, key last-written |
| Defender history purged (1013) | quarantine `Entries` | MPLog `DETECTION_ADD` | 1116/1117 | 1120 `Hashes` |
| USN journal deleted | `$LogFile` | `$MFT` allocation state | shadow copy | prefetch |
| Registry value deleted | `.LOG1`/`.LOG2` replay | unallocated hive cells | shadow copy of the hive | Sysmon 12/13/14 |
| Shadow copies deleted | the command line in Sysmon 1 / 4688 | System 7036 for the VSS service | `$J` on the diff-area files | Amcache for `vssadmin.exe` |
| Audit policy cleared (4719) | 4719 `AuditPolicyChanges` | Sysmon, unaffected | `$J` | the checklist at `../ctf-forensics/windows.md:481-498` |

## Traps

- 1102 is the **first record written into the freshly cleared file**, so its timestamp is the clear time, not the intrusion time - answer "when were the logs
  cleared" from it and never "when did the intrusion start". Its `EventRecordID` is usually 1, but do **not** assert that: Microsoft's own documented 1102 sample XML
  carries `<EventRecordID>1087729</EventRecordID>` (Microsoft Learn, event-1102). Read the value, quote the value. A 104 quoted without its `Channel` field names
  nothing.
- Sysmon 2 fires constantly from installers and archivers - Microsoft's own wording is "many processes legitimately change the creation time of a file; it does not
  necessarily indicate malicious activity". Require `PreviousCreationUtcTime` plus the `$FILE_NAME` divergence first.
- 23 archives, 26 does not. A bundle carrying 26 and no 23 means the events exist and the bytes do not.
- `evtx_dump` is multithreaded by default and emits records **out of order**, so a "gap" read off an unsorted dump is an artefact of the dump; pass `-t 1`. `chainsaw
  hunt -s <sigma>` **requires** `--mapping` and renders UTC by default. hayabusa's subcommand is `hayabusa dfir-timeline -t csv|json|jsonl -d <dir> -o <out>`, long
  flag lowercase `--iso-8601`, output in **local time** unless `-U` is passed. Measured 2026-09-28: `command -v` finds none of `evtx_dump`, `chainsaw`, `hayabusa`,
  `vshadowinfo`, `vshadowmount`, `regripper`, `reglookup` or `regipy` on this box, so until the rank-1 apt line in `../dfir-sherlock-triage/toolchain.md` is run, the
  First probe above and `tools/forensics/evtx_query.py` over an already-converted JSONL are the whole EVTX capability here.
- An absent artifact is not tampering. `../dfir-filesystem-timeline/` measured that a freshly formatted NTFS volume lists no `$J` at all, because the journal is
  created on first use.

## Routing

Shares signals with `../dfir-filesystem-timeline/` - when the question wants *when* a file changed rather than *who erased it*, that file owns it - and
`../dfir-persistence-trace/`, because a stopped service can be persistence rather than tampering. Check both first. Depth, one file at a time:
`../dfir-sherlock-triage/windows-event-logs.md`, then `../ctf-forensics/windows.md:481-498`. Signals are in `knowledge/bug-classes.json`; classify with `python3 tools/classify.py`.

## Discipline

One artifact family per probe, three attempts, then pivot to the next column of the recovery table rather than a fourth variant of the same query. Quote the artifact and the field
with every answer - 1102 `SubjectUserName`, 104 `Channel`, 5007 `New value`, chunk identifier gap `(4200, 4310)` - because a bare name or timestamp with no artifact named is not an
answer. Measured here: against a JSONL holding one 1102 record, `python3 tools/forensics/evtx_query.py --input sec.jsonl --event-id 1102 --challenge <c> --answer SubjectUserName`
reported `"read":2,"matched":1`, resolved `SubjectUserName` from inside `UserData/LogFileCleared` with no path given, and emitted the `tools/hooks.py pre-flag` argv - use it
instead of retyping a value. Record the negatives too: a channel proved contiguous is a result. `field-notes.md` grows on every solve, `proposed` awaiting review and `confirmed`
checked.
