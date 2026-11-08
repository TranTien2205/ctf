---
name: ir-live-estate-triage
description: >
  Router for a LIVE estate that has already been hit: services down, files
  encrypted, a ransom note, and a clock. Use when you are handed root on a
  compromised host and both recovery and investigation are scored — the
  post-incident phase of an attack-defense contest, or an incident-response lab.
  Bounds the intake so evidence survives without the service staying down, then
  routes to exactly one dfir-* class. Routes; never answers the question itself.
tags: [process, router, incident-response, live-host, recovery, timeline, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "the intake has run twenty minutes and the service is still down: restore now"
    - "a claim about what was taken has no verbatim excerpt behind it"
    - "a backup is about to be restored without being checked for the persistence"
evidence_level: catalogue
---
# Live compromised estate — Router

**Catalogue router. Nothing in this repository has solved one**, and all seven
`dfir-*` class skills it routes to are catalogue as well. Nothing below is local
experience.

## Why the Sherlock method does not transfer unchanged

`skills/dfir-sherlock-triage/` assumes a **closed bundle** and a numbered question
list: nothing changes while you work, and looking longer costs only your own time.
A live estate inverts both — the evidence changes under you and the service loses
points while you read. So the intake is **bounded by a clock**, and routing happens
after it.

## The one number that decides everything

Write it down before you start: **how long may the service stay down?** If service
availability is scored per tick and investigation is scored once at the end, then
twenty minutes of intake is affordable and two hours is not. Every decision below
resolves against that number, and the explicit trigger is:

> **Twenty minutes of intake, then restore.** Whatever is not collected by then is
> collected from the copy, not from the live host.

## First probe — copy, do not read

Reading a live host changes it. The cheapest thing that makes everything else
reversible is to get the artifacts off the box **before** touching them:

```bash
mkdir -p /evidence/{logs,configs,notes}
cp -a /var/log /evidence/logs/
cp -a /etc/cron.d /etc/systemd/system /evidence/configs/ 2>/dev/null
find / -xdev \( -name '*READ*ME*' -o -name '*RECOVER*' -o -name '*DECRYPT*' \) \
     -maxdepth 4 2>/dev/null | tee /evidence/notes/note-paths.txt
```

Then inventory and hash the copy, so every later claim can name a file whose
contents cannot have changed since:

```bash
python3 tools/forensics/artifact_inventory.py --path /evidence \
        --challenge <name> --hash --examples 3
```

**Falsifier for the whole intake:** the copy holds no log covering the hours before
the encryption, no ransom note, and no configuration newer than the image. Then
this host is not where the story is, and the next host is. Do not spend the budget
reconstructing from nothing.

## Order of work, and it is not the order of interest

1. **Copy and hash** — above. Nothing is deleted yet. Nothing is restored yet.
2. **Scope** — which hosts, which services, which data. A one-line answer per host.
3. **Restore the service** — see below. This is where the points are.
4. **Reconstruct the chain** — from the copy, with the service already up.
5. **State what was taken** — with an excerpt, or say it is unknown.
6. **Close the way in** — otherwise the restore is re-compromised.

Steps 4 and 5 happen *after* step 3 on purpose: a perfect timeline delivered with
the service still down loses.

## Restoring without restoring the intrusion

- **Dependency order, not importance order.** Datastore, then the service that
  reads it, then the thing in front of it. A service brought up before its
  datastore fails its health check and reads as "still down".
- **A backup taken after the intrusion carries the intrusion.** Before restoring
  one, check it for the same things `ad-planted-backdoor-hunt` sweeps for: start-up
  units, `authorized_keys`, web-reachable code, set-id binaries. A restored web
  shell is the commonest way a team gets hit twice by the same attacker.
- **Rotate every credential before reconnecting**, not after. The intrusion knew
  them; so does every other team if the image was shared.
- **Verify with the service's own health checks, not by eye.** Write the spec and
  keep it — it is the same spec `ad-patch-without-breaking-sla` brackets every later
  patch with:
  ```bash
  python3 tools/ad/sla_check.py <spec>.json --save restored.json
  ```

## Reconstructing the chain

Build the method around what is installed, not around a tool you wish you had.
`fls`, `mactime`, `icat`, `tsk_recover` and `bulk_extractor` are present;
`volatility3`, `plaso` and a Windows EVTX parser are **absent**, so memory images
cannot be analysed here at all and `tools/forensics/evtx_query.py` degrades to
`verdict=inconclusive`. The full table, and the one install that unlocks the most,
are in `toolchain.md` — open it only when you get to this step.

## Route on the question in front of you

| The question | Open |
|---|---|
| who logged in, from where, and did it succeed | `dfir-authentication-trace` |
| what ran, in what order, and as whom | `dfir-execution-trace` |
| what will start itself again after a reboot | `dfir-persistence-trace` |
| when did files change, and in what order | `dfir-filesystem-timeline` |
| what left the network, and how much | `dfir-network-exfil-trace` |
| what happened in the cloud control plane | `dfir-cloud-audit-trace` |
| which logs were cleared or timestamps altered | `dfir-antiforensics-trace` |
| the estate is live and another team may be inside now | `ad-planted-backdoor-hunt` |

Open **one**. A live estate makes it tempting to open four.

## Saying what was taken, honestly

The discipline is the one `EVIDENCE_POLICY.md` already sets for a bug class: a
claim needs a **verbatim excerpt**, and a timeout or an absence is not a confirm.

- "An archive of 240 MB was created at 02:14 and a 240 MB outbound transfer to
  203.0.113.9 completed at 02:19" — two artifacts, both quotable. That is a finding.
- "Data was probably exfiltrated" — no artifact. That is a hypothesis, and it is
  labelled one.
- **Absence of evidence is worth stating as absence.** "No outbound transfer larger
  than 1 MB appears in the captured window; the window begins at 01:40 and the
  intrusion predates it" is a useful, honest sentence.

## The report

The write-up is usually scored, and it is written from the timeline, not from
memory. `skills/ctf-writeup/` covers a jeopardy solve; an incident report needs
these six sections instead, each one carrying its own evidence:

| Section | Must name |
|---|---|
| Timeline | UTC, one line per event, the artifact each came from |
| Initial access | the file and line, or the log entry, that proves it |
| What the attacker did | execution, persistence, privilege, lateral — and which of those you could NOT evidence |
| Data impact | what was taken, what was merely reachable, what is unknown |
| Remediation | what changed, and the verification for each change |
| Residual risk | what is still open, and what would close it |

## What ends the triage

The copy is made and hashed; the service is green on the organiser's own checker;
one `dfir-*` class is open with one question in front of it; and every claim in the
draft report names the artifact it came from. Anything else is still triage.
