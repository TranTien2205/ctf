---
name: ad-planted-backdoor-hunt
description: >
  Find the access the organiser shipped inside the starting image, in the first
  thirty minutes, before another team uses it. Use in an attack-defense contest
  immediately after rotating credentials. This is not incident reconstruction —
  there is no timeline to build and no attacker to attribute; it is a bounded sweep
  of the places a planted foothold can live, ordered by how cheap each one is to
  check and how much it gives away.
tags: [process, method, attack-defense, defense, persistence, hardening, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "thirty minutes are spent: whatever is left goes on the list, and the loop resumes"
    - "a finding would need a restart to remove and the service is currently green"
    - "the sweep has not been bounded to hosts the event assigned you"
evidence_level: catalogue
---
# Hunting the planted foothold — Process Skill

**Catalogue method. Nothing in this repository has solved an attack-defense
contest**, and the seven `dfir-*` class skills in this tree are all catalogue too.
Treat the list below as a checklist to run, not as experience.

It is also deliberately **not** the `dfir-*` method. Those skills reconstruct what
an attacker did from a closed bundle of artifacts, answering a numbered question
list. Here the estate is live, you have root, nobody is grading your timeline, and
the only question is "what can someone else use against me in the next hour". Every
minute spent attributing is a minute not spent closing.

## Why it outranks writing an exploit

Every team booted the **same image**. Anything planted in it is planted in every
copy, so it is the one bug guaranteed to be present on every target and guaranteed
to be present on you. Finding it first is worth more than any exploit you will
write, in both directions at once.

## What is not available here, measured

Do not reach for what is not installed. On this box, measured: `debsums`, `aide`,
`rkhunter`, `chkrootkit`, `clamscan`, `auditctl` and `ausearch` are **absent**, and
so is the `yara` CLI although the Python module imports. There is no
file-integrity baseline tool and no host IDS. What replaces them is the package
manager's own verification, the filesystem's own timestamps, and a hand-made
baseline you take yourself.

## First action

The cheapest discriminating sweep, and the one that gives away the most per second
— everything that starts by itself:

```bash
systemctl list-unit-files --state=enabled
systemctl list-timers --all
ls -la /etc/cron.d /etc/cron.daily /etc/cron.hourly /var/spool/cron/crontabs 2>/dev/null
crontab -l 2>/dev/null
```

**Falsifier:** every enabled unit, timer and cron entry resolves to a distribution
package's own file, with a modification time that matches the rest of the image and
an image path under a vendor directory. Then persistence is not in the start-up
path, and the next stop is the account and key sweep below.

## The sweep, in order

Ordered by cost-to-check divided by what it gives away. Stop at thirty minutes.

1. **Start-up** — the first action above. Read the `ExecStart` of anything whose
   modification time is newer than the image, and anything whose name imitates a
   real service with one letter changed.
2. **Keys and accounts** — every `authorized_keys` on the box, not only root's;
   accounts with a login shell; accounts with an empty password field; sudo rules.
   ```bash
   find / -xdev -name authorized_keys -exec sh -c 'echo "== $1"; cat "$1"' _ {} \;
   awk -F: '$3>=0 && $7 !~ /(nologin|false)$/ {print $1, $3, $7}' /etc/passwd
   ls -la /etc/sudoers.d/ 2>/dev/null
   ```
3. **Web-reachable code** — anything under a document root that executes and was
   not shipped by the application. Compare against the application's own source
   tree or repository if you have one; a file whose timestamp differs from its
   siblings is the cheapest signal there is.
4. **Set-id binaries and loader hooks** — a short, finite list, so check it
   completely rather than sampling:
   ```bash
   find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls
   cat /etc/ld.so.preload 2>/dev/null
   env | grep -i preload
   ```
5. **Listening sockets versus services you can name.** Every listener must map to
   a service you can explain. One you cannot is either the plant or the next
   question.
   ```bash
   ss -lntup
   ```
6. **Package integrity, with what exists.** `debsums` is absent; the package
   manager can still verify on a Debian-family image:
   ```bash
   dpkg -V 2>/dev/null | head -50
   ```
   Read the output as "files that differ from the package", not as "malware".
   Configuration legitimately differs.
7. **The application's own configuration and secrets** — a token, a key or a
   database credential committed into the image is a planted foothold even when
   nobody hid it, because every team has it.

## Take a baseline while you are there

The sweep above is also the baseline. Save its output once, early, to a file off
the box. A second run an hour later, diffed against the first, answers "did
somebody get in since" — and no installed tool on this box answers that otherwise.
Timestamp the file and keep it with the decision log.

## Closing a finding without losing the service

Every removal is a patch, so it goes through the bracket in
`ad-patch-without-breaking-sla`: baseline, one change, compare. Two specific traps:

- **Do not delete before you have read and copied it.** A planted unit file names
  its author's technique, and it is also the thing another team will use — you want
  it recorded before it is gone. Availability is recoverable; the artifact is not.
- **Do not remove an account or a key a service authenticates with.** Check what
  uses it first; a planted key and a needed key look identical.

## What ends the sweep

Every enabled unit, timer, cron entry, `authorized_keys` line, set-id binary,
loader hook and listening socket is either explained by a vendor package or written
on the list with its removal command. The baseline file is saved off the box. The
clock stopped at thirty minutes whether or not the list is empty.
