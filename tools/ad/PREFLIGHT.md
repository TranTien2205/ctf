# PREFLIGHT — before 2026-10-16

**The brief is no longer a reconstruction.** The organisers have confirmed: eight
hours on **2026-10-16**, onsite, one machine per person, and the estate has been
taken over and ransomware-encrypted — you restore service, patch, and attack the
other teams, all three at once. And the line that changes the most:

> teams connect only to the organiser's private network, with **no connection to
> the internet**; no phones and no 3G/4G/5G devices during the contest.

## 0. What no internet means, before anything else

Read this first, because it decides what the rest of this toolkit is for.

**The tools work. The agents do not.** Measured today, not assumed: the whole
control plane passed inside a network namespace with only loopback and no route
anywhere —

```bash
unshare -rn python3 tools/ad/selftest.py                      # 87/87
unshare -rn sh -c 'ip link set lo up; sh lab/ad-range/dryrun.sh'   # 14/14
```

No tool under `tools/ad/` reaches the public internet. The only two that open a
socket at all are `sla_check` (your own service) and `flag_farm` (the scoreboard),
and both live on the organiser's network.

**What dies on the contest network, so do not plan around it:**

| Dead on the day | Why |
|---|---|
| any AI assistant, including this one | it reaches an API over the internet. With no internet there is no agent on the contest machine |
| `tools/writeup_search.py` | fetches public pages |
| `tools/crawl.py`, `tools/import_external.py`, `tools/github_pilot.py`, `tools/lab_sync.py` | all fetch |
| the `ctf-writeup-scout` subagent | external search |
| `sudo apt install`, `pip install`, `docker pull` | no package mirror, no registry |

So the artifacts that matter on 2026-10-16 are the ones a **human reads and a
deterministic tool executes**: `tools/ad/RUNBOOK.md` printed, this file worked
through beforehand, and `python3 tools/ad/tick.py` to answer "what next" when
there is no agent to ask. The skills and the subagents are for the **fifteen days
before** — rehearsal, not contest.

Every claim below was measured on this box; re-measure anything you depend on.

## 1. Install now, not on the day — there is no package mirror on that network

The one install that removes the largest blind spot. If the estate turns out to be
Windows-heavy, `tools/forensics/evtx_query.py` currently degrades to
`verdict=inconclusive` because no parser exists here:

```bash
sudo apt install python3-evtx libevtx-utils
python3 -c "import Evtx; print('evtx parser present')"
```

Measured candidates: `python3-evtx` **8.1.0-1**, `libevtx-utils`
**20251118-1+b1**. Both are in this box's lists **today**, and neither will be
reachable on the contest network. Install and verify the import now.

Also pull and keep locally, for the same reason, anything the rehearsal estate
needs: `docker image ls` should already show the base image
`lab/ad-range/compose.yml` uses before 2026-10-16, because `docker pull` will fail
on the day.

## 2. What you cannot install, so stop planning around it

- `volatility3` — apt Candidate is **(none)**. `sudo apt install volatility3`
  **will fail**. Memory image analysis is genuinely unavailable. A plan that
  assumes otherwise is fiction; say so to the team rather than discovering it at
  minute 40.
- No host IDS: `suricata` and `zeek` are absent. `dumpcap` + `tshark` + `scapy`
  is the whole network story.
- No file-integrity baseline: `debsums`, `aide`, `rkhunter`, `chkrootkit`,
  `clamscan` are absent. `sh tools/ad/host_snapshot.sh` plus
  `python3 tools/ad/host_diff.py` replaces them: take the baseline during the first
  thirty minutes, take another later, and diff. Pass `--after` once per host — a
  change on every host is the image, a change on one host is a person. The method
  is `skills/ad-planted-backdoor-hunt/SKILL.md`.
- Before rotating anything, run `python3 tools/ad/secret_inventory.py --root /etc`
  and read `rotation_order`. It groups by value, so the same password in four files
  is one rotation with four edits, and the widely-shared value is rotated while
  there is still time to fix what it breaks.
- No audit trail: `auditctl` and `ausearch` are absent.
- No `last`, `lastb`, `lastlog`, `utmpdump`. Walk the 384-byte struct instead.
- `pip` is EXTERNALLY-MANAGED: a plain `pip install` refuses. Use
  `sudo apt install python3-<name>`, or a venv.

## 3. Prove the plumbing offline — and prove it IS offline

Not on the day. Each of these runs with no network, and the first pair proves that
claim rather than asserting it:

```bash
unshare -rn python3 tools/ad/selftest.py
unshare -rn sh -c 'ip link set lo up; cd $(pwd) && sh lab/ad-range/dryrun.sh'
```

`unshare -rn` needs no root here (measured) and gives a namespace with no route
out, so anything that silently reached the internet fails there and passes
outside. Then the ordinary runs:

```bash
python3 tools/ad/selftest.py          # expect cases == passed, failed []
bash test/run_all.sh                  # expect PASS
python3 tools/ad/cap_split.py --from-fields tools/ad/fixtures/http_requests.fields --out /tmp/cs
python3 tools/ad/traffic_mine.py --live /tmp/cs --top 5      # expect candidates > 0
```

Then the whole rehearsal in one command. It stands up two stdlib servers on 19080
and 19081, drives every path that is otherwise first exercised during the contest,
and removes every process and temporary directory afterwards:

```bash
sh lab/ad-range/dryrun.sh
```

It prints PASS or FAIL per path and exits non-zero if any failed. Measured today:
14 checks, 14 passed. What it proves is the plumbing -- the SLA bracket catching a
real regression *and* a deleted check, the farm holding a flag through a scoreboard
outage and draining it afterwards, the capture pipeline carrying no response bytes,
and the tick decider putting availability first. What it cannot prove is the real
team host list, the real flag format and the real submission dialect: those come
from the brief.

Then one dry run of your own farm config, so nobody reads `--help` while the clock
runs:

```bash
python3 tools/ad/flag_farm.py <config>.json --once --dry-run
```

`--dry-run` HOLDS the flags rather than submitting them and says so. Nothing is
lost by rehearsing.

## 4. The go-bag

- The team host list, transcribed from the **official brief**, not from a guess.
  `flag_farm.py` refuses a range or a metacharacter; it cannot catch a typo.
- The flag regex, from the rules. Test it tonight: a capturing group is refused at
  load time, because `findall` would return the group and strip the wrapper.
- The submit URL, method, header and token, if published.
- One `sla_check` spec skeleton per expected service.
- An SSH key per operator, a password generator, a tmux layout, and one shared
  decision log with a section per service.
- `tools/ad/RUNBOOK.md`, printed. It is read while tired.

## 5. If you are behind, drop in this order

1. The lab rehearsal — keep the offline selftests.
2. Traffic mining — keep the capture running anyway; you can mine it later, but you
   cannot capture the past.
3. Your own exploit — a green service scores every tick; a bug scores once a tick.
4. Never drop: the SLA baseline before the first patch, and the evidence copy
   before the first deletion. Availability is recoverable. Evidence is not.
