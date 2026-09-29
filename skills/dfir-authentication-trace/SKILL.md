---
name: dfir-authentication-trace
description: >
  Action-oriented depth skill for Authentication and logon trace. Use after the router or
  tools/classify.py names this class; start with the first probe and record the expected signal. Do
  not use it as proof of a finding. Confusable classes: dfir-execution-trace, dfir-network-exfil-trace.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, event-logs, logon, kerberos, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Authentication and logon trace

**Catalogue class.** This toolkit has never solved one. What follows is standard published knowledge, not local experience - treat it as a
starting point and record what happens in `field-notes.md`. Field names are quoted from the Microsoft Learn `EventData` XML per ID; Linux
struct numbers were measured here today.

## First probe
```bash
python3 tools/forensics/evtx_query.py --input security.jsonl --event-id 4624 \
    --field-contains LogonType=10 --challenge <sherlock>-q1 --answer IpAddress

```
Re-run here on `tools/forensics/fixtures/evtx/sherlock_sample.jsonl` with `--event-id 4625 --field-contains SubStatus=0xc000006a --answer
IpAddress`. Read the keys that exist: the count is the **list** `matches` (length 2) - there is no scalar `matched` - `answer.value` is
`10.10.14.22`, top-level `verdict` is `inconclusive`, and `answer.pre_flag_argv` holds the record verbatim as `--evidence`. Paste that argv.

**Falsifier** - the observation that closes this class: every 4624 carries `LogonType` 4 or 5 with a `TargetUserName` ending in `$` or named
SYSTEM / LOCAL SERVICE / NETWORK SERVICE, and the bundle holds no 4625, 4648, 4768 or 4776. Test `TargetUserSid`, never `SubjectUserSid`:
Microsoft's own note is that 4624 "is typically triggered by the SYSTEM account", so `SubjectUserSid` `S-1-5-18` is the norm and separates
nothing (Microsoft Learn, 4624). Nothing authenticated from outside; reroute via `../dfir-sherlock-triage/method.md` step 1.

## Recognise
Who logged in, from where, by what method, when, for how long, after how many failures, switched to which account. The answer is one
`EventData` field, or one difference of two timestamps.

## Confirm
1. `--event-id 4624`, read `LogonType`: the type decides what every other field means.
2. Take `TargetLogonId`: it joins 4634, 4647, 4672 and 4964, and `SubjectLogonId` on 4688. Microsoft names Logon ID as the 4624-to-4672
   correlator, but names **`LogonGuid`** for 4648 and 4964 - join those two on the GUID when the Logon ID does not line up (Microsoft
   Learn, 4624 and 4964).
3. Confirmed = a quoted record with account, address and type in it. A 4625 count is not a logon.

## 4624: logon type is the answer
| Type | Name | What it means for the question |
|---|---|---|
| 2 | Interactive | at the console; `IpAddress` usually `127.0.0.1` |
| 3 | Network | share access, remote authentication, server side of a remote tool |
| 4 | Batch | a scheduled task ran as this account |
| 5 | Service | the Service Control Manager started a service |
| 7 | Unlock | workstation unlocked - same person, not a new arrival |
| 8 | NetworkCleartext | password reached the package unhashed (IIS basic auth, some LDAP) |
| 9 | NewCredentials | a token was cloned with other credentials for outbound use |
| 10 | RemoteInteractive | RDP / Terminal Services. "Was this remote desktop" means 10 |
| 11 | CachedInteractive | cached domain credentials; the DC was never contacted |
| 12 / 13 | CachedRemoteInteractive / CachedUnlock | 12 is "Same as RemoteInteractive. This type is used for internal auditing"; 13 is "Workstation logon." verbatim |

| Field | Answers |
|---|---|
| `IpAddress` / `IpPort` | "from where"; `::1` local, `::ffff:10.0.0.12` mapped IPv4. Port `0` for interactive, nonzero = arrived over a socket |
| `WorkstationName` | source host name. Microsoft's caveat for a blank one: "network logons with Kerberos likely have no workstation information, and NTLM logons have no TCP/IP details" |
| `AuthenticationPackageName` / `LmPackageName` / `KeyLength` | `NTLM`/`Kerberos`/`Negotiate`; then `NTLM V1`, `NTLM V2` or `LM`; `KeyLength` is always `0` for Kerberos, including via Negotiate |
| `TargetLogonId` / `TargetLinkedLogonId` | the join key (`0x3e7` is SYSTEM, not a user); the paired split-token session, `0x0` when none |
| `ElevatedToken` / `LogonProcessName` / `ProcessName` | `Yes` = administrator privileges; `User32` console, `Advapi` service-style, `Kerberos`, `NtLmSsp`; plus the requesting binary's full path |

## 4625: Status is generic, SubStatus is the answer
Read `SubStatus` first; fall back to `Status` only when `SubStatus` is `0x0`, the lockout case (`Status 0xC0000234`, `SubStatus 0x0`).

| Code | Microsoft's own wording, quoted | Implies |
|---|---|---|
| `0xC0000064` | "User logon with misspelled or bad user account" | the name does **not** exist: name guessing |
| `0xC000006A` | "User logon with misspelled or bad password" | the name **does** exist: password attack, or a typo |
| `0xC000006D` | "This is either due to a bad username or authentication information" | generic - read `SubStatus` |
| `0xC000006F` / `0xC0000070` | "User logon outside authorized hours" / "from unauthorized workstation" | policy held |
| `0xC0000071` / `0xC0000193` | "Account logon with expired password" / "with expired account" | a stale credential, not an attack |
| `0xC0000072` | "User logon to account disabled by administrator" | a stale account was tried |
| `0xC000015B` | "The user has not been granted the requested logon type (aka logon right) at this machine" | right missing, password may be right |
| `0xC0000224` | "Account logon with 'Change Password at Next Logon' flagged" | right password, blocked anyway |
| `0xC0000234` | "Account locked out" - it is the `Status` in the Microsoft Learn 4625 sample XML | the lockout threshold was reached |

Provenance: `064 06A 06D 06F 070 072 15B` verbatim from the Microsoft Learn 4625 table whose column head is literally "**Status** or
**Sub Status**", so a code is legal in either field; `071 193 224 234` verbatim from Microsoft Learn 4776 "Table 1. Winlogon Error Codes".
`0xC0000133` and `0xC0000225` turn up in real 4625 data but are in **neither** first-party table - resolve them where the 4625 page itself
sends you, "For more information about various Status or Sub Status codes, see NTSTATUS Values" (MS-ERREF), and quote the code, never a
community sentence about it. The separating rule (a reading rule, not a Microsoft quote - Microsoft only calls `SubStatus` "additional
information about logon failure"): many `0xC0000064` over **many different** `TargetUserName` from one `IpAddress` = name enumeration,
answer = the distinct-name count or the first name tried; many `0xC000006A` against **one** `TargetUserName` = password attack, answer = the attempt
count or the last 4625 before the first 4624; one `0xC0000234` ends the run = threshold hit, after which attempts prove nothing since a
locked account rejects the correct password too. 4625 has no `TargetLogonId` and `TargetUserSid` is the null SID `S-1-0-0` for a nonexistent
account, so correlate on `IpAddress` plus time.

## Explicit credentials, privilege, Kerberos
| ID | Channel | Field that answers |
|---|---|---|
| 4648 | Security | `TargetUserName` = account switched **to**; `SubjectUserName` = who switched; `TargetServerName` (`localhost` if local); `ProcessName` |
| 4672 / 4964 | Security | `PrivilegeList` joined by `SubjectLogonId` to its 4624; `SidList`, whose watch list is the **String Value** `SpecialGroups` under `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa\Audit`, SIDs delimited by `;` (Microsoft Learn, 4964) |
| 4768 / 4769 | Security, DC only | TGT then service ticket: `TargetUserName`, `IpAddress`, `Status`, `TicketEncryptionType`, `PreAuthType`; then `ServiceName`, `TicketEncryptionType`, `LogonGuid` |
| 4771 | Security, DC only | pre-auth failure; carries `0x10` and `0x18`, which 4768 never does |
| 4776 | Security | NTLM validation: `TargetUserName`, `Workstation` (source only), `Status` |

4648 is the tell for credential switching: it fires when a process supplies an account's credentials explicitly - "most commonly ... such as
scheduled tasks, or when using the RUNAS command" (Microsoft Learn, 4648) - so its `SubjectUserName` and `TargetUserName` differ on exactly
the hop a 4624-only view cannot see. Kerberos codes (Microsoft Learn, 4768 "Table 3"): `0x6` KDC_ERR_C_PRINCIPAL_UNKNOWN (username does not
exist), `0x12` KDC_ERR_CLIENT_REVOKED (disabled, expired or locked out), `0x17` KDC_ERR_KEY_EXPIRED (password expired), `0x18`
KDC_ERR_PREAUTH_FAILED (wrong password - appears on **4771**), `0x25` KRB_AP_ERR_SKEW (clock skew). `TicketEncryptionType` `0x11`/`0x12` =
AES128/AES256-CTS-HMAC-SHA1-96, `0x17`/`0x18` = RC4-HMAC/RC4-HMAC-EXP, `0xFFFFFFFF` "shows in Audit Failure events"; `PreAuthType` `2` =
PA-ENC-TIMESTAMP (normal password), `15` = PA-PK-AS-REP_OLD (smart card), `138` = PA-ENCRYPTED-CHALLENGE (Kerberos Armoring/FAST), and `0` =
"Logon without Pre-Authentication", which Microsoft calls out to monitor for because it means the account is flagged "Do not require Kerberos
preauthentication". A 4768 written by a host patched past the January 14 2025 cumulative update carries extra `EventData`
(`AccountAvailableKeys`, `SessionKeyEncryptionType`, `PreAuthEncryptionType`, `ResponseTicket`); the old names still parse. Directory-attack
traces by artifact identity (a 4769 burst over many distinct `ServiceName`
at `0x17`; a 4624 with no matching 4768) are at `../dfir-sherlock-triage/windows-event-logs.md:203-221`; do not restate them.

## Session lifetime and the duration answer
| ID | Channel | Use |
|---|---|---|
| 4634 / 4647 | Security | logoff joined by `TargetLogonId` / user-initiated logoff. A session may have one, the other, or both |
| 4778 / 4779 | Security | reconnected / disconnected: `SessionName` (`RDP-Tcp#3`, or `Console` for fast user switching), `ClientName`, `ClientAddress` (`LOCAL` for console), `LogonID` |
| 21 22 23 24 25, then 39 / 40 | TerminalServices-LocalSessionManager/Operational | RDP logon, shell start, logoff, disconnect, reconnect. 39: disconnected **by** another session (differing ids = kicked off). 40: disconnect with `<Reason>`; `0` no further information, `2` an administrative tool from another session, `3` idle session timeout, `11` the user clicked Disconnect. Codes run 0-12; the rest UNVERIFIED here |
| 1149 / 131 | RemoteConnectionManager / RdpCoreTS Operational | the source address of an RDP authentication; then TCP connection accepted with client address and port |

`../ctf-forensics/windows.md:425-455` carries the wider RDP tables, but its LocalSessionManager row reads `40 | Session created` and has no
39 at all - **that row is wrong**; 40 is the disconnect that carries `<Reason>`. Use the table above. Profile creation as the
first-interactive-logon proxy is `../ctf-forensics/windows.md:410-423`. Worked duration, Brutus Sherlock (published writeup, 0xdf 2024-04-09; `279` and `2024-03-06 06:32:45`
are answer shapes in `../dfir-sherlock-triage/answer-discipline.md:50,53`):

| Step | Artifact and exact line | Second |
|---|---|---|
| authentication | `sshd[2491]: Accepted password for root from 65.2.161.68 port 53184 ssh2` | 06:32:44 |
| session start | wtmp `ut_type` 7 on `pts/1` | 06:32:45 |
| session end | `systemd-logind[411]: Removed session 37.`, wtmp `ut_type` 8 | 06:37:24 |

`06:37:24 - 06:32:45 = 279`. But `06:37:24 - 06:32:44 = 280`, and the published prose names the `Accepted` second while printing 279: take
the start from the **session** record, not the authentication line. Windows form: 4624 `TargetLogonId` to the 4634 with that same
`TargetLogonId`, subtracting `TimeCreated/@SystemTime`.

## Linux: text lines, then the binary trio
`/var/log/auth.log` (Debian-family), `/var/log/secure` (RHEL-family). Shapes from OpenSSH `auth.c`, format string `"%s %s%s%s for %s%.100s
from %.200s port %d ssh2%s%s"` with authmsg in `{Accepted, Failed, Postponed, Partial}` and validity prefix `invalid user `:

| Line | Answers |
|---|---|
| `Accepted password for root from 65.2.161.68 port 53184 ssh2` | the logon second, user, source, source port |
| `Accepted publickey for u from 10.0.0.1 port 2200 ssh2: RSA SHA256:<b64>` | which **key** - the fingerprint is the answer |
| `Failed password for root from 65.2.161.68 port 46852 ssh2` | one attempt against an existing account |
| `Failed password for invalid user admin from ... port 46392 ssh2`, and the earlier `Invalid user admin from 65.2.161.68 port 46380` from `"Invalid user %.100s from %.100s port %d"` | account absent: the `0xC0000064` analogue. The `Invalid user` line precedes any password check |
| `pam_unix(sshd:session): session opened for user root(uid=0) by (uid=0)` | uid and the session boundary; Linux-PAM `pam_unix_sess.c` uses `"session opened for user %s(uid=%s) by %s(uid=%lu)"`, and `"session closed for user %s"` with no uid |
| `systemd-logind[411]: New session 37 of user root.` / `Removed session 37.` | the session **number** a question may ask for, and both ends |
| `sudo: cyberjunkie : TTY=pts/1 ; PWD=/home/cyberjunkie ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow`, and `useradd[2592]: new user: name=cyberjunkie, UID=1002, GID=1002, home=..., shell=/bin/bash` | escalation with target account and full command; account creation with uid |

`utmp` = who is on now (`/run/utmp`), `wtmp` = login history (`/var/log/wtmp`), `btmp` = failed logins (`/var/log/btmp`), `lastlog` =
`/var/log/lastlog`. Measured today: `last`, `lastb`, `lastlog` and `utmpdump` are all **absent** here, so the struct is the day-zero path.

```python
FMT = "<hxxi32s4s32s256shhiii4i20s"   # 384 bytes, confirmed by struct.calcsize; fields in order:
# ut_type ut_pid ut_line[32] ut_id[4] ut_user[32] ut_host[256] e_termination e_exit ut_session
# tv_sec tv_usec ut_addr_v6[4] unused[20]

```
Measured: `/var/log/wtmp` here is 160128 bytes = 417 records exactly and `/var/log/btmp` 7296 = 19; that format produced real
`BOOT_TIME`/`USER_PROCESS`/`DEAD_PROCESS` rows with usernames and `tv_sec` decoding to sane UTC. `ut_type`: 0 EMPTY, 1 RUN_LVL, 2 BOOT_TIME,
3 NEW_TIME, 4 OLD_TIME, 5 INIT_PROCESS, 6 LOGIN_PROCESS, **7 USER_PROCESS** (a login), 8 DEAD_PROCESS (its logout), 9 ACCOUNTING;
`UT_LINESIZE`/`UT_NAMESIZE` 32, `UT_HOSTSIZE` 256 (man 5 utmp). `lastlog` differs: no `ut_type`, one 292-byte record (`int32 ll_time`, `char
ll_line[32]`, `char ll_host[256]`) **indexed by uid**, so record N is uid N - measured as 292292 bytes = 1001 records, uid 0-1000.

## Day zero, with no EVTX parser installed
`evtx_dump`, `chainsaw`, `hayabusa` and python `Evtx` are absent until `../dfir-sherlock-triage/toolchain.md` rank 1 or 2 runs. Until then:

```bash
xxd -l 8 Security.evtx                 # prints "ElfFile." - confirms the container
strings -el Security.evtx | grep -n -i -e Administrator -e 4624

```
Line 1 was run here against `tools/forensics/fixtures/evtx-only/Security.evtx` and printed `456c 6646 696c 6500  ElfFile.`. `strings -el`
works because EVTX holds strings "in UTF-16 little-endian without the byte order mark" and event data is **not compressed** (libyal EVTX
format documentation). The same document gives the stdlib record walk: `ElfFile\x00` at offset 0, chunk `ElfChnk\x00`, record signature
`\x2a\x2a\x00\x00` then size (u32), record id (u64), written FILETIME at offset 16, binary XML from 24, size repeated in the last 4 bytes -
enough to count records and read every timestamp, not to resolve `Data Name`, which needs the template table. UNVERIFIED here: the walk was
not run, those fixtures being 44 bytes, header only. With a converter, pass `evtx_dump -t 1`: its default is multithreaded, records out of
order.

## Traps
- **`LogonType` 3 is not RDP.** RDP is 10, or 12 when cached. A type 3 at the same minute from the same address is the share or named-pipe
  side of the same visit.
- **A 4672 is not an administrator logon** but a privilege assignment on a session; join `SubjectLogonId` to the 4624 or the account named
  is the wrong one.
- **`0x18` lives on 4771, not 4768**: Microsoft states codes `0x10` and `0x18` do not generate 4768, "Event 4771 ... generates instead".
  **4776 names only the source workstation.**
- **utmpdump column order is not struct order** - `[7] [02549] [ts/1] [root] [pts/1] [65.2.161.68]` is type, pid, **ut_id, ut_user, ut_line**,
  ut_host, so a parser following the printed order shifts every field. That row is read off a published writeup, not off `utmpdump`, which is
  absent here. **btmp counts attempts, not distinct sources** - read `ut_host`; **`lastlog` keeps only the newest login per uid**, so a
  sparse mostly-zero file is normal, not tampering.
- **Local time.** `hayabusa` renders LOCAL by default (`-U`/`--UTC`, long flag lowercase `--iso-8601`); `chainsaw` is already UTC, so
  `--local` breaks it. **An empty 4688 command line** is command-line auditing being off, not nothing running - hand it to the execution
  class.

## Routing
Shares signals with `../dfir-execution-trace/` (a 4688 or Sysmon 1 command line is the answer) and `../dfir-network-exfil-trace/` (the
address is a destination, not a source). Router and depth `../dfir-sherlock-triage/` (`SKILL.md`, `../dfir-sherlock-triage/windows-event-logs.md`,
`../dfir-sherlock-triage/answer-discipline.md`, `../dfir-sherlock-triage/toolchain.md`); older tradecraft `../ctf-forensics/windows.md` and `../ctf-forensics/linux-forensics.md`.

## Discipline
One question, one field, one verbatim record. Record with `python3 tools/hooks.py pre-flag <sherlock>-qN --value '<answer>' --source
artifact --evidence '<the record line>'`, or paste the `pre_flag_argv` that `tools/forensics/evtx_query.py --answer FIELD` built. Three
attempts in one artifact family with no new record means pivot family, not a fourth filter. A count is not a confirmation, and a timestamp
at the wrong precision is graded wrong. `field-notes.md` grows on each solve: `proposed` awaits review, `confirmed` was checked. See
`../../LEARNING_LOOP.md`.
