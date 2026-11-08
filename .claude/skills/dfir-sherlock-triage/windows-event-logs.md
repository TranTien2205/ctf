# Windows event logs

The most common Sherlock artifact family by a wide margin. Answers logon,
execution, persistence and lateral-movement questions.

Evidence level: catalogue. The event-ID tables are standard published knowledge.
The tool invocations were verified against each tool's own source or documentation
at the time of writing; confirm any flag against the installed build with `--help`
before trusting it in a runbook, per this tree's rule on inventing tool flags.

## Parsing, in escalating cost

Nothing on this box parses EVTX until `toolchain.md`'s rank-1 install is run.

```bash
evtxexport -f xml Security.evtx > security.xml      # libevtx-utils; no runtime deps
evtx_dump -o jsonl -t 1 Security.evtx > security.jsonl
```

`-t 1` forces single-threaded output. The default is multithreaded and emits
records **out of order** - complete and correct, but not chronological, so any
"what happened first" answer read off the top of the file is silently wrong. Pass
it whenever order matters.

Into jq, then pandas:

```bash
jq -r 'select(.Event.System.EventID == 4624)
       | [.Event.System.TimeCreated_attributes.SystemTime,
          .Event.EventData.TargetUserName,
          .Event.EventData.LogonType,
          .Event.EventData.IpAddress] | @tsv' security.jsonl
```

Field paths differ slightly between converters. Dump one record in full and read
the real path before writing a filter across the set.

Sigma hunting over a whole directory:

```bash
chainsaw search -t 'Event.System.EventID: =4104' <evtx dir> --json
chainsaw search -e '<regex>' <evtx dir> --json
chainsaw hunt <evtx dir> -s <sigma dir> --mapping <mapping file>
chainsaw analyse gaps <evtx dir>
```

`-s` requires `--mapping`; chainsaw's own argument definition marks the mapping
parameter as required by the sigma parameter. The Kali package ships both a
mapping file and a rules tree under `/usr/share/chainsaw/`, so no separate Sigma
clone is needed for a first pass. `chainsaw` renders **UTC by default** - do not
pass `--local`.

`analyse gaps` finds chronological and record-ID discontinuities, which is the
check to run after a 1102.

## Security channel

### Authentication

| ID | Meaning | The field the question usually wants |
|---|---|---|
| 4624 | Successful logon | `LogonType`, `IpAddress`, `TargetUserName`, `LogonId` |
| 4625 | Failed logon | `Status` / `SubStatus`, `IpAddress`, count |
| 4634 | Logoff | `LogonId` - join to 4624 for session duration |
| 4647 | User-initiated logoff | `TargetUserName` |
| 4648 | Logon using explicit credentials | the account being switched TO |
| 4672 | Special privileges assigned | marks an administrator-equivalent session |
| 4768 | Kerberos TGT requested | `TargetUserName`, `IpAddress` |
| 4769 | Kerberos service ticket requested | `ServiceName`, `TicketEncryptionType` |
| 4771 | Kerberos pre-authentication failed | failure code |
| 4776 | NTLM credential validation | source workstation |

**Logon types**, which decide half the authentication questions:

| Type | Meaning |
|---|---|
| 2 | Interactive - at the keyboard |
| 3 | Network - share access, remote authentication |
| 4 | Batch - scheduled task |
| 5 | Service |
| 7 | Unlock |
| 8 | Network cleartext |
| 9 | New credentials - a process running as another account |
| 10 | RemoteInteractive - RDP |
| 11 | Cached interactive |

A question asking "was this a remote desktop session" means type 10, not type 3.

**4625 sub-status codes**, which distinguish a spray from a typo:

| Code | Meaning |
|---|---|
| `0xC0000064` | account does not exist |
| `0xC000006A` | wrong password, account exists |
| `0xC0000072` | account disabled |
| `0xC0000234` | account locked out |
| `0xC0000070` | workstation restriction |
| `0xC000015B` | logon type not granted |

Many `0xC0000064` against many names is enumeration; many `0xC000006A` against one
name is a password attack. That distinction is a frequent answer.

### Execution and change

| ID | Meaning |
|---|---|
| 4688 | Process creation - carries the command line ONLY if command-line auditing was enabled |
| 4689 | Process termination |
| 4697 | Service installed (Security channel) |
| 4698 / 4699 / 4700 / 4702 | Scheduled task created / deleted / enabled / updated |
| 4720 / 4722 / 4724 / 4726 / 4738 | Account created / enabled / password reset / deleted / changed |
| 4728 / 4732 / 4756 | Member added to a global / local / universal group |
| 5140 / 5145 | Network share accessed / detailed share access |
| 1102 | **Audit log cleared** - the answer moved; see the fallback below |

A 4688 with an empty command line does not mean nothing ran. It means command-line
auditing was off, and Sysmon 1 or PowerShell 4104 carries the string instead.

## Sysmon channel

Richest single channel when present. `Microsoft-Windows-Sysmon/Operational`.

| ID | Meaning | Key fields |
|---|---|---|
| 1 | Process create | `Image`, `CommandLine`, `ParentImage`, `ProcessGuid`, `Hashes`, `User` |
| 2 | File creation time changed | the timestomp signal |
| 3 | Network connection | `DestinationIp`, `DestinationPort`, `ProcessGuid` |
| 5 | Process terminated | `ProcessGuid` |
| 6 | Driver loaded | `ImageLoaded`, `Signature` |
| 7 | Image loaded | unsigned DLL from a user-writable path is the signal |
| 8 | CreateRemoteThread | source and target process |
| 10 | ProcessAccess | `GrantedAccess`, target - credential-store access shows here |
| 11 | FileCreate | `TargetFilename` |
| 12 / 13 / 14 | Registry key create-delete / value set / rename | `TargetObject`, `Details` |
| 15 | FileCreateStreamHash | alternate data stream written |
| 17 / 18 | Named pipe created / connected | pipe name |
| 19 / 20 / 21 | WMI filter / consumer / binding | persistence via WMI subscription |
| 22 | DNS query | `QueryName`, `QueryResults`, `ProcessGuid` |
| 23 / 26 | FileDelete | recovers what was removed |
| 25 | ProcessTampering | hollowing or herpaderping signal |

**`ProcessGuid` is the join key.** It is stable across events 1, 3, 10, 22 and 5,
which is what makes the execution chain in `method.md` mechanical rather than
intuitive.

## PowerShell channels

| Channel | ID | Meaning |
|---|---|---|
| `Microsoft-Windows-PowerShell/Operational` | 4103 | Module / pipeline execution detail |
| `Microsoft-Windows-PowerShell/Operational` | 4104 | **Script block logging** - the deobfuscated script text |
| `Windows PowerShell` (classic) | 400 / 403 | Engine start / stop |
| `Windows PowerShell` (classic) | 600 | Provider lifecycle |

4104 is the highest-value event in the whole set when present: Windows logs the
script block **after** deobfuscation, so a base64-encoded command appears in plain
text. A long script is split across multiple 4104 records with `MessageNumber` and
`MessageTotal` - reassemble in order before reading.

Recovering an encoded command by hand:

```bash
python3 -c "import base64,sys;print(base64.b64decode(sys.argv[1]).decode('utf-16-le'))" '<b64>'
```

UTF-16LE, not UTF-8: PowerShell's `-EncodedCommand` is UTF-16LE.

Distinct from 4104 and often overlooked: over-the-shoulder **transcripts** written
to `Documents\PowerShell_transcript.*.txt`, which capture output as well as input.
`ConsoleHost_history.txt` is a third source - see
`../ctf-forensics/windows.md:394-408` for using its write times as a timeline.

## Other channels worth naming

| Channel | IDs | Answers |
|---|---|---|
| `System` | 7045 | Service installed - name, image path, start type |
| `System` | 7034 / 7036 | Service crashed / state change |
| `TaskScheduler/Operational` | 106 / 140 / 141 | Task registered / updated / deleted |
| `TaskScheduler/Operational` | 200 / 201 | Action started / completed - the execution TIME, which 4698 does not give |
| `TerminalServices-LocalSessionManager` | 21 / 22 / 23 / 24 / 25 | RDP session logon, shell start, logoff, disconnect, reconnect |
| `TerminalServices-RemoteConnectionManager` | 1149 | RDP authentication - source address |
| `WMI-Activity/Operational` | 5857 / 5858 / 5860 / 5861 | WMI provider and permanent-subscription activity |
| `Windows Defender/Operational` | 1116 / 1117 | Threat detected / action taken |
| `BITS-Client/Operational` | 59 / 60 | Transfer started / completed - a download path that bypasses the browser |

Full RDP channel tables already exist at `../ctf-forensics/windows.md:425-455`.
Defender MPLog and DetectionHistory at `../ctf-forensics/windows.md:457-479`.

## When the log was cleared

Security 1102 means the answer moved, not that it is gone. In rough order of value:

1. **Sysmon** - a separate channel that clearing Security does not touch.
2. **Prefetch and Amcache** - execution survives log clearing entirely.
3. **`$J` USN journal** - file creation and deletion times, parser at
   `../ctf-forensics/windows.md:318-354`.
4. **Registry** - Run keys, Services and UserAssist are unaffected.
5. **`chainsaw analyse gaps`** - a record-ID discontinuity dates the clearing even
   when 1102 itself was removed.
6. The anti-forensics checklist at `../ctf-forensics/windows.md:481-498`.

## Directory-attack traces, written by artifact identity

This tree documents what these look like in a log. It does not document how to
perform them; see the scope clause in `../../AGENTS.md`.

- **Credential replay across hosts:** 4624 logon type 3 where the authentication
  package is NTLM on a network where Kerberos is expected, with no preceding 4768
  for that account, followed by 4776 on the source host.
- **Service-ticket harvesting:** a burst of 4769 requests from one account for many
  distinct `ServiceName` values, with `TicketEncryptionType` set to the RC4 value
  `0x17` rather than an AES type.
- **Forged-ticket use:** a 4769 or 4624 for an account with no matching 4768 TGT
  request, or a ticket whose account name does not exist in the directory.
- **Directory replication abuse:** event 4662 carrying the
  `DS-Replication-Get-Changes-All` control access right, requested by an account
  that is not a domain controller computer account.

In each case the answer the question wants is the field - the account, the address,
the timestamp - not the technique label.

## Falsifier

This file is the wrong one when no EVTX is present, or when the question is about
what exists on disk rather than what a process did. Route back through
`method.md` step 1.
