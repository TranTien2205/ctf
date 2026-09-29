# Attack–Defense: the first thirty minutes

Printed and followed in order. The point of a runbook is that nobody has to
decide anything while the clock is running.

Written for the shape described for Security Bootcamp Arena 2026 — a
post-ransomware hand-over followed by attack–defense. **The scenario summary we
worked from is a reconstruction, not an official brief**: no topology, OS,
service list, ransomware family, CVE or scoring rule has been published. So
everything below is organised by *format*, never by a guessed vulnerability.
Adjust the moment the real brief lands.

---

## 0. Before the contest (do this at home)

- Assign the six roles and write the names down. Unassigned roles mean six
  people doing the same thing for the first half hour.
- Rehearse `tools/ad/selftest.py` and one full `flag_farm.py --once --dry-run`
  against a local dummy so nobody is reading `--help` during the contest.
- Have ready: an SSH key per operator, a password generator, a tmux/screen
  config, and a shared scratch document with one section per service.

| Role | Owns |
|---|---|
| Incident commander | priorities, the clock, and the decision log. Does not type. |
| DFIR | timeline, IOCs, root cause, what was exfiltrated |
| Recovery | bring services back, verify backups are not themselves infected |
| Blue | patches, hardening, monitoring, and `sla_check.py` |
| Red | read the service, write the exploit, run the farm |
| Automation | health checks, deploy scripts, alerting |

---

## 1. Minute 0–5 — take a snapshot before touching anything

Nothing is more expensive than destroying the evidence you will need in an hour.

- Snapshot or image every box if the platform allows it.
- Copy `/var/log`, the service configs and any ransom note to a directory that
  is not on the box.
- Record hashes of anything suspicious before you move it.
- Write down: time, hostname, listening ports, logged-in users, running
  services, and which files are encrypted.

Do **not** delete malware yet. Do **not** restore a snapshot and reconnect.

## 2. Minute 5–10 — assume every credential is public

The starting image is identical for every team, so every team already knows
your default passwords, your SSH keys, your database credentials and your API
tokens. This is the single most reliable way to lose the whole contest.

- Rotate every password and every SSH key.
- Rotate database and application secrets, then restart what needs it.
- Remove unknown `authorized_keys` entries and unknown accounts.
- Then check nothing broke: `sla_check.py <spec> --save t0.json`.

## 3. Minute 10–20 — find the backdoors that shipped with the image

Organisers routinely plant persistence in the starting image. Finding it before
the other teams use it is worth more than any exploit you will write.

Look at, in order: cron and systemd timers, systemd units modified recently,
`authorized_keys` everywhere, web-accessible directories for shells, SUID
binaries, `LD_PRELOAD` and `ld.so.preload`, and any service account with a
login shell.

The repo's `dfir-persistence-trace` skill is the reference here. It is a
**catalogue** class — standard knowledge, nothing in this tree has solved one —
so treat it as a checklist, not as experience.

## 4. Minute 20–30 — stand up the loop before you attack

- Baseline capture: point a capture at each service **now**, while only the
  organiser's checker is talking to it. That capture is the baseline
  `traffic_mine.py` needs, and you cannot make it later once other teams start
  attacking.
- `sla_check.py` spec written per service, green, and saved.
- `flag_farm.py` config filled in with the team list and the flag format, run
  once with `--dry-run` so the plumbing is proven before there is an exploit.

Only now is it worth reading the service source for bugs.

---

## The steady-state loop

```
capture ──► traffic_mine.py ──► someone else's exploit ──► flag_farm.py
   ▲                                                            │
   └──────────── patch ◄── sla_check.py --compare ◄─────────────┘
```

Every tick, ask three questions and nothing else:

1. **Is the service green?** If not, that is the only thing that matters.
2. **Did anyone new attack us?** Re-run `traffic_mine.py`; a fresh high-scoring
   request is a free exploit.
3. **Who stopped yielding flags?** `flag_farm.py` prints `immune`. A team that
   patched has just written the shortest possible description of the bug.

## Rules that are easy to break under pressure

- **Never apply a patch without `--compare`.** A patch that breaks the checker
  costs more than the exploit it stops.
- **Never delete an artifact before it is copied.** Availability is recoverable;
  evidence is not.
- **Do not patch by deleting the feature.** The checker exercises the feature.
- **Do not submit a flag twice.** Most scoreboards penalise it; `flag_farm.py`
  keeps the seen-set for you.
- **Do not attack anything outside the team list.** `flag_farm.py` refuses CIDR
  ranges on purpose.
- **Log every decision with a timestamp.** The incident commander owns this, and
  the DFIR write-up at the end is usually worth points.
