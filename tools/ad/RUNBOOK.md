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

## 2. Minute 5–10 — baseline, THEN assume every credential is public

Rotation is the contest's most dangerous change: it is the one most likely to
break a service, and it has to happen anyway. So write the health spec FIRST,
or the rotation happens with nothing to compare against.

- Write one `sla_check` spec per service, from that service's own happy path.
  Two or three checks that exercise the real feature beat ten that assert
  `200` on `/`.
- Save the pre-rotation baseline:
  `python3 tools/ad/sla_check.py <spec>.json --save t0-before-rotation.json`
- If it is not green before you touch anything, write down which check is red
  and why. That is the organiser's starting state, and `--compare` will
  correctly refuse to blame your patch for it.

Only now rotate. The starting image is identical for every team, so every team
already knows your default passwords, your SSH keys, your database credentials
and your API tokens. This is the single most reliable way to lose the contest.

- Rotate every password and every SSH key.
- Rotate database and application secrets, then restart what needs it.
- Remove unknown `authorized_keys` entries and unknown accounts.
- After each one, prove nothing broke:
  `python3 tools/ad/sla_check.py <spec>.json --save after.json --compare t0-before-rotation.json`
  Exit 0 green, 1 revert the change, 2 already red, 3 the spec is unusable.

## 3. Minute 10–20 — find the backdoors that shipped with the image

Organisers routinely plant persistence in the starting image. Finding it before
the other teams use it is worth more than any exploit you will write.

Look at, in order: cron and systemd timers, systemd units modified recently,
`authorized_keys` everywhere, web-accessible directories for shells, SUID
binaries, `LD_PRELOAD` and `ld.so.preload`, and any service account with a
login shell.

`skills/ad-planted-backdoor-hunt/SKILL.md` is the ordered sweep for exactly this
thirty minutes, and it names what is NOT installed here so no step waits on a tool
that does not exist; `skills/ir-live-estate-triage/SKILL.md` is the router for the
post-ransomware half. Both are **catalogue** — standard knowledge, nothing in this tree has solved one —
so treat it as a checklist, not as experience.

## 4. Minute 20–30 — stand up the loop before you attack

- Baseline capture: point a capture at each service **now**, while only the
  organiser's checker is talking to it. That capture is the baseline
  `traffic_mine.py` needs, and you cannot make it later once other teams start
  attacking. Use `dumpcap`, not `tcpdump`: measured here, `/usr/bin/dumpcap`
  carries `cap_net_admin,cap_net_raw` so it needs no sudo. Always bound it, or the
  disk fills and you lose the service to a full filesystem rather than to a bug.
  ```bash
  dumpcap -i <iface> -q -f 'tcp port <port>' -a duration:120 -w baseline.pcap
  python3 tools/ad/cap_split.py --pcap baseline.pcap --out baseline/
  ```
  Then start the live capture on a rotating file, for the rest of the contest:
  ```bash
  dumpcap -i <iface> -q -f 'tcp port <port>' -b filesize:51200 -b files:20 -w live.pcap
  ```
  Never feed `tshark -q -z follow,tcp,ascii` to the miner: it carries the server's
  response into the parsed request, and the replay you build from it then points
  your victim's own response at a third team.
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
- **Do not attack anything outside the team list.** `flag_farm.py` refuses any
  host it cannot read as ONE address or ONE hostname: a wildcard, a numeric range,
  a comma or space list, a host carrying a port, and every shell metacharacter. It
  reports every offending entry rather than the first. That guard is what makes
  "it can only reach hosts you typed" true — it cannot save you from a host list
  transcribed wrongly from the official brief, so check the list against the brief.
- **If the event forbids AI assistance, this system is for practice before the
  contest, not during it.** Read the rules before the first outbound packet.
- **Log every decision with a timestamp.** The incident commander owns this, and
  the DFIR write-up at the end is usually worth points.
- **Never write a defensive claim without its coverage boundary.** "We evicted
  it" and "nothing was exfiltrated" are what the write-up is made of, and
  neither is provable. Record the command, its verbatim output, what that
  command could NOT have seen, and one grade: `evicted-verified`,
  `evicted-unverified`, `absent-within-coverage`. One packet outside the capture
  window falsifies an unqualified "nothing left the host"; the same sentence
  bounded by that window survives it. Five fields in `EVIDENCE_POLICY.md`.
