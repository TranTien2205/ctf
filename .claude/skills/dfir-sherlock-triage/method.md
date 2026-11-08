# Method - how a Sherlock is actually worked

Read this before any artifact-family file. The other files in this directory say
what a parser prints. This one says which parser to reach for, in what order, and
when to stop. A Sherlock is lost by reading the wrong artifact for an hour, not by
misreading the right one.

## The shape of the task

A Sherlock is not a flag hunt. It is a numbered list of questions against a fixed
bundle of honest system artifacts. Three consequences:

1. **The question is the router, not the file listing.** Two bundles with identical
   contents ask different things. Read every question before running anything.
2. **The artifact set is closed.** Every answer is already in the bundle. If a
   question looks unanswerable, the artifact holding it has not been parsed yet -
   there is nothing external to fetch.
3. **Questions are ordered as a narrative.** Question N-1 usually supplies the
   pivot for question N. Answering out of order throws away that gift.

## Step 0 - read all questions first, then plan once

Before the first parser runs, write the question list into the ledger and mark each
one with the artifact family you expect to answer it. This costs two minutes and it
is the single highest-return action in the whole method.

```bash
python3 tools/state.py <sherlock>-q1 --category dfir \
  --target <bundle path> --challenge-name "<Sherlock name> Q1" --event "HTB Sherlocks"
```

One question is one challenge in this tree. That is deliberate: `tools/decide.py`
budgets 5 probes per mechanism class and 25 per challenge, which is a sane budget
for one question and an absurd one for twenty. Parking question 7 and reviving it
after question 12 supplies the missing pivot is the normal path, not a failure.

## Step 1 - the question-to-artifact index

Find the question's intent in the left column. Run the cheapest artifact first; the
columns are ordered by cost, not by authority. Stop as soon as one produces the
answer with a verbatim excerpt.

| Question intent | Cheapest artifact | Second | Third |
|---|---|---|---|
| Who authenticated, and from which address | Security 4624 (logon type field) | auth.log, wtmp | RDP channel logs |
| Which authentications failed, and how many | Security 4625 (+ status/sub-status) | btmp, auth.log | Firewall log |
| Was the logon interactive, network, or remote | Security 4624 logon type 2 / 3 / 10 | RDP LocalSessionManager 21/25 | Sysmon 3 |
| What process ran | Sysmon 1 | Security 4688 | Prefetch, Amcache |
| The full command line of a process | Sysmon 1 CommandLine | Security 4688 (only if audited) | PowerShell 4104, ConsoleHost_history |
| What spawned it (parent) | Sysmon 1 ParentImage | Security 4688 creator process | process tree in a memory image |
| When something first ran | Prefetch first-run, Amcache | $MFT SI created | UserAssist |
| When something last ran, and how many times | Prefetch last-8 run times + run count | UserAssist count | Amcache |
| What script content was executed | PowerShell 4104 script block | PowerShell transcripts | ConsoleHost_history |
| What persisted, and where | SOFTWARE Run/RunOnce, SYSTEM Services | 7045 service install, 4698 task | TaskCache, startup folder, WMI subscription |
| What was downloaded | Sysmon 3 + 22, browser history | Zone.Identifier ADS host URL | pcap objects, BITS qmgr.db |
| What was exfiltrated, and how much | pcap conversation byte counts | Sysmon 3 | firewall log |
| What file was created, moved, or deleted | $J USN journal (reason flags) | $MFT SI vs FN | Recycle Bin $I records |
| Hash of a payload that is gone from disk | Amcache SHA-1 | Defender quarantine extraction | carve from the image |
| A duration in seconds | two timestamps subtracted | 4624 logon id joined to 4634 | session records in wtmp |
| The technique, as an ATT&CK id | behaviour mapped offline against the STIX bundle - `detection-and-mapping.md` section 5 | - | - |
| Which account was created, and by whom | Security 4720 (+ subject field) | SAM key last-write time | NTUSER.DAT profile creation |

## Step 2 - the pivot chains

A Sherlock answer usually sits one hop away from the previous answer. These are the
hops that pay. Each arrow is a join on a concrete field, named so the join is
mechanical rather than intuitive.

**Execution chain** - "what ran and where did it come from"
```
Amcache SHA-1
  -> carved or quarantined sample (same SHA-1)
  -> Defender DetectionHistory / MPLog (threat name, path)
  -> Sysmon 1 (Image, Hashes)        [join on file path or hash]
  -> Sysmon 1 ParentImage             [join on ParentProcessGuid]
  -> Security 4688 (same path, different audit source - use to corroborate)
  -> Sysmon 3 (network)               [join on ProcessGuid]
  -> pcap conversation                [join on 5-tuple + time window]
  -> $MFT FILE_CREATE                 [join on file path]
```

**Identity chain** - "who did it and for how long"
```
Security 4624 (Logon ID, e.g. 0x3E7-style hex)
  -> Security 4672 special privileges   [join on Logon ID]
  -> Security 4688 / Sysmon 1           [join on Logon ID or user SID]
  -> Security 4634 or 4647 logoff       [join on Logon ID -> session duration]
  -> RDP LocalSessionManager 21/25      [join on session id + user]
```

**Persistence chain** - "how did it survive a reboot"
```
SOFTWARE Run key value (path)
  -> $MFT / $J creation of that path    [join on path]
  -> Prefetch for that binary           [first run == first execution]
  -> Sysmon 1 with that Image           [confirms it actually ran]
  -> Amcache / Defender for the hash
```

**Lateral chain** - written by artifact identity, never by technique brand name
```
4624 logon type 3 where the authentication package is NTLM and Kerberos was expected
  -> 4776 credential validation on the source host
  -> 5140 / 5145 share access (which share, which file)
  -> Sysmon 1 on the destination (what ran after the logon)
  -> 4769 service ticket requests, noting the encryption type field
  -> 4662 carrying the DS-Replication-Get-Changes-All control access right,
     from an account that is not a domain controller computer account
```
That last row is how directory-replication abuse looks *in a log*. This tree
documents detection from artifacts, never the offensive procedure; see the scope
clause in `../../AGENTS.md`.

## Step 3 - when the expected artifact does not answer

Do not run a sixth variant of the same query. Change artifact family, in this order:

1. **Was the log cleared?** Security 1102 means the answer moved. Fall back to
   Prefetch, Amcache, $J, and Sysmon (a separate channel that 1102 does not clear).
2. **Is audit policy off?** 4688 with no command line means command lines were never
   audited. Sysmon 1 or PowerShell 4104 carry it instead.
3. **Is the artifact dirty?** A hive captured live needs its LOG1/LOG2 replayed
   before it reads correctly. See `registry-and-execution.md`.
4. **Is the timestamp source wrong?** See `answer-discipline.md`; a correct value in
   the wrong timezone or precision is graded wrong.
5. **Has this exact shape been solved here before?**
   `python3 tools/chain_match.py --record <sherlock>-qN`

## Step 4 - one worked question, end to end

The question: *"What was the full command line of the process that established the
outbound connection to the attacker infrastructure?"*

```
reader      inventory says Sysmon-Operational.evtx and a pcap are both present
hypothesizer the pcap names the peer; Sysmon 3 joins that peer to a ProcessGuid
writer      tshark -r capture.pcapng -q -z conv,tcp    -> peer address, byte counts
reader      the peer with the largest outbound byte count is the candidate
writer      chainsaw search -t 'Event.System.EventID: =3' <evtx dir> --json
            | jq 'select(.Event.EventData.DestinationIp=="<peer>")'
reader      that record carries ProcessGuid and Image
writer      chainsaw search -t 'Event.System.EventID: =1' <evtx dir> --json
            | jq 'select(.Event.EventData.ProcessGuid=="<guid>")'
reader      that record carries CommandLine - the verbatim answer
```

Two probes, one join, one answer. The failure mode this replaces is grepping the
whole EVTX set for a process name guessed from the scenario text.

Record it, never hand-edit the ledger:

```bash
python3 tools/hooks.py pre-flag <sherlock>-q4 --value '<the command line>' \
  --source artifact --evidence '<verbatim excerpt of the Sysmon record>'
```

`tools/hooks.py` accepts `--source artifact` and applies no flag-format regex, so a
command line, a timestamp or a bare username records cleanly.

## Discipline

- **Every answer quotes the artifact.** An answer reconstructed from the scenario
  text, from a writeup, or from what the technique "usually" does is a guess, and
  this tree labels a guess a guess.
- **A parser that errors is not evidence.** Record the transport result and mark the
  probe `inconclusive`; never upgrade it by prose.
- **The bundle may contain live malware.** Nothing in it is executed. See
  `intake-and-inventory.md` for the containment rule.
- **Budget:** 5 probes or 15 minutes per artifact family, 25 probes or 45 minutes
  per question. On exhaustion park the question and move to the next; the narrative
  ordering means a later question often hands back the missing pivot.
