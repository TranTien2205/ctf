# ATTACK_DEFENSE_BUILD_PLAN.md

This is the build plan for one evening (2026-09-29) plus one morning, ahead of an
attack-defense contest with a post-ransomware phase 1 on 2026-09-30. It ranks
every candidate change to `tools/ad/`, `tools/forensics/` and the documents around
them by what it costs to lose if the change is not made, and it names the exact
edit, the verification command and the minutes for each. The scenario below is a
**reconstruction, not an official brief** — nothing is published about topology,
OS mix, service list, ransomware family, CVEs, flag format, tick length, SLA
definition or scoring weights — so every item is organised by *format* and by
*mechanism*, and every item says what degrades if the estate turns out to be
something else.

The scenario, as reconstructed: each team is handed an enterprise-like estate that
has already been hit by ransomware. Phase 1 is post-incident — restore service,
reconstruct the chain from initial access to impact, identify what data left,
close the remaining weaknesses. Phase 2 is attack-defense against the other teams
while keeping your own services green and producing an incident write-up. Every
team starts from an identical image, so every team already knows your default
credentials.

**How to read this file.** Sections 2 and 3 are the orientation. Section 4 is the
work, in tiers; start at T0 item 1 and go down. Section 5 is the order with a
running clock. Section 6 is what to do if the evening collapses. Everything from
section 7 on is reference, risk and approval-gated proposals.

**Where this file sits in the gate.** It is a root `.md`, so the PostToolUse gate
hook does not fire on it — that hook matches `tools/`, `skills/`, `knowledge/` and
`test/` only. It *is* inside `authored_files()`, and it is **not** in
`tools/check_boundary.py`'s `DECLARES_BOUNDARY` set: measured, that set holds 12
relative paths and the bare `README.md` entry exempts the repository-root README
only. So this file may not contain any of the 17 blocked methodology substrings,
and may not write a probe-and-minute budget pair other than the two
`tools/decide.py` enforces. It is also **not** in `CONTROL_PLANE` and not under
`skills/`, so `test_every_tool_path_named_in_prose_resolves` does not read it —
which is why this plan can name `tools/ad/tick.py` before that file exists.

---

## 2. What already exists

Measured on 2026-09-29 in `/home/kali/ctf-v2`. Do not rebuild any of this; build
on it. One row per thing, with the gap it leaves.

| What exists | Path | Verified state | The gap it leaves |
|---|---|---|---|
| The attack-defense commit | `9543fb1` | HEAD. "Add tools/ad: the attack-defense control plane, with its own offline selftest" | `AGENTS.md` does not mention `tools/ad` anywhere, so an agent reading the bootstrap file cannot discover it |
| The DFIR commit | `03e013a` | Parent of HEAD. Seven bug classes, a router, `tools/forensics` | All seven classes are `catalogue`; nothing here has solved one |
| Health checks | `tools/ad/sla_check.py` | Pure `evaluate()`/`run_all()`/`compare()`. Empty spec refused. `--compare` deliberately asymmetric. Exit 1 regression, 2 not-ok, 0 green | `compare()` builds `was` from `before` but only iterates `after`, so a check that passed and is now **deleted or renamed** returns verdict `safe to keep`. Measured both cases |
| Flag farming | `tools/ad/flag_farm.py` | Refuses a config with no `authorized_event`; refuses a slash-notation CIDR host; dedupes two teams returning one flag to `new_flags: 1`; scans stdout **and** stderr | `seen.add(f)` at line 155 precedes `submit()` at line 158, and `main()` writes the `.seen` file whatever `submit_error` says. A scoreboard outage discards flags permanently |
| Traffic mining | `tools/ad/traffic_mine.py` | Ten SUSPECT patterns, scored over raw **and** URL-decoded path+query+body. Turned 4 requests into 3 ranked candidates with `$TARGET` replay templates and the victim Host stripped | `replay_template()` strips only host, content-length, connection, accept-encoding — so the attacking team's Cookie and Authorization travel into a replay aimed at a third team. And its own docstring (lines 11-12) documents a `tshark … follow,tcp,ascii` input that puts the victim's response into the parsed request body |
| Offline proof | `tools/ad/selftest.py` | 16 cases, 16 passed, `offline: true`. Ran it today | No case feeds real capture-tool output, and no case asserts the sibling-plane separation the README declares |
| Contest-day runbook | `tools/ad/RUNBOOK.md` | 115 lines. Six roles, minute 0-5 / 5-10 / 10-20 / 20-30, the steady-state diagram, six pressure rules opening with "Never apply a patch without `--compare`" | Section 2 rotates every credential at minute 5-10 while the SLA spec is not written until section 4 at minute 20-30. `grep -c tcpdump` returns **0** — section 4 says "point a capture at each service now" with no command at all. It repeats a false CIDR safety claim, and `grep -ci 'ai assistance'` returns 0 |
| The layer's own README | `tools/ad/README.md` | Explains the sibling plane, the four changed assumptions, the guards, and a "What is still missing" list of four candidate skills | Four statements are now false: "None of this has been executed", the selftest "has **not** been run", `run_all.sh` "has **not** been run", and "The gate checks that new tooling is documented" — that last one is disproved, the orphan check globs top-level `tools/*.py` only |
| DFIR tooling | `tools/forensics/{artifact_inventory,evtx_query,timeline_merge,fkit,selftest}.py` + `fixtures/` | Selftest passes | `timeline_merge.from_numeric()` has two tiers only (`MS_THRESHOLD = 10 ** 11`), so a journald microsecond `__REALTIME_TIMESTAMP` reads as milliseconds and lands outside the 1970..2200 window: journald cannot enter the tree's only timeline merger |
| DFIR skills | `skills/dfir-sherlock-triage/` (router, 11 files) + 7 class skills | All seven class skills are `catalogue` | Every one assumes a closed artifact bundle with a numbered question list. A live estate inverts that. And `skills/dfir-sherlock-triage/network-and-cloud.md:137` states `last -f` "is present here" while `last`, `lastb`, `lastlog` and `utmpdump` are all **absent** — measured, and `skills/dfir-authentication-trace/SKILL.md:158` already says so. The tree contradicts itself on a minute-three command |
| The taxonomy | `knowledge/bug-classes.json` | 32 classes: 25 web + 7 dfir | No `ad-*` class and no `ir-*` class. The file is **generated** from `build/make_bug_classes.py`; never hand-edit it |
| Knowledge | `knowledge/chains/` 69 cards, `knowledge/attempts/` 3 kill-maps, `knowledge/gadgets/` 25 | — | No chain card matches an attack-defense contest, so `tools/chain_match.py` has nothing to recall |
| The gate | `test/run_all.sh` | Passes, exit 0. Line 37 already runs `tools/ad/selftest.py` inside its tool-layer loop | Measured 71 seconds idle by the orchestrator; 189-223 seconds when timed under concurrent load. Nothing in it proves the attack-defense plane's separation, and `tools/system_eval.py` has no attack-defense decision cases |
| The gate hook | `.claude/settings.json` | PostToolUse on `Write|Edit`, matching `tools/`, `skills/`, `knowledge/`, `test/`; `timeout: 300`; `asyncRewake: true` | At 71-223 s a run, headroom against the 300 s timeout is real but not large under load. A failing gate can wake the model out of band and land an edit nobody authored |
| Boundary gate | `tools/check_boundary.py` | Required step. 17 blocked substrings, 12 exempt paths. Prints `boundary: 0 violation(s)` today | Nothing under `tools/ad/` is exempt. Test a candidate name before coining it — see T0-7 |
| Slash commands | `.claude/commands/{ctf-start,ctf-next,ctf-classify,ctf-solved,ctf-gate}.md` | All five exist | All five drive `tools/state.py`, `tools/decide.py` or `tools/hooks.py` — single-target, single-flag. None works in attack-defense |
| The agent layer | `.claude/agents/` | **Does not exist.** `.claude/workflows/` does not exist either | There is no subagent layer at all. `agent/autonomous-loop.md` says of itself "This is a suggested manual workflow, not an implemented autonomous loop", and `agent/probe-policy.json` has six category rows with no dfir row and no ad row |
| Working tree | `.g2.txt` | 277 lines of leftover gate output, untracked, and `git check-ignore -v .g2.txt` exits 1 — **not** ignored | A `git add -A` before the contest commits session garbage into history |
| Capture tooling | `dumpcap`, `tcpdump`, `tshark` | All present. `getcap` shows `/usr/bin/dumpcap cap_net_admin,cap_net_raw=eip` and `/usr/bin/tcpdump` carries **none** | `dumpcap` captures unprivileged; `tcpdump` needs sudo here. Prefer `dumpcap` in every instruction |
| Windows artifacts | — | `python3-evtx` apt Candidate **8.1.0-1**, `libevtx-utils` Candidate **20251118-1+b1** | Neither is installed, so `tools/forensics/evtx_query.py` degrades to `verdict=inconclusive` with no parser. One apt command tonight fixes it — T0-7 |
| Memory images | — | `volatility3` apt Candidate is **(none)** | `sudo apt install volatility3` **will fail**. Memory analysis is genuinely unavailable; no plan may assume otherwise |
| Free ports | — | `18080` is held by `give_to_player-edge-1`. `19080`, `19081`, `19090` measured free | Any lab must use 19080+. A compose up on 18080 fails with "port is already allocated" |
| Other absences | — | `/usr/bin/time` absent (use the shell builtin); the `yara`/`yarac` CLI absent though the Python module imports; no host IDS (`suricata`, `zeek`), no file-integrity baseline (`debsums`, `aide`) | `tcpdump` + `tshark` + `scapy` + `dpkg -V` and a hand-rolled baseline are what exist |

---

## 3. If you build only three things

### One — `ad-sla-vanished-check` (`tools/ad/sla_check.py`)

Availability is scored continuously and cannot be won back; a flag is scored once
per tick. So the guard on availability is worth more per minute than anything else
here, and that guard fails open. Reproduced directly: `compare()` builds `was`
from `before` but only iterates `after`, so `before = [index ok, store_note ok]`
against `after = [index ok]` returns verdict `"safe to keep"` — and so does a
**renamed** failing check. The tool whose entire purpose is stopping "patch by
deleting the feature" — the failure its own RUNBOOK lists as a rule — blesses
exactly that case.

The hour-four sequence is natural: the exploit comes through `/api/note`, the
operator disables `/api/note`, the `store_note` check goes red, the operator edits
the spec to stop the noise, `--compare` goes green, and the organiser's checker
marks the service down for the rest of the contest. 30 minutes. It is also the
prerequisite that makes every patch-bracket idea elsewhere in this plan
meaningful: a bracket built on a `compare()` that blesses deletions is theatre.

### Two — `ad-flag-submit-durability-core` (`tools/ad/flag_farm.py`)

The single point of failure in the tree, verified in source and end to end.
`tick()` calls `seen.add(f)` at line 155 before `submit()` at line 158, and
`main()` writes the `.seen` file regardless of `submit_error`. So a flag found
while the scoreboard is down is marked submitted **forever**, with no retry and no
recovery across a restart. At 60-second ticks across eight teams, a 90-second
outage discards roughly sixteen flags, and the only symptom is a `submit_error`
string in one JSON line of a scrolling log.

Splitting `seen` (submitted) from `pending` (observed), draining only on a real
accepted submission, persisting both, and hoisting an `ALERT` after three
consecutive failures turns the worst failure mode in the tree into a recoverable
one. One detail that is easy to get wrong: `submit()` returns `err=None` in **two
non-submitting branches** — `if dry_run or not sub.get("url")` — so a drain keyed
on `err is None` would eat flags during the `--dry-run` rehearsal the RUNBOOK
itself prescribes, and at the minute-20 state where `submit.url` is not yet known.
The drain must key on an explicit "submitted for real" flag.

### Three — `ad-scope-and-flagregex-guards` (`tools/ad/flag_farm.py`)

Two verified config-time defects, one with consequences outside the scoreboard.
The host guard rejects only slash notation: `10.60.1.*`, `10.60.1.1-50`,
`10.60.1-3.1`, comma lists, space lists, `$(id)` and `a;id` are all **accepted** —
while `tools/ad/README.md` claims "There is no discovery and no CIDR expansion, so
it can only ever reach hosts the operator typed" and `tools/ad/RUNBOOK.md` claims
"`flag_farm.py` refuses CIDR ranges on purpose". A false safety claim is worse
than none, because it is the sentence the operator trusts instead of checking, and
`nmap -sL -n` expands `10.60.1.*` to 256 hosts.

Second, in the same two functions: `run_exploit` uses
`re.findall(cfg["flag_regex"], out)` at line 108, and `findall` with a capturing
group returns the **group** — `r'FLAG\{(.*?)\}'` against `got FLAG{abc123} here`
yields `['abc123']`. Every flag would be submitted with its wrapper stripped,
rejected, and marked seen, for the whole contest. A capturing group is the natural
thing an operator writes. `re.compile(rx).groups` detects it exactly, and
switching to `finditer` with `group(0)` makes the failure arithmetically
impossible.

---

## 4. The build plan

### T0 — tonight, the first ~4 hours of productive time

240 build minutes plus roughly 7 gate fires. The gate measured **71 seconds** idle
(exit 0, PASS); the 189-223 s figures came from timing it under concurrent load.
At 71-120 s per fire that is 8-15 minutes of background gate, so 240 + ~15 = ~255
against 270 available. It fits, and it fits only because the gate is four times
cheaper than the specs first believed.

Every item here is one of: a silent permanent loss of points, a false safety claim
an operator will act on instead of checking, or a document that instructs a
near-certain self-inflicted loss. Nothing here adds a skill, a bug class, a
generated-file edit, or a new subdirectory. Order is forced in one place: three
items edit `flag_farm.py`, so durability lands and gates before the scope guards.

---

#### T0-1 · `drop-g2-session-garbage` · `/home/kali/ctf-v2/.g2.txt`, `/home/kali/ctf-v2/.gitignore`

First because it costs five minutes and clears the only unclean thing in the tree
before anything else touches it. Verified: `git check-ignore -v .g2.txt` exits 1,
so it is **not** ignored and a `git add -A` before the contest commits 277 lines of
leftover gate output into history, against the tree's own rule about committing
state. Its content was scanned: no flag shape, no credential substring, no PEM
header, no long base64 run. This is housekeeping, not an incident.

- Remove `/home/kali/ctf-v2/.g2.txt`, or move it to the session scratchpad if you
  would rather keep it. It is reproducible by re-running the gate.
- In `.gitignore`, inside the existing "Disposable caches and logs" block that
  already holds `cache/`, `*.log` and `*.sqlite3-journal`, add:
  ```
  # Hand-redirected gate output. *.log above covers the well-named case; these are
  # the ad-hoc names that leaked into the tree root.
  /.g?.txt
  gate*.txt
  ```
- Redirect future gate runs to a `.log` name so the existing rule covers them.
- Do **not** add a blanket `*.txt`. Three `.txt` files are tracked, all under
  `tools/forensics/fixtures/`: `PROVENANCE.txt`, `bundle/notes/README_first.txt`
  and `bundle/C/$Recycle.Bin/S-1-5-21-1001/$IA1B2C3.txt`.

**Verify:** `git status --porcelain` prints nothing; `git check-ignore -v gate1.txt`
names the new rule; `git ls-files '*.txt' | wc -l` still prints 3. `.gitignore` is
not under a hook-watched directory, so run the gate by hand once.

**Minutes: 5**

---

#### T0-2 · `ad-sla-vanished-check` · `/home/kali/ctf-v2/tools/ad/sla_check.py`, `/home/kali/ctf-v2/tools/ad/selftest.py`

Highest points-per-minute in the plan, and the argument is in section 3. Also
separate the exit codes: an empty spec, a missing spec file and a genuine
regression all currently exit 1, so an operator wiring `sla_check ... && deploy`
cannot tell "you broke the service" from "you typo'd the path". Nothing in the tree
consumes these codes — grepped `tools/*.py` and `test/*.py` for `tools/ad`, no hits
— so changing them breaks no caller.

- In `compare()`, also walk `before`:
  ```python
  was = {r["name"]: r["ok"] for r in before.get("results", [])}
  now = {r["name"]: r["ok"] for r in after.get("results", [])}
  vanished = [n for n, ok in was.items() if ok and n not in now]
  ```
  A vanished check that **used to pass** is a regression, not a note. Append each
  to `regressions` as `{"check": n, "reasons": [<the reason text below>], "excerpt": ""}`
  so the existing `verdict` and exit-1 path fire with no further change.
- The reason text, and the escape hatch in it is load-bearing: "this check passed
  before the patch and is no longer in the spec: a check was removed, renamed, or
  the spec was edited. Restore it, or prove the feature still works another way. If
  the removal is deliberate, re-save the baseline with `--save` — that is the legal
  move, not switching `--compare` off." Without that last sentence a blocked
  operator at hour four stops running `--compare`, which is worse than the bug.
- Keep a separate `added` list (names in `after` and not in `before`) as
  informational only. Adding checks must never block a patch.
- Update the `compare()` docstring: it promises only "a check that passed before
  and fails now" and must now also say "or is gone now".
- In `main()`, separate the failure modes and document the contract at the top of
  the file: **0** all green, no regression; **1** a regression against `--compare`,
  revert; **2** a check is failing but was already failing (or there is no
  `--compare`), your call; **3** the spec itself is unusable — missing,
  unparseable, or no checks. Wrap the `open(args.spec)` / `json.load` in a `try` and
  exit 3 on `OSError`/`ValueError`; change the existing no-checks
  `raise SystemExit(json.dumps(...))` to exit 3 as well.
- Three new `selftest.py` cases, driving `compare()` directly (pure, no socket):
  a vanished **passing** check is a regression and verdict is `REVERT THE PATCH`; a
  vanished **already-failing** check is not a regression and verdict is
  `safe to keep` (the existing case `sla: an already-broken check does not block a
  patch` must still pass); a **renamed** failing check is caught —
  `before = [index ok, store_note ok]`, `after = [index ok, store_note_v2 failing]`
  yields at least one regression.

**Verify:**
```bash
python3 tools/ad/selftest.py | python3 -c "import json,sys;d=json.load(sys.stdin);assert d['failed']==[],d['failed'];print('cases',d['cases'])"
```
Then by hand against any reachable URL: save a run with two passing checks, delete
one check from the spec, re-run with `--compare`, confirm verdict
`REVERT THE PATCH` and `echo $?` prints 1. Confirm an already-red check still lets
a patch through (`echo $?` prints 2, regressions `[]`). Confirm an empty spec and a
missing spec path both now print 3, where both print 1 today.

**Minutes: 30**

---

#### T0-3 · `ad-flag-submit-durability-core` · `/home/kali/ctf-v2/tools/ad/flag_farm.py`, `/home/kali/ctf-v2/tools/ad/selftest.py`

The single point of failure; the argument is in section 3. First of three
sequential `flag_farm.py` edits — land it, gate, then the next, or the
pending/seen bookkeeping gets broken by an interleaved edit.

- **Make `seen` mean SUBMITTED, not OBSERVED.** Add a second set `pending`: a flag
  goes to `pending` if it is in neither `seen` nor `pending`; the submission batch
  is `sorted(pending)`, so a flag from an earlier failed tick retries
  automatically; flags move `pending → seen` **only** on a real accepted
  submission. `tick()` gains `"pending_flags": len(pending)` and
  `"submitted_ok": bool`. The signature becomes
  `tick(cfg, seen, pending, dry_run=False)`; `main()` is the only caller. No
  existing selftest case calls `tick()`, so nothing else breaks.
- **Do not key the drain on `err`.** `submit()` returns `(text, None)` in two
  non-submitting branches — `if dry_run or not sub.get("url")`. Change it to return
  `(text, err, submitted_for_real: bool)`, false for dry-run and for a missing url,
  and drain only when `submitted_for_real and err is None`. When not
  `submitted_for_real`, add
  `"pending_note": "nothing was submitted (dry run, or submit.url is not set): these flags are held, not lost"`.
- **Persist both sets and alarm on an outage.** `main()`: load `<config>.seen` and
  `<config>.pending` (same one-flag-per-line format), write both every tick. Track
  consecutive failed submissions in a local counter; at 3, add **first** in the
  output dict so it survives a scrolling log:
  `"ALERT": "submission has failed for N consecutive ticks; K flags are pending. Check submit.method/format/token against the rules NOW; flags are held, not lost."`
- Five new `selftest.py` cases, driving `tick()` with `flag_farm.run_exploit`
  monkeypatched to a stub returning a fixed flag per team — no socket, no
  subprocess, which the file's docstring promises and `test/run_all.sh` depends on:
  a failed submit holds flags as `pending` not `seen`; the next successful submit
  drains `pending`; a flag already submitted is never resubmitted; a dry run does
  **not** drain; a config with no `submit.url` does **not** drain.
- The dedupe case is mandatory, not optional. Two teams returning the same flag
  giving `new_flags: 1` is real measured behaviour and must not regress.

**Verify:** the selftest as above. Then the live rehearsal, offline: a config with
`"exploit": ["printf", "FLAG1\n"]`, `"flag_regex": "FLAG[0-9]"`, and
`"submit": {"url": "http://127.0.0.1:1/flags"}`; run
`python3 tools/ad/flag_farm.py cfg.json --once` twice. Run 1 must report
`pending_flags 1`; run 2 must **still** report it pending, where today run 2 reports
`new_flags 0` and the flag is gone.

**Minutes: 35**

---

#### T0-4 · `ad-scope-and-flagregex-guards` · `/home/kali/ctf-v2/tools/ad/flag_farm.py`, `/home/kali/ctf-v2/tools/ad/selftest.py`

Third of the three `flag_farm.py` edits: the only item with off-scoreboard
consequences, plus a defect that silently invalidates every submission. The
argument is in section 3. Use the validator that was actually tested rather than a
first draft.

- Replace the host check in `load_config()` with a whitelist-shaped validator:
  ```python
  import ipaddress, re
  HOSTNAME = re.compile(r"^[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?(\.[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?)*$", re.I)
  BAD = ("/", "*", ",", " ", "\t", "\n", "\r", "?", "[", "]", ";", "|", "&",
         "$", "`", "(", ")", "\\", "'", '"', "{", "}", "<", ">", "!")
  ```
  `check_host(h)` returns a problem string or `None`: reject an empty or
  whitespace-padded host; reject any `BAD` character with a message saying a range
  or a metacharacter here becomes discovery against hosts the event did not assign
  you, and that a port belongs in the exploit argv; accept a bare IP via
  `ipaddress.ip_address` unless it is multicast, unspecified or reserved; then
  **gate the nmap-range heuristic on the string containing no letters** —
  `if re.search(r"\d-\d", s) and not any(c.isalpha() for c in s)` — or it rejects
  `web1-2.example.com`, and a guard that refuses a valid host is a guard the
  operator disables at hour four; finally require `HOSTNAME.match`.
- Allow `_` in a hostname: it carries no range or shell meaning and contest DNS
  does hand out such names. Accept bare IPv6 through `ipaddress`.
- Collect a problem for **every** offending team instead of `break`-ing on the
  first. Today a config with two CIDR hosts reports exactly one problem, so an
  operator fixing a 12-host list learns about one error per run.
- Verified accepted by this validator: `10.60.1.1`, `2001:db8::1`,
  `notes.team3.local`, `team-1.local`, `web1-2.example.com`. Verified refused:
  every notation in section 3, plus `224.0.0.1`, `0.0.0.0`, and `10.60.1.1:5000`
  with the message naming where the port goes.
- **Add a `flag_regex` guard** in `load_config`: compile it, append a problem if it
  does not compile, and append a problem if `rx.groups` is non-zero, naming the
  count and saying `re.findall` then returns the group so every flag would be
  submitted with its wrapper stripped — use `(?:...)` instead of `(...)`.
- **Belt and braces in `run_exploit`.** Replace line 108's
  `flags = sorted(set(re.findall(cfg["flag_regex"], out)))` with
  `flags = sorted({m.group(0) for m in re.finditer(cfg["flag_regex"], out)})`. Make
  this change even though the config guard exists: the guard is advice, `group(0)`
  is arithmetic.
- **Make `skip_self` loud.** Confirmed: unset, `tick()` returns
  `teams_yielding [1,2]` — you attack yourself and submit your own flag. Do not
  fail; set a warning flag in `load_config` and have `main()` print once, before
  the first tick:
  `{"warning": "skip_self is not set: your own team is in the attack list and your own flag will be submitted. Set skip_self to your team id."}`
- Eight new `selftest.py` cases: `10.60.1.*` refused; `10.60.1.1-50` refused;
  `"10.60.1.1,10.60.1.2"` refused; the space-separated pair refused; `"$(id)"`
  refused; a **positive** case asserting `10.60.1.1`, `notes.team3.local` and
  `web1-2.example.com` are all still accepted — this is the case that keeps the
  guard from being disabled; a `flag_regex` with a capturing group refused at
  `load_config`; and the extractor returning the whole match — drive the `finditer`
  expression on `"got FLAG{abc123} here"` with `r"FLAG\{(.*?)\}"` and assert
  `{"FLAG{abc123}"}`.

**Verify:** the selftest. By hand: a config with `"host": "10.60.1.*"` must exit
non-zero printing the problem list; a config with **two** bad hosts must list
**both**; the same config with two explicit hosts must be accepted; a config with
`flag_regex` `"FLAG\{(.*?)\}"` must be refused naming the group.

**Minutes: 45**

---

#### T0-5 · `cap-split` · `/home/kali/ctf-v2/tools/ad/cap_split.py` (new), `/home/kali/ctf-v2/tools/ad/selftest.py`

This repairs a written promise. `tools/ad/traffic_mine.py` lines 11-12 document
`tcpdump -i any -s0` plus `tshark -q -z follow,tcp,ascii,0` as its input, and that
pipeline was proved to put the victim's HTTP response — including a flag-shaped
string — inside the parsed request body. Measured on a rebuilt two-stream capture:
4 of 4 replay commands carried `--data-binary` holding the response, 3 of 4 had the
response blob inside `reasons` as a "parameter name", and the output held 11
occurrences of `HTTP/1.0`. So the operator follows the tool's own docstring, gets a
curl that POSTs the victim's response at another team, gets nothing, and concludes
the bug does not exist. Also confirmed: `parse_request` returns `None` for a
combined access-log line **and** for a request line with leading whitespace, so two
fallbacks other designs relied on do not exist.

Build the `tshark -T fields` **hex** variant. A working prototype of the core is
already on disk in this session's scratchpad; read it first.

- CLI: `cap_split.py --pcap cap.pcap --out reqs/ [--filter EXPR] [--port N] [--from-fields FILE] [--append] [--max-bytes N] [--exclude-src IP]... [--limit N]`.
- Primary path shells out to the verified invocation on tshark 4.0.7:
  ```
  tshark -r <pcap> -Y http.request -T fields -E occurrence=a \
    -E aggregator=$'\x1f' -E separator=$'\x1e' \
    -e frame.number -e frame.time_epoch -e ip.src -e tcp.stream \
    -e http.request.method -e http.request.uri -e http.request.version \
    -e tcp.reassembled.data -e tcp.payload
  ```
- **Read the bytes as hex, not as text.** Take
  `hexstring = (tcp.reassembled.data or tcp.payload)`, strip `:`, `unhexlify`. Text
  fields were proven irreversibly lossy: tshark renders a real CR, LF or TAB inside
  a field as the two literal characters `\r` `\n` `\t` but passes a genuine
  backslash through unchanged, so a body of `{"p":"C:\notes"}` is byte-identical to
  an escaped newline. And on a request split across two TCP segments the
  `http.request` filter fires on the **last** frame, whose `tcp.payload` holds only
  the tail — measured, 58 bytes of a 121-byte request — while
  `tcp.reassembled.data` holds the whole thing. Hex needs no unescaping at all.
- **Keep-alive is handled for free, and this is the decisive argument.** Three
  requests on **one** TCP stream emitted **three** separate rows, each correctly
  reconstructed; `-E occurrence=a` did not merge them. A `follow` dump recovers an
  unknown fraction, because the stream count is not knowable in advance — one
  measured capture put 4 requests on streams 0-3 while another put 3 on stream 0.
- **Never call `str.splitlines()` on this output.** Python treats `\x1e` (RECORD
  SEPARATOR) as a line boundary, so `splitlines()` shreds every row mid-field. This
  silently produced "rebuilt 0 requests" in a prototype run. Use
  `stdout.split("\n")` and skip blanks. `\x1f` is **not** a splitlines boundary,
  which is why it is safe as the header aggregator.
- **tshark writes harmless WARNINGs to stderr** on this box
  (`read_filter_list(): /usr/share/wireshark/cfilters line 1 …`). Non-empty stderr
  is not an error; never fail on it and never mix it into stdout.
- Rebuild `METHOD SP uri SP version CRLF` + each header + CRLF + CRLF + body. Write
  to `out/<seq:04d>-s<stream>.txt` in `frame.time_epoch` order, binary mode. Never
  write the response. Skip a record with no method.
- Factor as `rebuild(fields_list) -> str|None` and `strip_follow(text) -> list[str]`,
  both pure, both driven by the selftest with no tshark present. `--from-fields`
  reads a saved tshark run instead of shelling out — the escape hatch when field
  names drift, **and** the seam that keeps the selftest subprocess-free.
- stdout JSON: `{"mode":"cap-split","pcap":…,"out":…,"requests":N,"streams":N,"skipped":N,"tshark":"<version line>","hosts_seen":[…],"next":"python3 tools/ad/traffic_mine.py --baseline <baseline-dir> --live <out> --top 10"}`.
  Print the tshark version so a field-name drift is visible rather than silent.
- Guards: if `shutil.which("tshark")` is `None`, print an error JSON naming
  `--from-fields` as the fallback and exit 2 — no traceback. Refuse to write into a
  non-empty directory without `--append`; mixing baseline and live destroys the only
  signal `traffic_mine` has. Do the `which()` probe **inside a function**:
  `selftest.py` imports its siblings at module scope and an import-time probe would
  kill all cases.
- Fixture `tools/ad/fixtures/http_requests.fields`: saved tshark field output
  including one body holding a `|` and a TAB, one multi-segment record, one with no
  body, one malformed. Extension `.fields` deliberately — outside the gate's scanned
  suffixes. Do **not** commit a `.pcap`: `*.pcap` is gitignored and the fixture
  would be silently untracked.
- Do **not** wire this into `tools/ad/selftest.py` via a subprocess or a scapy
  import. That selftest runs inside the gate and is pure-function by design; a
  non-stdlib import there would make the gate depend on scapy for the first time.
- **Include the regression case that makes tonight's defect permanently visible to
  the gate:** feed `rebuild()`'s GET output through `traffic_mine.parse_request` +
  `replay_template` and assert `--data-binary` is **not** in the command and
  `HTTP/1.0` is **not** in the command; then the same for the POST tuple, asserting
  `--data-binary` **is** present. The existing case `mine: the replay template drops
  Host` asserts `--data-binary` is present on a POST it authored, so keep the two
  distinguished by method or they read as contradictory.
- Fix `tools/ad/traffic_mine.py`'s docstring in the same pass: replace the `tcpdump`
  line with the bounded `dumpcap` one from T0-6 and the `follow` line with
  `python3 tools/ad/cap_split.py --pcap cap.pcap --out reqs/`, and delete the claim
  that follow output is this shape.

**Verify:** offline,
`python3 tools/ad/cap_split.py --from-fields tools/ad/fixtures/http_requests.fields --out /tmp/live`
then `python3 tools/ad/traffic_mine.py --live /tmp/live --top 5` must report
`candidates > 0`. Live, on a free port:
```bash
python3 -m http.server 19080 --bind 127.0.0.1 &
dumpcap -i lo -q -f 'tcp port 19080' -a duration:15 -w /tmp/c.pcap &
curl -s 'http://127.0.0.1:19080/api/note?id=1'
curl -s 'http://127.0.0.1:19080/static?f=../../flags/current'
python3 tools/ad/cap_split.py --pcap /tmp/c.pcap --out /tmp/reqs
python3 tools/ad/traffic_mine.py --live /tmp/reqs --top 5 | grep -c 'HTTP/1.0'   # must be 0
```
The same pipeline through `tshark -q -z follow,tcp,ascii,<n>` prints 11.

**Minutes: 45**

---

#### T0-6 · `ad-runbook-ordering-and-capture` · `/home/kali/ctf-v2/tools/ad/RUNBOOK.md`

The one file that gets printed and read while tired, and it currently instructs two
near-certain losses. Section 2 rotates every credential at minute 5-10 while the
SLA spec is not written until section 4 at minute 20-30, so the contest's most
dangerous change happens with nothing to compare against. Section 4 says "point a
capture at each service **now**" with **no command at all** —
`grep -c tcpdump tools/ad/RUNBOOK.md` returns 0 — and the command in
`traffic_mine.py`'s docstring is unbounded, which fills the disk and takes down the
availability the runbook exists to protect. Write all the edits in one pass: the
file is under `tools/`, so each save fires the background gate.

- **Move the SLA spec earlier.** Retitle section 2 to "Minute 5-10 — baseline, THEN
  assume every credential is public" and open it with three bullets before any
  rotation bullet: write the `sla_check` spec for each service first, from the
  service's own happy path (two or three checks that exercise the real feature beat
  ten that assert 200 on `/`); save the **pre**-rotation baseline
  `sla_check.py notes.json --save t0-before-rotation.json`, and if it is not green
  before you touch anything, write down which check is red and why — that is the
  organiser's starting state and `--compare` will correctly refuse to blame your
  patch for it; then rotate **one credential class at a time** (app secrets, then
  database, then SSH), running `--compare t0-before-rotation.json` after **each**
  class rather than after all of them. In section 4, replace the spec-writing bullet
  with "the spec written in section 2 is still green; re-save it as `t0.json` now
  that the rotation is done".
- **Add the missing capture command** to section 4, bounded, `dumpcap` first:
  ```
  dumpcap -i <if> -q -f 'tcp port <p>' -w /var/tmp/cap/notes.pcap -b filesize:102400 -b files:10
  python3 tools/ad/cap_split.py --pcap /var/tmp/cap/notes.pcap --out reqs/
  # tcpdump equivalent needs sudo here:
  #   sudo tcpdump -i any -s 1600 -W 10 -C 100 -w /var/tmp/cap/notes.pcap 'tcp port <p>'
  ```
  with two sentences: the ring buffer means the capture cannot fill the disk and take
  your own service down, so put the files on a filesystem the service does not write
  to and check `df -h` every time you check the scoreboard; and `getcap` shows
  `/usr/bin/dumpcap cap_net_admin,cap_net_raw=eip` while `/usr/bin/tcpdump` carries
  none, so `dumpcap` needs no sudo here and `tcpdump` does. Add one line that the
  number of TCP streams is not knowable in advance — 4 requests on 4 streams in one
  measurement, 3 on 1 in another — which is why `cap_split.py` exists.
- **Add the missing-baseline fallback.** In a post-ransomware phase 1 the service
  may not be up at minute 20, and with an empty baseline `/`, `/login` and
  `/static/app.js` all score 5 with identical reasons. Write: if the service is not
  up in time to capture the organiser's checker, build the baseline from your own
  `sla_check` run — start the capture, run `sla_check.py notes.json`, stop it; your
  spec is the happy path, so the requests it makes are a legitimate definition of
  normal traffic. Do **not** write that an application access log substitutes:
  measured, `traffic_mine.parse_request` returns `None` on a combined log line.
- **Add the abort ladder** — what to drop, in order. Drop 1: write-up polish (keep
  raw notes and timestamps). Drop 2: exfiltration scope in full — keep the one-line
  answer and the evidence path. Drop 3: new exploit development; switch entirely to
  `traffic_mine`, because another team's working exploit costs minutes and your own
  costs hours. Drop 4: the persistence hunt beyond cron, systemd timers and
  `authorized_keys`. Drop 5: full timeline reconstruction — keep initial access and
  impact, drop the middle. Drop 6: farming teams that have gone immune. **Never
  drop, at any level of panic:** credential rotation, `sla_check --compare` before
  every patch, and the baseline capture. Each is unrecoverable later, and the
  baseline literally cannot be recreated once other teams start attacking.
- **Add the team-size mapping**, most-likely-first. Six or more: as tabled today.
  Four: the incident commander also takes automation; DFIR and recovery merge; blue
  and red stay separate, and that split must survive longest, because the same
  person cannot patch and exploit without dropping one. Three:
  commander+automation, blue+recovery, red+DFIR; the commander still does not type.
  Two: person A owns green (rotate, `sla_check`, patch), person B owns points
  (`traffic_mine`, `flag_farm`, exploits); DFIR becomes a timeboxed pass over
  section 3 and then a written note. One person plus agents: the human owns exactly
  three things an agent must **never** do — **restart a service, delete an artifact,
  claim a flag** — and the order for one person is section 2 (rotate), then section 4
  (baseline capture, which cannot be made later), then section 3 (persistence hunt,
  timeboxed), then exploit; say plainly that section 1's snapshot is the first
  casualty of being alone, and that every agent-proposed patch still goes through
  `sla_check --compare` because an agent cannot judge whether it broke the checker.
  At every size: one person owns the decision log, and it is never the person typing.
- **Add the order-of-volatility line** to section 1, because it is the ranking that
  decides what a restart destroys: the socket table and process list die at the
  first service restart and are not recoverable; a deleted-but-running binary dies
  when the process exits and is recoverable only while it runs
  (`cp /proc/<pid>/exe`); logs survive a restart only partly, because a restart
  rotates them; filesystem metadata is destroyed irreversibly by restoring a
  snapshot, so build the metadata baseline before the first restore; the encrypted
  files themselves are already the impact and are not going anywhere.
- **Add three rules** to "Rules that are easy to break under pressure": never let an
  agent or a script restart a service on its own — a restart is a decision with an
  availability cost, the incident commander makes it and it goes in the decision log
  with a timestamp; **if the event forbids AI assistance, close this toolkit**
  (`CLAUDE.md` scopes it to practice before such a contest, and
  `grep -ci 'ai assistance'` returns 0 in this file today); and check `df -h` and the
  capture directory every time you check the scoreboard.
- **Add the egress deadman**, one paragraph, because it is the single most reusable
  safety pattern and it applies to the patch ladder too:
  ```bash
  sudo -v                                   # no privilege here means no rollback at all
  sudo iptables-save > /tmp/ad/iptables.pre
  test -s /tmp/ad/iptables.pre || echo "EMPTY ROLLBACK - STOP"
  ( sleep 120; sudo iptables-restore < /tmp/ad/iptables.pre ) &
  ```
  The `test -s` guard is what makes it safe: an unprivileged `iptables-save` writes a
  zero-byte file that looks armed. This makes a wrong filter cost 120 seconds.
- **Delete the false CIDR claim.** Replace "`flag_farm.py` refuses CIDR ranges on
  purpose" with, once T0-4 has landed, "`flag_farm.py` refuses any host that is not
  a single unicast address or a hostname: ranges, wildcards, comma lists and
  metacharacters are each refused with a named problem." If T0-4 has not landed,
  write the measured truth instead: it refuses slash notation and nothing more, so
  **you** are the guard — paste the organiser's published team list into the config
  and have a second person read it back before the first non-dry-run tick.
- **Fix the tree's self-contradiction while you are here**, because it is a
  minute-three command that fails: `skills/dfir-sherlock-triage/network-and-cloud.md`
  lines 133-137 tell the operator to run `last -f wtmp` and state that `last -f` "is
  present here", while `last`, `lastb`, `lastlog` and `utmpdump` are all **absent**
  (measured) and `skills/dfir-authentication-trace/SKILL.md:158` already says so.
  Replace those lines with a pointer to the 384-byte struct walk in that second file,
  keep the `auth.log` greps unchanged, and write only the invariant (384 bytes per
  record, count = size / 384) — **not** an absolute byte count, because
  `/var/log/wtmp` grows with every login and a hardcoded number is how the first
  contradiction happened. This edit is under `skills/`, so it fires the gate; batch
  it with nothing else.
- **Gate trap:** this file is an authored file, so do not write a probe-and-minute
  budget pair other than the two `tools/decide.py` enforces. Use ticks and counts.

**Verify:** `grep -c tcpdump tools/ad/RUNBOOK.md` returns 1 (the one explanatory
clause; it returns 0 today, so this is a real signal).
`grep -c 'dumpcap' tools/ad/RUNBOOK.md` is at least 1.
`grep -c 'before-rotation' tools/ad/RUNBOOK.md` is at least 1 and its line number is
**below** the section-2 heading and **above** the first rotation bullet.
`grep -ci 'ai assistance' tools/ad/RUNBOOK.md` returns 1.
`grep -c 'refuses CIDR ranges' tools/ad/RUNBOOK.md` returns 0.
`grep -rn 'last -f' skills/ | grep -v authentication-trace` returns nothing.
Then extract and run every command in the runbook:
`grep -oE '(python3|bash|dumpcap|docker) [^`]+' tools/ad/RUNBOOK.md | sort -u`.
Finally the real test, tonight and not tomorrow: one operator reads sections 0-4
aloud and performs them against a local dummy service, timed. That rehearsal is
30-50 minutes of **human** time and is not counted in the minutes below; if minute
0-30 takes fifty minutes in rehearsal, cut steps tonight rather than on the day.

**Minutes: 45**

---

#### T0-7 · `ad-preflight-tonight` · `/home/kali/ctf-v2/tools/ad/PREFLIGHT.md` (new)

The only item that is worthless if it slips to tomorrow: apt availability on the
contest network is unknown and there is no second chance at 09:00. The install
question was verified rather than guessed — `python3-evtx` Candidate **8.1.0-1** and
`libevtx-utils` Candidate **20251118-1+b1** are in this box's lists, so one command
tonight removes the largest blind spot (a Windows-heavy estate, where
`tools/forensics/evtx_query.py` currently degrades to `verdict=inconclusive` with no
parser). But `volatility3` Candidate is **(none)**, so `sudo apt install volatility3`
**will fail** and memory analysis is genuinely unavailable; a plan that assumes
otherwise is a fiction.

One screen, imperative, five sections.

- **Section 1 — run these tonight, in this order.** Every line a command followed by
  the check that proves it worked. Mark the block UNVERIFIED-UNTIL-RUN, because apt
  needs network:
  ```
  sudo apt install --no-install-recommends python3-evtx libevtx-utils
    verify: python3 -c "import Evtx; print(Evtx.__file__)"   AND   command -v evtx_dump
    why:    without it a Windows estate is unreadable. Candidates 8.1.0-1 and
            20251118-1+b1 were in this box's package lists on 2026-09-29.
  ```
  Then a NOT AVAILABLE list with the reason, so nobody plans around a fiction:
  `volatility3` apt Candidate (none) — no memory-image analysis; if a memory dump
  appears, the honest answer is `strings` plus `bulk_extractor`, both present, not
  volatility. The `yara`/`yarac` CLI is absent though the Python module imports
  (`yara` Candidate 4.5.8-1 if you want the CLI), so write rules against the module.
  `pip install` refuses here — pip is EXTERNALLY-MANAGED, so only
  `sudo apt install python3-<x>` or a venv works. A host IDS and a file-integrity
  baseline are both absent and must **not** be installed under time pressure: they
  need tuning and a clean baseline you no longer have, and a ruleset reload on a
  scored interface at hour four is self-inflicted SLA loss. The substitutes are
  `dumpcap` + `tshark` + `cap_split` for network and `dpkg -V` / `rpm -Va` plus a
  `find / -newermt <T>` snapshot for integrity.
- **Section 2 — what degrades if the estate is not what we guessed.** A
  three-column table: assumption / what breaks / cheapest move on the day.
  Windows-heavy: EVTX unreadable → the apt line above, else
  `tools/forensics/artifact_inventory.py` plus `strings` over the `.evtx`, which
  recovers command lines and loses structure and timestamps. Containerised or
  orchestrated: `tools/ad` still works because services still speak HTTP, but
  `tcpdump -i any` inside a container needs a sidecar or host networking, and an
  access log is **not** a drop-in `traffic_mine` input (measured), so the fallback is
  a small proxy that writes raw requests or the `sla_check`-capture trick in RUNBOOK
  section 4. No source for the services: `traffic_mine` becomes the **primary**
  exploit source, which promotes T1-3 and the baseline fallback above everything
  else. Availability-dominant scoring: `flag_farm`'s value collapses and `sla_check`
  becomes the only tool that matters. Flags that do not rotate: already safe — the
  seen-set submits a flag once and the dedupe is measured. Unknown tick length: one
  config line, `tick_seconds`; do not build for it.
- **Section 3 — the corrected gate cost.** `bash test/run_all.sh` measured **71
  seconds** idle, exit 0, PASS; 189-223 seconds when timed under concurrent load.
  `/usr/bin/time` is **absent** on this box, so use the shell builtin. The
  PostToolUse hook in `.claude/settings.json` runs the gate in the background after
  any Write or Edit under `tools/`, `skills/`, `knowledge/` or `test/`, with
  `timeout: 300` and `asyncRewake: true`. Consequences to write down: batch edits
  into one write per file; during the contest run `bash test/run_all.sh` by hand
  rather than trusting the hook, because under load the run can approach the timeout
  and be killed with the result unknown; and after any session that touched those
  four directories, run `git diff` before committing, because a failing gate can
  wake the model out of band and land an edit nobody authored.
- **Section 4 — two gate traps that bite a documentation edit. Write this section
  without spelling any blocked token.** Proved: writing those tokens into a file
  under `tools/ad/` makes `python3 tools/check_boundary.py` return 2 violations and
  exit 1, because `DECLARES_BOUNDARY` keys on the relative path so only the **root**
  `README.md` is exempt — `tools/ad/README.md`, this file and any
  `skills/<id>/SKILL.md` are all scanned. So write: `tools/check_boundary.py` is a
  required step in `test/run_all.sh`; it lower-cases every `.py`/`.md`/`.yaml`/
  `.json`/`.sh` outside its skip list and fails on 17 machine-and-directory
  methodology substrings held in its `BLOCKED` tuple. Read that tuple in the file
  before naming any tool or coining any skill id; do not guess, and do not copy a
  blocked token into a tracked file in order to warn about it. Test a candidate with:
  ```bash
  python3 -c "import sys;sys.path.insert(0,'tools');import check_boundary as cb;print([t for t in cb.BLOCKED if t in 'YOUR-CANDIDATE'.lower()])"
  ```
  An empty list is clean. One of the credential-testing tools that is actually
  installed on this box is **not** clean, and the one-liner names which. Also record
  the second trap: the budget-phrase test scans every authored file, `tools/ad/*.md`
  included, for a probe-and-minute pair and permits only the two `tools/decide.py`
  enforces. And record what **is** safe, because the runbook's persistence hunt
  depends on it: the phrase "cron, systemd timers, `authorized_keys`, SUID and
  `LD_PRELOAD`" tests clean, which is why RUNBOOK section 3 passes the gate today.
- **Section 5 — before the first outbound packet.** Five lines: the organiser's team
  list is pasted into the `flag_farm` config verbatim and read back by a second
  person; `authorized_event` names the real contest; `skip_self` is set to your own
  team id (unset means you attack yourself and submit your own flag — measured);
  `flag_regex` has **no** capturing group (measured: `findall` then returns the group
  and every flag is submitted with its wrapper stripped); and the first run is
  `--dry-run --once` and its output is **read**, not assumed. Plus the minute-zero
  dialect probe: submit one flag by hand with `curl -i` and copy the exact request
  into the config before the farm ever runs unattended. Plus one line for a defect
  that tracebacks rather than erroring cleanly: `sla_check.run_all()` does a bare
  `spec["base"]` subscript, so a spec missing `base` raises `KeyError` instead of
  producing the tool's own error JSON — check every spec has a `base` before the
  contest.

**Verify:** `python3 tools/check_boundary.py` prints `boundary: 0 violation(s)`
**immediately after saving this file** rather than waiting for the background gate —
this file is the one most likely to trip it, because its whole job is to talk about
tooling. Then `bash -c 'time bash test/run_all.sh'` prints a real figure and exit 0.
`apt-cache policy volatility3 | grep Candidate` prints `(none)`. `command -v yara`
prints nothing while `python3 -c 'import yara'` succeeds. When the apt line is
actually run, paste the two verify commands' real output into the file and replace
UNVERIFIED with the date and the installed version. Then run `bash test/run_all.sh`
once before bed: installing `python3-evtx` pulls dependencies into a working system
the night before a contest, and a broken `python3` at 09:00 costs more than EVTX
parsing buys.

**Minutes: 35**

---

### T1 — tonight only if T0 lands early

165 minutes total. Treat it as a ranked queue, not a commitment; realistically one
or two of these in the last hour, and anything untouched slides to the morning
ahead of T2. None of these prevents a silent permanent loss, which is why they sit
behind T0. They are the interpretation aids and the rehearsal: they make T0's fixes
usable and, in the dry run's case, prove they work.

---

#### T1-1 · `ad-readme-corrections` · `/home/kali/ctf-v2/tools/ad/README.md` — 20 min

First in T1 because one of its three false statements is a safety claim. Verified by
grep: "None of this has been executed" (the selftest is 16/16 and the gate passes),
"can only ever reach hosts the operator typed" (false for five notations tested),
and "The gate checks that new tooling is documented, so it will likely fail" —
disproved precisely: `test_every_tool_is_named_somewhere` globs
`(ROOT/'tools').glob('*.py')`, top level only, so nothing under `tools/ad/` is
covered and the gate passes today with `tools/ad` absent from `AGENTS.md`.

- Replace the whole Status section with a measured one, dated: selftest 16 cases /
  16 passed / offline; `bash test/run_all.sh` passes with `tools/ad/selftest.py` in
  its tool-layer loop at line 37, measured 71 s idle; and the runtime checks —
  `flag_farm` refuses a config with no `authorized_event` and a slash-notation CIDR
  and dedupes two teams returning one flag to `new_flags: 1`; `sla_check` refuses an
  empty spec and its `--compare` is deliberately asymmetric; `traffic_mine` turned 4
  requests into 3 ranked candidates. Retitle the four-defect list "Defects found by
  reading the code before it ever ran" so it reads as history rather than a live
  warning.
- State the gate fact **precisely** rather than as "there is no such check", or the
  next builder orphans a top-level tool: `test_every_tool_is_named_somewhere` globs
  top-level `tools/*.py` only, so a tool in a subdirectory is invisible to it; the
  separate `test_every_tool_path_named_in_prose_resolves` **does** match
  `tools/ad/<name>.py` wherever it is written and requires the file to exist, so the
  proposed `AGENTS.md` rows are safe to add once the files exist.
- Rewrite the Guards paragraph to claim only what the code does, after T0-4. Note
  the precise mechanism: `flag_farm` runs the exploit through
  `subprocess.run(argv)` with **no** `shell=True`, so a metacharacter in a host is
  not a shell injection into `flag_farm` itself — the exposure is a range reaching a
  tool the operator's own exploit shells out to (`nmap -sL -n` expands `10.60.1.*`
  to 256 hosts) or an exploit script using `$1` unquoted.
- Cut the four-candidate skill wishlist to one line pointing at `PREFLIGHT.md` for
  the reasoning. A ranked wishlist in the README is an invitation to spend the
  evening on it.
- Fold in T1-2's README half if that item lands, so this file is written **once**:
  two edits to one file cost two gate runs and risk a collision.
- Depends on T0-4 so the Guards paragraph is written once.

**Verify:** `grep -c 'None of this has been executed' tools/ad/README.md` → 0;
`grep -c 'can only ever reach hosts the operator typed'` → 0;
`grep -c 'gate checks that new tooling'` → 0;
`python3 tools/check_boundary.py` → 0 violations.

---

#### T1-2 · `ad-immune-honesty` · `/home/kali/ctf-v2/tools/ad/flag_farm.py` — 30 min

`README.md` has a section titled "The one output to read every tick" about `immune`,
and `tick()` computes it from `not r["flags"]` without consulting the `status` field
it already records — so a timeout, a crashed exploit and a genuine patch land in one
list. Measured: four stubbed results gave `immune [2,3,4]` with statuses `timeout`,
`error: [Errno 2] No such file` and a clean `exit 0`. In a post-ransomware phase 1,
hosts being down is the default state for the first hour, so at the moment `immune`
is trusted most it is mostly noise and the operator spends the most expensive half
hour hunting a patch on a box that is simply offline. This is the attack-defense
side of the tree's own rule that a timeout is evidence about availability, not about
a bug. Fourth sequential `flag_farm.py` edit.

- Bucket the non-yielding teams from the status values `run_exploit` actually
  produces (`"timeout"`, `"error: <exc>"`, `"ok"`, `"exit <code>"`):
  `timeout → unreachable`, `startswith("error:") → exploit_broken`, otherwise
  `silent`.
- Emit three lists and keep `immune` as the honest subset only — the `silent` bucket
  — with a note each: the `immune` note says these teams ran the exploit to
  completion and returned nothing while others returned flags, so they have patched
  and their patch is the shortest description of the bug; the `unreachable` note
  says a timeout is availability evidence about **them**, not evidence that they
  patched, and is worth one manual `curl`, not a patch hunt; the `exploit_broken`
  note says fix your own exploit before reading anything into the result. Each note
  is non-empty only when its list is.
- If `exploit_broken` covers **every** team, hoist a top-level
  `"ALERT": "the exploit failed to run against every team; this is a local problem"`
  — a wrong interpreter path otherwise reads as the entire field patching
  simultaneously.
- Two selftest cases against a stubbed `run_exploit`: one yielding, one timeout, one
  exploit-error, one silent → `immune` holds the silent team only and each note is
  non-empty only when its list is; every team returning `error:` → the top-level
  `ALERT` key is present.
- The README half of this change belongs in T1-1.

**Verify:** the selftest, plus by eye on real output: a `--once` rehearsal against
one reachable and one unreachable host must put them in different lists.
`grep -c 'unreachable_note' tools/ad/flag_farm.py` → 1.

---

#### T1-3 · `ad-replay-credential-strip` · `/home/kali/ctf-v2/tools/ad/traffic_mine.py` — 25 min

`replay_template` strips only host, content-length, connection and accept-encoding,
so the attacking team's `Cookie`, `Authorization` and `X-Team-Token` travel into a
replay aimed at a third team. Measured: the emitted curl carried
`-H "cookie: session=…"`, `-H "authorization: Bearer TEAM4_TOKEN"` and
`-H "x-team-token: team4secret"`. The replay 401s, the operator records that team as
immune, and the highest-return move in attack-defense silently stops working for
authenticated endpoints — which is most of them. It also puts another team's bearer
token into shell history and into the scored write-up, against the tree's rule on
committing credentials.

- Split header handling: `TRANSPORT` (dropped silently) = host, content-length,
  connection, accept-encoding, keep-alive, te, transfer-encoding, upgrade, expect.
  `IDENTITY` (dropped **with a note**) = cookie, authorization, x-team-token,
  x-api-key, x-auth-token, proxy-authorization, x-csrf-token, x-xsrf-token.
- Return a dict:
  `{"curl": "<command, $TARGET, no credentials>", "stripped_identity": [...], "note": "this request was authenticated as the ATTACKING team; the replay will 401 until you substitute your own credential for the target."}`.
  In `main()`, keep the key `replay` holding the **string** so nothing that reads it
  breaks, and add `stripped_identity` and `replay_needs_auth` beside it. Print the
  note next to the curl, not buried.
- Fold in the one-line `--path-as-is` fix while in the same function: `curl`'s own
  help on this box says `--path-as-is  Do not squash .. sequences in URL path`, so
  without it a traversal candidate — worth 4 points in the scorer — replays as a
  clean 404 and gets discarded. Change the opening element to
  `["curl -sS -i --path-as-is --max-time 10"]`. Do not also add `--globoff`:
  separate concern, untested.
- **Mandatory and missed by the original spec:** changing the return type breaks the
  existing selftest case `mine: the replay template drops Host and parameterises the
  target`, which calls `.lower()` on the result and would raise `AttributeError`.
  Update it in the **same write**, keeping all four of its assertions, reading the
  `["curl"]` value.
- Two new cases: a request with Cookie + Authorization emits a curl containing
  neither substring while `stripped_identity` names both; a request with only
  ordinary headers still emits them, so the strip is narrow.

**Verify:** the selftest, and confirm the **updated** existing case still passes —
that is the one that proves the return-type change did not break the harness. End to
end with one authenticated raw request:
`python3 tools/ad/traffic_mine.py --live <dir> | grep -c 'Bearer\|session='` must be
0 in the replay field. Confirm the replay string now begins
`curl -sS -i --path-as-is --max-time 10`.

---

#### T1-4 · `ad-submit-dialect-configurable` · `/home/kali/ctf-v2/tools/ad/flag_farm.py` — 25 min

`submit()` hardcodes `method="PUT"` with a bare JSON array against an API nobody has
published. With durability landed, a wrong dialect no longer destroys flags, so this
buys a reviewed config change instead of a hand-edit of Python at minute zero.

- Split `build_submission(cfg, flags) -> (method, url, headers, body_bytes)` out as
  a **pure** function over three formats: `json-array` (`json.dumps(list(flags))`,
  `application/json`), `newline` (`"\n".join(flags) + "\n"`, `text/plain`), and
  `form` (`urlencode([(field, f) for f in flags])`,
  `application/x-www-form-urlencoded`). Attach the token header only when **both**
  `header` and `token` are set, as today.
- Keep `PUT` and `json-array` as defaults so any config already written behaves
  identically. Do **not** swap the default to `POST`: that trades one guess for
  another.
- Refuse an unknown `submit.format` at startup, naming the three valid values — a
  typo found at minute zero beats one found at minute sixty.
- Remember `import urllib.parse`: the module imports only `urllib.error` and
  `urllib.request` today, and `urllib.parse` is not implicitly available from those.
- Warning carried from the durability work: the dry-run short-circuit tests
  `not sub.get("url")`, so any new branch must widen it or `--dry-run` starts
  submitting.
- Two selftest cases: assert method, Content-Type and exact body bytes for all three
  formats, including that the token header appears only when both keys are set; and
  an unknown format raises `ValueError`.

**Verify:** the selftest. By hand, a config with `"format": "nonsense"` is refused at
startup naming the three valid values; a config with `"newline"` and a refused
`submit.url` still reports the flag as pending, proving durability is unchanged.

---

#### T1-5 · `ad-ledger-template` · `/home/kali/ctf-v2/tools/ad/ledger.template.json` (new) — 15 min

Fifteen minutes whose value survives every other item being unfinished: filled in
tonight it is a printed per-service intake checklist with the rollback commands on
it. It is also the schema the morning's `tick.py` reads.

- A committed JSON template with `schema_version`, `service`, `authorized_event`,
  `phase` (`intake` | `steady`), `tick_seconds`, a `paths` block (`sla_spec`,
  `sla_saves`, `capture_baseline`, `capture_live`, `mined`, `farm_config`,
  `farm_log`), an `intake` list of `{step, done, at, note}`, and three empty arrays:
  `exploit_ideas`, `patches`, `claims`.
- The eight intake steps, in this order: `snapshot-before-touching`,
  `evidence-copied-off-box`, `sla-spec-written-and-green`, `credentials-rotated`,
  `unknown-keys-and-accounts-removed`, `planted-persistence-swept`,
  `baseline-capture-started`, `farm-dry-run-proven`.
- **One ordering correction against the runbook:** `sla-spec-written-and-green` must
  come **third**, before `credentials-rotated`, because RUNBOOK section 2 ends with a
  `sla_check --save` that cannot run without a spec. This matches T0-6's reordering.
- Default location `runs/<service>/ledger.json`. Confirmed:
  `git check-ignore -v runs/notes/ledger.json` resolves to `.gitignore:18`
  `**/runs/`, so team hosts and tokens stay out of git with no `.gitignore` edit.
  Note the flip side: `*.seen` is ignored **nowhere else**, so a farm config left
  outside `runs/` puts real flags into history.
- Gate constraints: this lands under `tools/` with a `.json` suffix, so it **is** an
  authored file — no budget-pair phrase, no hardcoded tree root, English only, and no
  blocked token.

**Verify:**
```bash
python3 -c "import json;d=json.load(open('tools/ad/ledger.template.json'));s=[x['step'] for x in d['intake']];assert s[0]=='snapshot-before-touching';assert s.index('sla-spec-written-and-green') < s.index('credentials-rotated'), s;print('ok',len(s),'steps')"
```
Copy it to the **scratchpad**, not to `runs/notes/ledger.json` — that path belongs to
`tick.py --init`, which is specified to refuse an overwrite.

---

#### T1-6 · `ad-rehearsal-dryrun` · `/home/kali/ctf-v2/lab/ad-range/dryrun.sh` (new) — 40 min

The reduced lab, and the reason it survives while a three-container estate does not.
Four code paths have **never executed**: `submit()`, the immune transition,
`--compare` actually blocking a patch, and `cap_split` feeding `traffic_mine` over a
socket. All four are reachable with a stdlib `http.server`, a scoreboard stub and
`printf FLAG1` as the exploit — no docker, no rotator, no aftermath artifacts. The
one thing a lab cannot prove is the real scoreboard dialect.

- Non-interactive, `set -u`, **no** `set -e` (a failing station must still report).
  `trap 'bash lab/ad-range/down.sh' INT TERM EXIT` so a ctrl-C never leaves
  processes running. Print one line per station as
  `[PASS] 3/6 flag_farm submits and dedupes (4.1s)` or
  `[FAIL] … -> <exact stderr> -> <the one command that fixes it>`. Keep a counter;
  exit non-zero if any station failed. ~6 minutes wall clock so it is re-runnable
  after every fix rather than ceremonial.
- **Use port 19080** (and 19081, 19090 if needed). Confirmed: 18080 is occupied by
  an unrelated container and a bind there fails with "port is already allocated".
  Pre-check each with `ss -ltn` and fail naming the port.
- Station 1 — offline preconditions: `python3 tools/ad/selftest.py` with
  `cases == passed`; `python3 tools/forensics/selftest.py`;
  `command -v tshark dumpcap jq`; and the measured-truth assertion that
  `tcpdump -i lo -c 1 -w /dev/null` exits **1** for this user while
  `dumpcap -i lo -q -a duration:1 -w /dev/null` exits **0**.
- Station 2 — bring up a stdlib `http.server` on 127.0.0.1:19080 serving a file
  containing a flag-shaped string, and a scoreboard stub. The stub must accept
  exactly what `submit()` sends: PUT, `Content-Type: application/json`, a bare JSON
  array, optional token header, replying
  `{"accepted": [...], "rejected": [...], "duplicate": [...]}`.
- Station 3 — `sla_check --save` twice, once per spec, both green with
  `passed == checks`. Both saves happen **here**; station 6 cannot `--compare`
  without them. Never save to `baseline.json`: `.gitignore` drops
  `**/baseline.json`.
- Station 4 — `flag_farm … --once` asserting `new_flags >= 1` **and** that the
  submit body contains `accepted`; then immediately again, asserting
  `new_flags == 0`. This is the first time `submit()` has ever run. On failure print
  the hint that `submit()` sends PUT with a bare JSON array and one optional header
  attached only when **both** header and token are set, so a different scoreboard
  shape is a config change (T1-4) and must be made before the contest.
- Station 5 — capture and mine: `dumpcap` on `lo` filtered to the service port, a
  baseline loop of happy-path requests, then the SUSPECT payloads (traversal,
  prototype pollution, a `%20`-encoded SQL UNION, a trusted-header request); then
  `cap_split` and `traffic_mine --baseline … --live …`. Assert `candidates >= 3`
  **and** `grep -c 'HTTP/1.0'` over the output == 0. That second assertion is the
  standing regression guard for the T0-5 defect.
- Station 6 — patch under SLA, both directions. First the **wrong** patch (remove
  the endpoint): `--compare` must exit **1** with verdict `REVERT THE PATCH` naming
  the check. Then the **right** patch: `--compare` exits 0 with `safe to keep`. Then
  `flag_farm --once` and assert `immune` behaves. Seeing the tool block a bad patch
  once is worth more than reading that it does.
- Final block: stations passed, wall clock from `$SECONDS` (**not**
  `/usr/bin/time`, which is absent), a GO/NO-GO, and the list of fields the operator
  must still fill from the real rules — `flag_regex`, submit
  url/header/token/format, `tick_seconds`, team hosts, the capture interface, one SLA
  spec per service.
- **Run the negative test once** or the dry run is decoration: point station 4 at a
  config with a deliberately wrong `flag_regex` and confirm it **FAILS** with
  `new_flags 0` and prints the hint. Second negative test, cheap: delete
  `submit.url` and confirm the run reports the flags as **pending**, not gone.
- Nothing here is under `tools/`, `skills/`, `knowledge/` or `test/`, so no gate
  fires while building it.

**Verify:** `bash lab/ad-range/dryrun.sh; echo exit=$?` prints 6 PASS lines and
`exit=0`. The EXIT trap means an interrupted run tears the lab down — print one line
saying so.

---

#### T1-7 · `scope-sentence-agents-md` · `/home/kali/ctf-v2/AGENTS.md` — 10 min, APPROVAL-GATED

Propose, do not apply. Section 7 says "**No red team**: every machine, Active
Directory or box privilege-escalation technique belongs to the other toolkit and is
out of scope here", and phase 1 of this scenario **is** host-level defensive work on
your own boxes. An agent reading that bullet at 10:00 can reasonably refuse to help
with the runbook's own section 3, and a refusal mid-contest costs more than a wrong
answer.

The gate is **not** the obstacle: `tools/check_boundary.py` returns 0 violations
today and RUNBOOK section 3 already ships that checklist. So this is a
clarification, not an unblock. **Mechanical detail:** the bullet **wraps** across
lines 235-236 with a two-space continuation indent (confirmed with `cat -A`), so an
exact-match edit must include the break. Bundle it with the `tools/ad` tool-table
rows in **one** approval. The verbatim replacement text is in section 11.

---

### T2 — the morning of, ~2 hours

100 minutes of the 120 available, leaving 20 for the gate and for the two preflight
commands that must be run rather than read. Interpretation and phase-1 write-up
support: nothing here keeps a service green or a flag submitted, so it earns the
morning rather than the evening.

---

#### T2-1 · `tick` · `/home/kali/ctf-v2/tools/ad/tick.py` (new) — 50 min

The RUNBOOK asks the operator to answer three questions every tick by reading three
JSON files, and at minute 200 nobody will. Build the 50-minute version, not a
140-minute one: a decider built on tools that lie gives confident wrong advice, so it
is only worth building after T0 has made the three tools honest.

- A **pure function** `decide_next(ledger, facts, now)` over file mtimes and saved
  JSON, returning one `action`, a `rationale`, a `facts` block, a `facts_missing`
  list, a `budget` block and a `commands` list — mirroring `tools/decide.py`'s output
  shape so the low-reliability protocol in `AGENTS.md` reads the same in both games.
- It writes **no** `challenges/<name>/state.json` and never calls `tools/hooks.py`.
  That is the sibling-plane separation `tools/ad` is built on.
- Derived facts, read from disk every run, each wrapped so a missing file becomes a
  null fact plus a `facts_missing` entry rather than an exception: newest `sla_saves`
  file by mtime → `sla_ok` (its top-level `ok`), `sla_failed`
  (`[r["name"] for r in results if not r["ok"]]`), `sla_age_seconds`; the live
  capture directory's file count and newest mtime; the newest mined JSON and its
  `top[0]`; the last JSON line of the farm log → `new_flags`, `immune`,
  `teams_yielding`, `submit_error`, `last_farm_age_seconds`.
- Precedence, first match wins: **1** an unfinished intake step (phase `intake`);
  **2** `restore_service` — `sla_ok` false, or no save exists, or the save is older
  than twice `tick_seconds`; **3** `revert_patch` — a patch with verdict `regression`
  and no `reverted_at`, returning its `rollback` string verbatim as the only command,
  which `tick.py` **never runs**; **4** `verify_patch` — a patch applied with verdict
  null, commanding one `sla_check … --save … --compare …` (both flags in one
  invocation, legal today); **5** `snapshot_before_patch` — a patch planned but not
  applied with no fresh green baseline; **6** `mine_traffic` — live capture newer
  than the newest mined file, commanding
  `traffic_mine.py --baseline … --live … --top 10` (they are **options**, not
  positionals); **7** `promote_candidate`; **8** `park_exploit_idea`; **9** `farm`;
  **10** `hold`, naming the files watched and their age in seconds.
- Two guards carry it: a missing or stale file is **unanswered, never green** — the
  local analogue of "a timeout is never a confirm" — and **no action can be an attack
  while any service is red or unanswered**.
- Budgets in the payload and enforced only where stated:
  `{"defensive":"unbudgeted","ticks_per_exploit_idea":2,"max_unverified_patches":1}`.
  Nothing this tool returns can stop a defensive step. Express budgets in ticks and
  counts, never as a probe-and-minute pair — the gate's budget-phrase test permits
  only the two `tools/decide.py` enforces.
- A candidate fingerprint must be recomputed, because a mined `top` entry carries
  **no** parameter list and its `query` is truncated to 300 chars and `body` to 500:
  use
  `sha1(method + "\n" + path + "\n" + "\n".join(sorted(traffic_mine.param_names({"query": e["query"], "body": e["body"]}))))[:12]`.
  `param_names` takes exactly those two keys and is the function the scorer itself
  uses, so importing the sibling keeps one definition of a parameter.
- Verbs: `tick.py <ledger>` (decide), `--init <service>` (write from the template,
  refuse to overwrite), and `record --kind <k> --field name=value …` with
  table-driven required fields and a refusal printing `{"ok": false, "reason": …}`
  and exit 2.
- Atomic writes: `NamedTemporaryFile` in the ledger's directory, flush, fsync,
  `os.replace` — copy `tools/state.py`'s `atomic_json()`.
- Add matching cases to `tools/ad/selftest.py`, driving `decide_next` with literal
  dicts (no temp files, no mtime reads), which is why it must stay pure. At minimum:
  a missing save is unanswered not green; a stale green save blocks attacking; a
  regression outranks a verify; one unverified patch blocks a second snapshot; and
  every payload carries `budget["defensive"] == "unbudgeted"`.

**Verify:** `python3 tools/ad/tick.py runs/notes/ledger.json --init notes`, then a
second `--init` must refuse (exit non-zero). A decide run on a fresh ledger returns
`action: intake_step` with a non-empty `facts_missing`. Drive `decide_next` directly
with a literal ledger holding a `regression` patch and facts with `sla_ok` false, and
assert the action is `restore_service` and the rationale names the failed check — red
SLA outranks a pending revert.

---

#### T2-2 · `timeline-microseconds` · `/home/kali/ctf-v2/tools/forensics/timeline_merge.py` — 25 min

journald is the richest log source on a modern Linux estate and the tree's only
timeline merger refuses all of it: a microsecond `__REALTIME_TIMESTAMP` reads as
milliseconds and falls outside the 1970..2200 window, giving `parsed: 0`. Phase-1
chain reconstruction is scored once rather than continuously, which is why it is T2.
**Three edits, not the one edit it looks like** — the unit string `from_numeric`
returns is a **key** into the `ASSUMPTIONS` dict, and adding a tier without adding
its entry raises `KeyError: 'epoch_microseconds'`.

- Edit 1 — `from_numeric`, widest tier first so the existing two keep their exact
  ranges: `US_THRESHOLD = MS_THRESHOLD * 1000`, `NS_THRESHOLD = US_THRESHOLD * 1000`,
  then branches for nanoseconds (`/1e9`), microseconds (`/1e6`), milliseconds
  (`/1000.0`) and seconds, returning the matching unit string.
- Edit 2 — add both new `ASSUMPTIONS` entries:
  `"epoch_microseconds": "a bare number in 1e14..1e17 was read as epoch microseconds (journald __REALTIME_TIMESTAMP)"`
  and
  `"epoch_nanoseconds": "a bare number at or above 1e17 was read as epoch nanoseconds"`.
- Edit 3 — the existing `epoch_milliseconds` text says "a bare number at or above
  1e11", which becomes **false** once 1e14 is the ceiling. Replace with "a bare
  number in 1e11..1e14". An assumption block that states a wrong range is worse than
  none, because it is what the write-up quotes.
- Do **not** touch `in_range`, `PLAUSIBLE_LOW`/`HIGH` or the FILETIME path: the
  1970..2200 window is what stops a wrong tier succeeding silently.
- Fixture `tools/forensics/fixtures/timeline/journal_sample.jsonl` — four
  `journalctl -o json` records with real microsecond values, one nanosecond-width,
  one millisecond-width. Use `.jsonl` (`edr_alerts.jsonl` is precedent). Never name a
  timeline fixture `*.log` — `*.log` is gitignored and it would be silently
  untracked.
- `tools/forensics/selftest.py` has **no** pure-function harness: every case is
  `case(name, tool, argv, check)` shelling out to the tool. Add three subprocess
  cases in the existing timeline block: a microsecond epoch parses and reports
  `epoch_microseconds` with `unparsed == 0`; a nanosecond epoch parses; and a
  second-and-millisecond epoch still reads as it did before (the regression pin that
  proves the new tiers did not steal the old ranges).

**Verify:**
```bash
journalctl -n 20 -o json --no-pager > /tmp/j.jsonl
python3 tools/forensics/timeline_merge.py --source /tmp/j.jsonl:__REALTIME_TIMESTAMP:journal --challenge tmp --limit 5
python3 tools/forensics/selftest.py
```
`parsed` must equal the record count with `unparsed: 0` and assumptions
`{"epoch_microseconds": N}`.

---

#### T2-3 · `ad-evidence-rule` · `/home/kali/ctf-v2/EVIDENCE_POLICY.md`, `/home/kali/ctf-v2/tools/ad/RUNBOOK.md` — 15 min

"We evicted the persistence" and "nothing was exfiltrated" are the two claims the
scored phase-1 write-up is made of, and all three of `EVIDENCE_POLICY.md`'s evidence
kinds describe something **present** in a response — so a claim about absence enters
the report ungraded, and an unqualified "nothing was exfiltrated" is the one sentence
an organiser can falsify with a single packet.

- **Edit 1** — append a `## Defensive claims (attack-defense and post-incident)`
  section after `## What does not count` and before `## Cards`. A defensive claim
  states an absence and no command can prove one, so it is evidenced by a method plus
  its blind spot. Five fields: `command` (the exact command, not a description),
  `output` (verbatim, bounded), `coverage` (what that command could **not** have seen
  — this field *is* the claim), `recheck` (the observation that would fail if the
  claim were false), and `grade`, one of `evicted-verified` (the mechanism was
  re-triggered and did not fire), `evicted-unverified` (the artifact was removed;
  nothing re-triggered it), or `absent-within-coverage` (a search ran, found nothing,
  and `coverage` names what it was blind to). An absolute absence is refused unless
  the grade is `absent-within-coverage` and `coverage` is filled in. State the honest
  form: "no exfiltration appears in the capture between T0 and T1, which begins after
  the incident" — still an absence, same grade, and the coverage field is what makes
  it true. The difference between those two sentences is worth more in a write-up
  than either claim is.
- Say plainly that this needs no `hooks.py` verb: every hook first requires a state
  file holding `probes` and `hypotheses` lists, so a defensive claim would have to
  invent a challenge, a hypothesis id and a bug class to get through. The claim
  belongs to the service, and the service ledger owns it.
- **Edit 2 — the correction that keeps the document self-consistent.** Line 50 reads
  "Say which of the three evidence kinds supports each claim." Adding a fourth
  category makes that false. Replace with: "Say which of the three evidence kinds
  supports each claim, or — for a claim about an absence — which of the three
  defensive grades, with its coverage boundary."
- **Edit 3** — one bullet appended to the RUNBOOK's pressure-rules list: never write
  a defensive claim without its coverage boundary.
- Ordering: `EVIDENCE_POLICY.md` **is** in `CONTROL_PLANE`, so
  `test_every_tool_path_named_in_prose_resolves` resolves the `tools/ad/tick.py` it
  names. Land T2-1 first or the whole gate fails.

**Verify:** `grep -n 'Defensive claims' EVIDENCE_POLICY.md`;
`grep -c 'absent-within-coverage' EVIDENCE_POLICY.md` ≥ 3;
`grep -n 'three defensive grades' EVIDENCE_POLICY.md`; and confirm the old sentence
is gone.

---

#### T2-4 · `agents-md-rows-and-scope` · `/home/kali/ctf-v2/AGENTS.md` — 10 min, APPROVAL-GATED

Discoverability, not a gate requirement — an agent reading `AGENTS.md` today cannot
learn `tools/ad` exists, which is how the whole control plane shipped invisible. Safe
and cheap: `test_every_tool_path_named_in_prose_resolves` **does** match
`tools/ad/<name>.py` in `AGENTS.md` and requires the file to exist, so the rows must
land **after** the tools; `test_every_tool_is_named_somewhere` globs top-level
`tools/*.py` only, so they satisfy discoverability rather than a check. **One
consolidated row beats three**, because three rows pin three filenames the gate then
resolves on every run. Apply together with the scope sentence under one approval;
`AGENTS.md` is always in context, so each edit costs every future session a re-read.
The verbatim text is in section 11.

---

### T3 — after the contest

This is where roughly 1,900 of the 2,400 proposed minutes went, and the cut is the
main output of this ranking. Three groups, and the reasoning for each.

**Group 1 — all new skills, bug classes and routers (~850 minutes).** Absorbs every
proposed knowledge-layer item: `ad-wiring`, `ad-traffic-mining`, `ad-triage`,
`ad-shared-image-exploit`, `ad-exploit-hygiene`, `ad-service-triage`,
`ad-web-class-addendum`, `ad-defense` (with `patch-without-breaking-sla`,
`credential-rotation`, `backdoor-hunt`, `egress-and-blast-radius`,
`minimal-detection`), and the whole `ir-live-estate` directory (`ir-router`,
`ir-collect`, `ir-first-ten-minutes`, `ir-restore-order`, `ir-transfer-map`,
`ir-chain-reconstruction`, `ir-exfil-scope`, `ir-incident-report`, `ir-wiring`). Each
ships as `catalogue` by the tree's own rule — a class rises only through a chain card
— and each costs a generator entry plus two skill files plus a registry entry plus
two generator runs plus `skill_audit --apply` plus a gate. At hour four nobody opens a
catalogue skill while a service is red; they read the RUNBOOK. So the genuinely
actionable content is merged into the T0 RUNBOOK edit instead: the patch ladder, the
rotation order, the persistence sweep order, the abort ladder, the order of
volatility, and the egress deadman. Three constraints for whoever builds this later:
the taxonomy, `skills/INDEX.md` and `skills/registry.json` are **generated** — edit
`build/make_bug_classes.py` and `build/make_index.py`;
`knowledge/skill-audit.json`'s `summary.skills` count is compared against a live
audit by the gate, so `tools/skill_audit.py --apply` is a **mandatory** step after
adding a skill; and `tools/skill_audit.py` caps a `router`-layer skill at 160 lines,
so a router's tables must be carved into a sibling file.

**Group 2 — the entire `.claude/agents/` subagent layer (~235 minutes).** The
directory does not exist, the enforcement semantics of scoped `tools:` entries are
unverified, and unrehearsed orchestration the night before a contest is the
highest-regret spend available. Its one load-bearing idea — the prohibitions an agent
must obey — lands as prose in the T0 runbook. Full specs are in section 7 so the
files can be created on a day when a human can watch them fail.

**Group 3 — host collectors and the full docker estate.** Worth zero if the estate
turns out to be Windows, and the collector designs were measured **unrunnable as
specified**: a `/var/lib/dpkg/info/*.md5sums` walk is 407,392 entries ≈ 41 minutes,
`find / -xdev -perm -4000 -type f` exceeded 120 s, and a hung hard NFS mount on this
box makes `df` block forever (`timeout 3 df` exits 124). Any future collector needs
`timeout` around every command, `/proc/mounts` instead of `df`, network filesystems
pruned, and expensive collectors opt-in.

| T3 item | Path | Min | Why it waits |
|---|---|---|---|
| `patch-gate` | `tools/ad/patch_gate.py` | 45 | Strongest T3 candidate and the first thing to build afterwards. It enforces the snapshot/patch/compare sequence and writes a rollback script — but once T0-2 lands, the manual sequence the RUNBOOK prescribes becomes trustworthy, and that is the cheaper 80%. Revisit after a contest where the manual loop was **measured** too slow |
| `secret-inventory` | `tools/ad/secret_inventory.py` | 45 | Finding where a credential lives in four places before rotating three is a real phase-1 need, and the read-only design (fingerprint plus rotation groups, never more than four characters of a value) is right. Deferred because the rotation **order** is the part that prevents the loss, and that order goes into the RUNBOOK for free in T0. For whoever builds it: no full-filesystem walk, and never `df` or `statvfs` |
| `ad-access-log-adapter` | `tools/ad/traffic_mine.py` | 25 | Included only because the capability three layers assumed exists does **not**: `parse_request` returns `None` on a combined log line and on a request line with leading whitespace. That was the hedge for a containerised estate, a box with no root, and a Windows host with no `tcpdump`. The T0 documents are made honest without it, so this is new capability, and new capability on contest eve is the wrong bet. Fold the two-character leading-whitespace tolerance into T0-5 if it is free |
| `ad-separation-test` | `tools/ad/selftest.py` | 20 | Two `ast`-based cases asserting nothing under `tools/ad` imports `state`, `hooks` or `decide`, and that no non-docstring literal names `challenges/`. A declared invariant with no test is a comment, and the cheapest way for this design to rot is one future edit that imports `hooks.py` to "record the flag properly". Match on the **first dotted component**, not `startswith`, or a future `import decider` false-positives; and sequence the negative control so the restore is **unconditional**, or a wrongly-passing test leaves the edited file corrupted. Deferred only because the invariant is not at risk during the contest |
| `ad-system-eval-cases` | `tools/system_eval.py` | 30 | `AGENTS.md` calls the offline evaluator a required gate, and with a tick decider outside it that sentence is false for half the control plane. Additive and safe — a fifth `ad_decisions` key adds no obligation, since the well-formedness test never iterates unknown keys. Note honestly that the case total moves (47 → 53) but nothing gates on accuracy. Depends on `tick.py` existing |
| `host-baseline-and-diff` | `tools/ad/host_snapshot.sh`, `tools/ad/host_diff.py` | 70 | The only replacement for the two absent integrity tools, and its `on_all_hosts` inference (a change on every host is the image or your own automation; a change on one host of eight is an attacker) is genuinely something no human does reliably. Deferred on two grounds: worth zero if the estate is Windows, and the collectors were measured unrunnable as first specified — the fix (cheap set by default, expensive collectors opt-in, every collector wrapped in `timeout`, network filesystems skipped from `/proc/mounts`) is itself most of the build |
| `lab-estate` | `lab/ad-range/compose.yml` | 120 | A three-container estate with a flag rotator, planted aftermath artifacts and a patched second team is a genuinely good rehearsal rig, and the no-build path (`python:3.11-slim` already in the local store, bind-mounted stdlib scripts) makes it affordable in principle. Deferred because T1-6 exercises the same four untested paths with a stdlib `http.server`, and because no local stub can prove the real submission dialect. Use 19080/19081/19090 — 18080 is taken |
| `ad-knowledge-layer` | `skills/` | ~850 | Group 1 above |
| `ad-agent-layer` | `.claude/agents/` | ~235 | Group 2 above; specs in section 7 |
| `ad-documented-tooling-gate` | `test/regression.py` | 20 | **Last, and the first thing to abandon.** It would convert today's omission into a standing check that every tool subdirectory is named in `AGENTS.md` — but the check reports **two** undocumented directories today, `['ad','forensics']`, so it cannot land on the `tools/ad` rows alone and needs a second `AGENTS.md` row belonging to another layer. Double approval-gated, wins nothing on the day, and a red required gate plus `asyncRewake` is how an unauthored edit lands. Do not weaken the test to excuse a directory by name — that re-creates the blind spot |

---

## 5. Build order

Running total in build minutes; gate latency is additional (71-120 s per fire).

| # | Item | Min | Running |
|---|---|---|---|
| 1 | `drop-g2-session-garbage` | 5 | 5 |
| 2 | `ad-sla-vanished-check` | 30 | 35 |
| 3 | `ad-flag-submit-durability-core` | 35 | 70 |
| 4 | `ad-scope-and-flagregex-guards` | 45 | 115 |
| 5 | `cap-split` | 45 | 160 |
| 6 | `ad-runbook-ordering-and-capture` | 45 | 205 |
| 7 | `ad-preflight-tonight` | 35 | **240 — end of T0** |
| 8 | `ad-readme-corrections` | 20 | 260 |
| 9 | `ad-immune-honesty` | 30 | 290 |
| 10 | `ad-replay-credential-strip` | 25 | 315 |
| 11 | `ad-submit-dialect-configurable` | 25 | 340 |
| 12 | `ad-ledger-template` | 15 | 355 |
| 13 | `ad-rehearsal-dryrun` | 40 | 395 |
| 14 | `scope-sentence-agents-md` (propose) | 10 | **405 — end of T1** |
| 15 | `tick` | 50 | 455 |
| 16 | `timeline-microseconds` | 25 | 480 |
| 17 | `ad-evidence-rule` | 15 | 495 |
| 18 | `agents-md-rows-and-scope` (apply) | 10 | **505 — end of T2** |
| 19 | `patch-gate` | 45 | 550 |
| 20 | `secret-inventory` | 45 | 595 |
| 21 | `ad-access-log-adapter` | 25 | 620 |
| 22 | `ad-separation-test` | 20 | 640 |
| 23 | `ad-system-eval-cases` | 30 | 670 |
| 24 | `host-baseline-and-diff` | 70 | 740 |
| 25 | `lab-estate` | 120 | 860 |
| 26 | `ad-knowledge-layer` | 850 | 1710 |
| 27 | `ad-agent-layer` | 235 | 1945 |
| 28 | `ad-documented-tooling-gate` | 20 | 1965 |

Two ordering constraints are hard. Items 3, 4, 9 and 11 all edit `flag_farm.py`:
land each one, gate, then the next, or the pending/seen bookkeeping gets broken by an
interleaved edit. And items 17 and 18 name `tools/ad/tick.py` in files the gate
resolves, so item 15 must land first.

---

## 6. Two-hour version

If the evening collapses, build exactly these three, in this order:

1. **`ad-sla-vanished-check`** (30 min) — the guard on the score you cannot win
   back, and it currently blesses both a deleted and a renamed check.
2. **`ad-flag-submit-durability-core`** (35 min) — the single point of failure;
   converts a catastrophic-and-silent loss into a held-and-alarmed one.
3. **`ad-scope-and-flagregex-guards`** (45 min) — the only off-scoreboard
   consequence in the plan, plus a defect that silently invalidates every submission.

That is 110 minutes plus three gate fires. If even that is too much, build **item 2
alone**: a flag held is a flag recoverable, and no other single change in this plan
can prevent a 100% loss of the attack score.

If there is one spare hour after those three, spend it on
`ad-runbook-ordering-and-capture` (T0-6) — it is the only artifact that gets printed
and read while tired, and it currently instructs two near-certain losses.

---

## 7. The agent layer

`.claude/agents/` does not exist; neither does `.claude/workflows/`. The ranked plan
defers the whole layer to T3, for three reasons: the directory would be new, whether
a scoped `tools:` entry is **enforced** or merely enables the tool was not provable
statically, and a subagent that stalls on a permission prompt mid-tick is worse than
no subagent. This section carries the specs anyway, in enough detail to create the
files on a day when a human can watch them fail.

**One measured hazard that shapes the whole design.** `.claude/` is the single
directory no gate check reads: `tools/check_boundary.py` skips it by name,
`test/gate-exemptions.json`'s scan roots do not include it,
`test_every_tool_path_named_in_prose_resolves` reads `.claude/commands` and stops, and
the PostToolUse hook matches only `tools/`, `skills/`, `knowledge/`, `test/`. So an
agent file can name a tool that does not exist, omit the flag rule, or lose its
`tools:` line and the gate still says PASS. A lint wired into `tools/ad/selftest.py`
closes that with **no** edit to `test/run_all.sh`, because the gate already loops over
that selftest.

**Frontmatter keys that exist** in the installed build's agent-file parser: `name`,
`description`, `model` (with `inherit` special-cased), `color`, `background`,
`omitClaudeMd`, `memory` (`user|project|local`), `isolation` (`worktree|remote`),
`effort`, `permissionMode`, `maxTurns`, `tools`, `disallowedTools`, `skills`,
`initialPrompt`, `observer`, `observerMessage`, `observeSubagents`, `mcpServers`,
`hooks`. The `tools` splitter is parenthesis-aware, so
`Bash(python3 tools/ad/x.py:*)` survives as one entry. A list entry equal to `*` drops
the restriction entirely, which is the exact hole a lint must close.

### 7.1 `agent/ad-prohibitions.md` — the canonical block (15 min)

One file whose entire body is the block below, with no heading above it and nothing
after it, so a lint can require it verbatim in every agent file. It goes in `agent/`
rather than `.claude/` deliberately: `agent/` **is** inside the gate's scan roots, so
the language and budget-drift checks cover the prohibition text.

```
## PROHIBITED - these are not preferences

1. Never send a request to a host that is not listed, individually, in the
   team list of the flag_farm config for this service. No range, no sweep, no
   adjacent address, no organiser infrastructure, no host you inferred from a
   hostname pattern. Do not work around the config guard, and do not add a
   host the operator did not type.
2. Never delete, move, truncate, rename or overwrite an artifact, a log, a
   capture, a backup or a ransom note. Availability can be restored; evidence
   cannot. If something has to be moved, name it and stop.
3. Never edit a file inside a service directory unless a snapshot from
   tools/ad/sla_check.py --save exists for that service, was written in the
   last ten minutes, and you have quoted its "passed" and "checks" numbers in
   your report. After the edit, run sla_check.py again with --compare against
   that snapshot. If comparison.regressions is not empty, write REVERT THE
   PATCH, restore the bytes you replaced, re-run --compare, and stop.
4. Never restart, stop, reload, redeploy or reinstall a service, and never
   restore a snapshot or a backup. You do not own availability. Print the
   command you would have run and stop. If you changed a file that needs a
   restart to take effect, say in your report that the change is NOT LIVE.
5. Never rotate, change or generate a credential, key, token or secret. Name
   the one you found, say where, and stop.
6. Never claim a flag. A flag counts only when it appears in a response body
   or in a supplied artifact, and only tools/ad/flag_farm.py submits one. Do
   not put a flag in a report, a commit message, a chat line, or any file
   outside the run directory.
7. Never state a finding without a path and a verbatim excerpt of the bytes
   that prove it. "Likely", "probably", "appears to" and "should be" are
   hypotheses: write HYPOTHESIS in front of them.
8. A timeout, a connection reset, an empty response or a missing input file is
   not a result. Record it as inconclusive, say which input was missing, and
   stop that item. Do not retry it a third time.
9. Stop at your stop condition and report. Do not start a different kind of
   work because the first kind ran out, and do not run the same tool again
   with different flags hoping for a better answer.
```

Three drafting constraints, all against the gate's own code: do not write a
probe-and-minute budget pair other than the two the controller enforces, because
`agent/` is scanned; every `tools/<path>.py` named must exist on disk, and nothing in
the gate resolves tool paths inside `agent/*.md`, so the lint is the only thing that
catches a typo; and none of the blocked methodology substrings may appear, because
`agent/` is not skipped and this file is not exempt — which is also why rule 1 says
"the config guard" rather than naming a notation.

### 7.2 `agent/ad-roles.md` — the index and the parity story (25 min)

Two jobs: the index the incident commander reads to pick an agent in ten seconds, and
the whole non-Claude-Code parity story, since other runners read `AGENTS.md` and from
there this file, but do not discover `.claude/agents/`.

Sections, in order. A one-paragraph statement that these are narrow subagents for an
authorized attack-defense event, started by name, owning no priorities, no clock, no
availability and no submission. Then **the run directory**, a table defining the
layout every prompt refers to, stating plainly that `runs/` does not exist in a fresh
checkout and that preflight creates it, and that `.gitignore` line 18 `**/runs/` makes
everything under it uncommittable by default — while `*.seen` is ignored nowhere else,
so a farm config outside `runs/` puts real flags in git. Rows: `survey/<host>/`,
`capture/<service>/baseline/`, `capture/<service>/live/`, `sla/<service>.spec.json`,
`sla/<service>.t0.json`, `sla/<service>.before.<n>.json`, `mined/<service>.<n>.json`,
`farm/<service>.json`, `farm/<service>.seen`, `reports/<agent>-<n>.md`,
`locks/<service>.owner`, `patch-paths.txt`.

Then **the agents**, one row each: name, one-line job, read-only or write-capable,
input path, where the report goes, stop condition. Then **why four of five agents have
no Bash** — the enforcement paragraph, and it must be exact because it is the safety
argument: a read-only agent with no Bash physically cannot send a request, restart a
service or delete a capture, and needs no permission prompt to do its job; the
operator runs the tool and redirects its JSON into `runs/`, the agent reads that file.
That costs one shell character and buys a guarantee instead of a promise. Then
**collision rules**: exactly one agent is write-capable so concurrent readers cannot
collide by construction; every agent reads `runs/.../locks/<service>.owner` first and
stops if it names someone else; every `sla_check --save` uses a fresh numbered
filename; and no attack-defense agent sets `isolation: worktree`, because a worktree
is a second copy of the tree with its own `runs/`, so the lock files and the `.seen`
flag set would fork — and a forked `.seen` means double submission. State plainly that
the lock file is convention and the tool list is the enforcement.

Then **running these outside Claude Code**: the prompt bodies are plain markdown;
open the file, ignore the frontmatter, follow the body as a self-imposed role — and
the honest degradation, that under any other runner the tool-absence guarantee does
not exist and the prohibitions block is all there is. Then **what the gate checks**:
name the lint, say it runs inside `tools/ad/selftest.py`, list its failing checks, and
say the gate prints only `FAILED: tools/ad/selftest.py` so the detail comes from
running that selftest directly.

### 7.3 `tools/ad/agent_lint.py` plus a selftest case (50 min)

Stdlib only — not because PyYAML is missing (it is present, 6.0.3) but because a
required gate step should not depend on a third-party package. CLI
`agent_lint.py [--json]`, exit 0 with no failures, always JSON on stdout:
`{"mode":"ad-agent-lint","agents":N,"roles_rows":N,"failures":[{"file","check","detail"}],"warnings":[…]}`.
`ROOT` is three `dirname`s up from `__file__`. A pure `audit() -> dict` does all the
work and **must never raise** — a missing directory or an unreadable file becomes a
failure or warning entry, because a traceback inside the selftest fails the whole gate
with no useful message.

Frontmatter parsing is deliberately not YAML: require a first line that is exactly
`---`, read to the next such line, split each line on the first `:`. Failing checks:
**1** `name` equals the filename stem (a convention check — keeping them equal makes
the question of which one resolves the subagent moot); **2** `description` present
and at least 40 characters; **3** `tools` present, non-empty, and no entry equal to
`*` — a missing line leaves the restriction undefined so the subagent inherits
everything, and a lone `*` does the same, so both fail and the detail says which;
**4** write capability is **declared, not inferred** — if `tools` contains `Write`,
`Edit`, `NotebookEdit` or a bare `Bash`, the body must contain the literal line
`WRITE-CAPABLE: yes`, otherwise `WRITE-CAPABLE: no`; **5** every repo path named in
the body resolves, regex
`\b(?:tools|agent|test|scripts|build|skills|knowledge)/[A-Za-z0-9_./-]+\.(?:py|sh|md|json)\b`,
applied to the agent bodies **and** to `agent/ad-roles.md`,
`agent/ad-prohibitions.md` and `.claude/commands/ad-*.md`, because the gate's own
checks miss all three — nothing resolves paths in `agent/*.md`, the prose check
matches `.py` only, and the slash-command check's regex is single-segment so it never
matches `tools/ad/anything`; **6** the prohibitions block appears verbatim, reporting
the **first missing line** rather than just "missing"; **7** no blocked token —
`sys.path.insert` `tools`, then `from check_boundary import BLOCKED`, and fail if any
is in `body.lower()`; **import** it, never restate the list, or this file itself
becomes a boundary violation (`check_boundary.py` is import-safe: `sys.exit(main())`
is under `if __name__`); **8** drift both ways against `ad-roles.md` — every agent
file's name appears there, and every name there exists as a file, with a `LATER`
marker exempting the second half.

Warnings, never failures: a body still containing `FILL-IN`; `maxTurns` absent;
`omitClaudeMd` absent; `.claude/agents` absent entirely, so the lint can land before
the first agent file; and a frontmatter key outside the set the build parses. Wire it
with `import agent_lint` beside the three existing tool imports in
`tools/ad/selftest.py` (which already does `sys.path.insert(0, HERE)`) and one case at
the end in the file's own decorator style:
```python
@case("agents: every .claude/agents file passes the lint")
def _():
    r = agent_lint.audit()
    assert not r["failures"], r["failures"]
```
No edit to `test/run_all.sh` is needed or wanted.

### 7.4 The five agents

| Agent | Tools | Write | Job and stop condition |
|---|---|---|---|
| `ad-service-read` | `Read, Grep, Glob` | no | Reads one service's source and returns the flag-store sinks with `file:line`, the routes that reach them, the auth boundary in front of each, three falsifiable hypotheses with a falsifier each, and the one-line patch that stops each mechanism without removing the feature. Stops after the patches, after 60 turns, or when two of three hypotheses have no statable falsifier. `maxTurns: 60`, `effort: high` |
| `ad-traffic-watch` | `Read, Grep, Glob` | no | Reads one service's saved `traffic_mine` JSON plus the two capture directories and reports the three most likely stolen exploits with the replay command copied verbatim. Must quote `baseline_requests`, `live_requests` and `candidates` **first**, and must know that `candidates` is a **count** while the ranked entries are in `top[]`. Stops after one mined file and one report. `maxTurns: 30` |
| `ad-patch-bracket` | `Read, Grep, Glob, Edit, Bash(python3 tools/ad/sla_check.py:*)` | **yes** | The only agent that may edit a running service, and it exists so the write is always bracketed. Refuses to start without a spec; saves a numbered `before` run; writes the patch into the report **before** applying it; applies one `Edit`; re-measures with `--compare`; reverts itself on any regression. Cannot restart anything, so it must say LIVE or **NOT LIVE** and print the restart command. Stops after one patch to one service plus its revert. `maxTurns: 40`, `permissionMode: default` |
| `ad-sla-triage` | `Read, Grep, Glob` | no | Called when a check goes red. Decides between exactly three causes — (a) a patch we applied broke it, (b) something external is hitting it, (c) it was already red at t0 — with the excerpt that decides it, and names the smallest next action. Must write exactly `no t0, cannot distinguish (a) from (c)` when the t0 run is missing rather than guessing. Never measures. `maxTurns: 20` |
| `ad-host-survey` | `Read, Grep, Glob` | no | Reads a read-only host dump and ranks what looks planted — units, timers, cron, `authorized_keys`, SUID, preload, unexpected listeners — with the exact line, a CERTAIN/HYPOTHESIS confidence, and the one thing that would settle it. Reads the dump's manifest **first** and lists every ABSENT input before saying what it found. Removes nothing, reaches no host. `maxTurns: 80` |

Every one carries `model: inherit`, `omitClaudeMd: true` (the tree's own contract is
the jeopardy loop, so loading it wastes context and instructs the wrong loop), and
the prohibitions block verbatim at the end of the body. Four of the five carry
`tools: Read, Grep, Glob` and nothing else — byte-identical in shape to the build's
own shipped read-only agent template, which is what makes their read-only status
enforcement rather than prose.

`ad-patch-bracket` is the exception and carries two explicit caveats in its body.
Whether the scoped `Bash(...)` entry is **enforced** or merely enables the tool was
not provable, so the body must carry a fallback — if a Bash call is refused or
prompts, print the exact `sla_check.py` command, ask the operator to run it, and read
the saved JSON — which makes the agent work either way. And `Edit` ships
**unnarrowed** with the literal marker
`FILL-IN: narrow the Edit entry to the service directory (e.g. Edit(/srv/app/**)) before the contest`,
because the real estate path is unknown until the day. The lint reports `FILL-IN` as
a warning, not a failure, so the gate stays green — and narrowing that entry by hand
at minute zero is then the **only** mechanical enforcement of the patch rule that
exists, which makes it a numbered preflight step rather than a memory.

---

## 8. What we are deliberately not building

| Not building | Why |
|---|---|
| An `--ad` mode in `tools/decide.py` | Two code-level blockers. `decide.py` reads `flag = current.get("flag")` at line 181 and returns `record_solve`/`verify_flag` then `return result` through line 202, so no later rule is reached — a rotating flag pins the controller permanently. And `test_every_state_key_the_controller_reads_has_a_writer` fails any `decide.py` that branches on a state key no tool under `tools/*.py` writes, so an `--ad` mode forces the jeopardy ledger to grow attack-defense keys. A third argument often given — that `pre-probe` refuses a duplicate request — is **weaker than claimed**: `hooks.py` line 77 already carries an `--allow-repeat` escape hatch |
| A `hooks.py` verb for a defensive claim, a patch or a tick | Every hook calls `load_state()` first, which refuses any file that is not a dict carrying `probes` and `hypotheses` lists, and the path only ever resolves under `challenges/<name>/state.json`. A defensive claim has no challenge, no hypothesis id and no bug class, so the verb would have to fabricate all three |
| A standalone `submit_flags.py` | Absorbed by T0-3 plus T1-4, which together cost 60 minutes against its 70 and change one hot path instead of adding a second submitter. A standalone submitter means a second seen-set, and two seen-sets is how you double-submit — which the RUNBOOK lists as a pressure rule. Its two good ideas survive: the durable queue becomes the pending set, and its `--probe` concept becomes the minute-zero "submit one flag by hand with `curl -i`" line in PREFLIGHT |
| A scapy-based pcap splitter | Absorbed by `cap-split`. The scapy approach concatenates payload in capture order with no TCP sequence handling — its own spec admits a retransmitted or reordered stream concatenates wrongly — where `tshark` reassembles correctly and emits one row per request even on a keep-alive connection. It would also have been the first non-stdlib dependency reachable from a gate-run selftest |
| A shell `awk`-toggle capture converter | Same tool, third name. Killed as a **mechanism** because it depends on this `tshark` build's byte-count direction markers and on a shell word-splitting subtlety: refactoring the stream list into a variable yields `live_requests: 0` with no error. A Python tool with selftest cases cannot fail that quietly |
| `tools/ad/capture.py`, a capture supervisor | Its headline guard is a minimum-free-space check, and free space can only be read with `df` or `statvfs`, **both of which block forever** on this box's hung hard NFS mount (`timeout 3 df` exits 124). A supervisor whose safety check can hang is worse than no supervisor. The two bounded `dumpcap` lines it existed to wrap go straight into the T0 runbook |
| `tools/ir/exfil_summary.py` | Every threshold in its ranking is a guess without a real exfiltration capture to calibrate against, and a confidently wrong byte count in a scored write-up is worse than "we ranked by bytes and read the top five by hand". `tshark -r cap.pcap -q -z conv,tcp \| sort -k7 -n \| tail -20` answers the same question with no tool and no false authority |
| `tools/ad/evidence_pack.py` | `rsync`, `tar` and `sha256sum` already do the work and are all present. The one guard worth code — comparing `st_dev` of source and destination to catch an "off the box" copy that is on the same filesystem — is not worth 40 minutes here. The four-command stopgap preserves the property that matters: the hash exists before the artifact moves and is checkable after |
| A `PreToolUse` hook that blocks an unbracketed patch | Killed on a verified defect, not on cost: this build documents that hooks for these calls start in the home directory with a reduced environment, and the specified script inspected the project with **relative** paths, so it would have exited silently and protected nothing while everyone believed it did. Add a failure mode that denies every `Edit` in every session including the fix, and it is unrecoverable-shaped on contest morning. Its goal survives as narrowing `ad-patch-bracket`'s `Edit` entry |
| `.claude/workflows/ad-tick.js` | The workflow `agent()` API expresses a DAG of agent runs, not a timer — and a tick **is** a wall clock, which the workflow sandbox does not have. Meanwhile `flag_farm.py` already loops natively on `tick_seconds` and an SLA watch is a `while sleep 30` loop |
| Slash commands `/ad-tick` and `/ad-preflight` | A slash command is an in-session entry point, and at minute 0 the operator is on the estate or in a terminal, not in a session on this box. They also duplicate commands that would then live in three places, so a flag change needs three edits. The commands go into the RUNBOOK, which is the artifact that gets printed. The one genuinely valuable preflight step is a single `mkdir -p` line, which goes into PREFLIGHT.md |
| An `ad` row in `ctf.py` (SKILLS + SIGNALS) | Killed on measurement, not principle. `test_ctf_py_categories_have_a_router` runs one direction only, so a router is gate-legal without it; `ctf.py`'s misc SIGNALS row already owns `scoreboard` and that row's own comment says every term in it is unclaimed elsewhere; and `observation_route` ranks by occurrence **count** with routing correctness at 13 of 13 and zero margin, so a two-occurrence attack-defense text can silently outrank a one-occurrence web text and move an existing jeopardy case |
| An `ad` or `ir` row in `agent/probe-policy.json` | Its six keys hold probe **payloads** keyed to the jeopardy controller's vocabulary. The attack-defense first move is a tool invocation with a named output key, not a probe payload. It has no dfir row either and nothing broke |
| An attack-defense bug class in the taxonomy | "Attack-defense" is a game mode, not a bug class. Beyond the generator cost, `classify.py` weights signals by rarity across the handouts on disk and there are **zero** attack-defense handouts, so new classes either never win a vote or distort the weighting for the classes that work. That is a research change, not an evening change |
| A live-network case in `tools/ad/selftest.py` | The file promises "no network, no sockets, no subprocess" so the gate can run it, and the gate does. A socket makes a required gate flaky, and a flaky required gate is how a team learns to bypass it. The substitute is proven: monkeypatch `run_exploit` and drive `tick()`, and drive `evaluate`, `compare`, `build_submission` and `replay_template` as the pure functions they are |
| A tool that discovers other teams' hosts, or expands a range | `flag_farm.py` requires every host typed individually, on purpose. A discovery tool would undo the one guard that keeps this directory from quietly becoming something else. The team list comes from the organiser's scoreboard |
| A host IDS, a file-integrity daemon, or anything watching continuously | All absent, and installing and tuning any of them during a contest costs more than it returns. An auto-blocker is also the wrong instinct: it will eventually block the organiser's checker and cost more than the exploit it stopped |
| An atime-based flag-read detector | Measured and it does not work: `findmnt -no OPTIONS /` reports `relatime`, under which atime updates only when it is older than mtime/ctime or a day stale, so a poller on the flag file mostly will not fire |
| A ransomware-family identifier, or decryptor hunting | Nothing about the family is published, an organiser-built sample has no public decryptor, and attribution earns nothing the timeline does not. The forensically useful part of a ransom note is its birth time and the account that wrote it |
| A hand-written EVTX parser | `python3-evtx` is one apt line away (Candidate 8.1.0-1) and a correct parser is a day's work — the binary-XML template table is the hard part, and without it you get timestamps and no field names |
| A `yara` rule pack | The CLI is absent, there is no rule corpus in this tree, and rules written from memory produce confident output about nothing. `grep -rE` over the web root plus a birth-time cluster finds the same files in the time the pack would take to write |
| Automatic patch application, automatic rollback, or auto-submit outside `flag_farm` | `tick.py` names the rollback command and never runs it. An automated revert during a scored tick is the one action you cannot undo, and a second submitter means a second seen-set |
| A cross-service dashboard | `for f in runs/*/ledger.json; do python3 tools/ad/tick.py "$f"; done` is the whole feature. A dashboard is the thing that gets built instead of the decider |
| Raising `test/baseline.json` | It is a floor, not an equality, and nothing in T0-T2 adds a skill, a class or a chain card. If an item ever appears to require raising a floor, that is a signal the item is wrong |

---

## 9. What is unknown about the real brief, and the cheapest way to learn it

| Unknown | Why it matters | Cheapest probe on the day |
|---|---|---|
| The flag format | `flag_farm` refuses to start without `flag_regex`, and a regex with a capturing group silently strips every wrapper | The rules page, else exploit your **own** service once and read the flag you get back — that proves the regex end to end. `preflight … --sample '<the flag>'` confirms it in one second |
| The submission dialect: method, URL, body format, header name | Highest-consequence unknown. Before T0-3, a wrong guess plus the seen-set destroys every flag of the contest | Submit one flag by hand with `curl -i` and copy the exact request into the config before the farm runs unattended |
| Whether duplicates are penalised | The whole justification for the seen-set being destructive. Currently an assumption about scoreboards in general, not a measurement about this event | The rules, or submit one flag twice deliberately against your own service at minute zero and read the response |
| Tick length, and whether flags rotate | Sets `tick_seconds` and the staleness thresholds in `tick.py` | Watch your own scoreboard row for two rotations, or the rules page. The non-rotating case is already safe: the dedupe is measured |
| Availability-dominant or attack-dominant scoring | Decides whether `sla_check` or `flag_farm` is the tool that matters, and therefore which T0 items earn their minutes | The rules, or empirically: let one non-critical check go red for one tick and read the delta. T0-2 is weighted high because it pays under **both** branches |
| Linux, Windows or mixed estate | If Windows-heavy, EVTX is the primary artifact and it is unreadable here until one apt line runs; the capture story degrades too, since `tcpdump -i any` is Linux-only | `uname -a`, the first login banner, or `nmap -sV` against your own hosts in the first sixty seconds |
| Containerised or orchestrated | Mainly breaks the capture story: `tcpdump -i any` inside a container needs a sidecar or host networking | `ls /` for `/.dockerenv`, `docker ps`, or ask. Hedge: a small proxy writing raw requests, or the `sla_check`-capture trick — **not** an access log, measured |
| Whether the organiser publishes their checker | `sla_check`'s value depends entirely on whether the spec mirrors the real checker or guesses the happy path | The rules or the scoring page at minute zero. If published, transcribe the spec from it and `--compare` becomes near-authoritative |
| Whether source is supplied for the services | If not, `traffic_mine` stops being a bonus and becomes the **primary** exploit source, promoting T1-3 above everything in T1 | `ls` the service directory in the first five minutes; a deployed attack-defense service usually ships its own source |
| Whether you get root, and whether a snapshot is allowed | Several host commands under-report without root and read as a clean box; without a snapshot, read-only-first discipline becomes the only protection for the evidence | `id`, `sudo -v`, and the platform console at minute zero |
| The authorized team list and address space | `flag_farm` cannot verify this, and until T0-4 lands it cannot reliably reject a range. The one unknown with consequences outside the scoreboard | The organiser's published list, pasted verbatim, read back by a second person before the first non-dry-run tick |
| Whether the services speak HTTP at all | `sla_check`, `traffic_mine`, `cap_split` and the replay are all HTTP-shaped. A raw TCP service degrades all of them | `ss -ltnp` on your own box plus one `curl -sS -i` per port, inside the first five minutes. Say so immediately rather than letting a tool report zero as if it meant no attacks |
| Whether TLS terminates in front of the service | If it does, an external capture is ciphertext and the whole mining path is dead — capture on loopback behind the terminator | One `tcpdump -c 5 -A` on the service port and see whether you can read it |
| Whether the checker's traffic is visible on your interface | Without it `traffic_mine` has no baseline, `baseline_requests` reads 0, and every request scores on payload shape alone | Start the capture before anyone attacks and count the files that appear in the first two minutes. **This cannot be measured later**, which is why it is a numbered preflight step |
| Whether apt or any outbound access works from the operator box | Decides whether tonight's install window is the only one | No cheap way to learn in advance. Assume it is, and install tonight |
| Whether the event forbids AI assistance | `CLAUDE.md` scopes this toolkit to practice **before** such a contest, and `grep -ci 'ai assistance'` returns 0 in the RUNBOOK today | The rules, before the contest, not during. If forbidden, tonight's build is still legitimate preparation and tomorrow the toolkit is closed |

---

## 10. What will go wrong

### The tree's own traps this build will hit

- **The gate hook fires on nearly every item.** `.claude/settings.json` runs
  `test/run_all.sh` in the background after any `Write` or `Edit` under `tools/`,
  `skills/`, `knowledge/` or `test/`, with `asyncRewake: true`. A **failing** gate can
  wake the model out of band and land an edit nobody authored — this has happened
  before in this tree. After any session that touched those directories, run
  `git diff` before committing. Batch edits into one write per file. During the
  contest, run `bash test/run_all.sh` by hand rather than trusting the hook.
- **A half-written file blocks the fix.** A failing lint or selftest fails the whole
  gate, including the commit that would repair it. Always run the specific tool
  directly (`python3 tools/ad/selftest.py`) before letting the background gate settle,
  because the gate prints only `FAILED: tools/ad/selftest.py`.
- **`tools/ad/selftest.py` imports its siblings at module scope.** A new module with
  an import-time probe (`shutil.which`, a socket, a non-stdlib import) kills every
  case, not just its own. Put probes inside functions.
- **Changing a return type breaks a case in a way that looks unrelated.** T1-3
  changes `replay_template` from `str` to `dict`; the existing case calls `.lower()` on
  the result. Update it in the same write.
- **Three items edit `flag_farm.py` and one more edits it in T1.** Interleaving them
  is how the pending/seen bookkeeping breaks. One at a time, gate between.
- **`check_boundary.py` scans everything you write under `tools/` and at the root.**
  `DECLARES_BOUNDARY` keys on the relative path, so only the **root** `README.md` is
  exempt. Writing a blocked token into a file in order to warn about it fails the
  required gate — proved, 2 violations. Run `python3 tools/check_boundary.py`
  immediately after saving a document rather than waiting.
- **Generated files must never be hand-edited:** `knowledge/bug-classes.json`,
  `skills/INDEX.md`, `skills/registry.json`. And adding a skill moves
  `knowledge/skill-audit.json`'s summary count, which the gate compares against a live
  audit — so `tools/skill_audit.py --apply` is mandatory after any skill change. This
  is the main reason the knowledge layer is T3.
- **Fixture names are a trap.** `*.pcap`, `*.log`, `**/baseline.json`,
  `**/state.json`, `.env`, `*.key`, `*.pem`, `*.token` and `*.secret` are all
  gitignored, so a fixture with one of those names is silently untracked: the gate
  passes here and fails on a fresh clone. Use `.txt`, `.jsonl`, `.fields` or
  `.ndjson`.

### Operator failure modes at hour four

- **Disabling a guard instead of reading it.** Every guard in T0 is written with its
  escape hatch in the message — `sla_check`'s vanished-check reason names `--save` as
  the legal move, the host validator refuses a range but accepts
  `web1-2.example.com`. A guard that refuses a valid input is a guard that gets
  commented out.
- **Trusting a stale artifact.** `tick.py`'s rule that a missing or stale file is
  **unanswered, never green** exists for this. So does `facts_missing`: a blind tool
  must look obviously blind.
- **Patching by deleting the feature.** The RUNBOOK names it and T0-2 is what makes
  the naming true.
- **Rotating a credential from your only session.** Before any rotation, add your own
  key, open a **second** already-authenticated session and leave it open. Note that
  `sudo -n true` prints "a password is required" and exits 1 on this box, so a
  non-interactive privilege check is not guaranteed — prove privilege interactively in
  that second session.
- **Reading `immune` as "they patched" when the host is simply down.** In a
  post-ransomware phase 1 that is the default state for the first hour. T1-2 is the
  fix; until it lands, check `per_team[].status` before inferring a patch.
- **Filling the disk with a capture** and taking down the availability the capture was
  protecting. The ring buffer in T0-6 is the fix; `df -h` every time you check the
  scoreboard is the habit.
- **Restoring a snapshot that still contains the implant.** The mechanical test:
  compare the implant's creation time against the snapshot's own timestamp. If the
  implant is older, the snapshot contains it. That requires a filesystem-metadata
  baseline **before** the first restore, which is why order of volatility is in the T0
  runbook.

### Authorization limits

- Only hosts the organiser listed, typed individually into the `flag_farm` config,
  read back by a second person. No range, no wildcard, no adjacent address, no
  organiser infrastructure. T0-4 makes the guard real; until it lands, the operator
  **is** the guard and the documents must say so.
- Defensive work is on your **own** estate. The line is whose host it is, not how low
  in the stack the work sits. Section 11 proposes the wording that makes that explicit;
  until it is approved, the collision between `AGENTS.md` section 7 and the runbook's
  own section 3 is real and an agent may reasonably refuse.
- If the event forbids AI assistance, this toolkit is for practice before the contest,
  not during it.
- Never commit a real flag, a credential, or state holding sensitive evidence.
  Everything contest-shaped goes under `runs/`, which `.gitignore` line 18 already
  covers — but `*.seen` is ignored **nowhere else**, so a farm config outside `runs/`
  puts real flags into history.

### The degrade plan

If the build runs out of time, degrade in this order, and only in this order: drop T3
entirely (already done); drop T2 to the morning; drop T1 to a ranked queue and take
only `ad-readme-corrections` and `ad-immune-honesty`; then fall back to section 6's
three items; then to item 2 alone. If the contest itself runs out of time, use the
abort ladder in T0-6 — and never drop credential rotation, `--compare` before a patch,
or the baseline capture, because each is unrecoverable later.

---

## 11. Proposed edits to `AGENTS.md` and `CLAUDE.md`

**These are proposals.** `AGENTS.md` edits are approved first, by convention and by
the operator's own instruction. Do not apply any of this unasked. Bundle all of it
into **one** approval: `AGENTS.md` is always in context via `CLAUDE.md`'s
`@AGENTS.md` import, so every edit costs every future session a re-read.

Apply only **after** `tools/ad/tick.py` exists, because
`test_every_tool_path_named_in_prose_resolves` reads `AGENTS.md` and requires every
`tools/<...>.py` it names to resolve. Note the reverse: that regex matches `.py` only,
so a `.sh` path in a row is **not** gate-checked and must be proofread by hand.

Three further constraints, verified: `AGENTS.md` must keep naming `tools/decide.py`,
`tools/hooks.py`, `tools/skill_audit.py`, `tools/search_facts.py` and
`tools/handout_inventory.py`; it must not contain the case-insensitive substrings
`password spray`, `ssh pivot`, `lateral movement` or `root flag`; and no edit may
introduce a probe-and-minute budget pair other than the two `tools/decide.py`
enforces. `AGENTS.md` and `CLAUDE.md` are both in `check_boundary.py`'s
`DECLARES_BOUNDARY` set, so the replacement text below may name Active Directory in
prose.

### Proposal 1 — the scope sentence (`AGENTS.md` section 7)

The bullet **wraps across lines 235-236** with a two-space continuation indent —
confirmed with `cat -A`. An exact-match edit must include the line break.

Current, verbatim:

```
- **No red team**: every machine, Active Directory or box privilege-escalation
  technique belongs to the other toolkit and is out of scope here.
```

Proposed replacement:

```
- **No red team**: every machine, Active Directory or box privilege-escalation
  technique belongs to the other toolkit and is out of scope here. Attacking a
  host to gain a foothold is that toolkit's job, not this one's.
- **Defending a host you were handed is in scope.** In attack-defense the estate
  is issued to you and keeping it alive is the scored task: rotating the
  credentials that shipped in the image, reading cron, timers, units and
  `authorized_keys` for what the organiser planted, patching a service without
  breaking its checker, and copying evidence before it is destroyed. That is
  defence of your own assets, under `tools/ad/` and the `dfir-*` classes. The
  line is whose host it is, not how low in the stack the work sits: inventory and
  remove on your own estate, yes; escalate or take something on someone else's,
  no — and the only hosts you may touch at all are the ones listed individually
  in the contest's own team list.
```

The permissive half is bounded twice — "your own estate" and "listed individually in
the contest's own team list" — and the forbidden direction is named first. If this is
declined, the fallback is a one-line note in `tools/ad/RUNBOOK.md`; the collision is
real either way and must be recorded somewhere an agent will read.

### Proposal 2 — one consolidated tool-table row (`AGENTS.md` section 2)

Insert after the `knowledge/attempts/` row, which is the table's last line. One row,
not three, because three rows pin three filenames the gate resolves on every run:

```
| `tools/ad/` | attack-defense only: `sla_check` (the service's own health checks; `--compare` refuses a patch that broke something which previously passed), `flag_farm` (one exploit against every listed team each tick, duplicate-suppressed, with the `immune` list naming who has already patched), `traffic_mine` (rank your own capture against the organiser's checker baseline and get a replay command), `cap_split` (turn a capture into the raw requests `traffic_mine` wants), `tick` (the next action for one service, from `runs/<service>/ledger.json`). `tools/ad/RUNBOOK.md` is the first thirty minutes and `tools/ad/PREFLIGHT.md` is what to install and what degrades. `python3 tools/ad/selftest.py` proves the decision logic offline |
```

### Proposal 3 — one branch-table row (`AGENTS.md` section 1)

Insert after the "Resuming one" row, which is line 46:

```
| **Attack-defense contest, not jeopardy** | `cat tools/ad/RUNBOOK.md`, then `python3 tools/ad/tick.py runs/<service>/ledger.json` — the sibling loop under `tools/ad/`. `tools/decide.py` and `tools/hooks.py` are the jeopardy controller and do not run here |
```

### Proposal 4 — a subsection in `AGENTS.md` section 3

Insert after the hard-rules list (which ends at line 132) and before "One question per
iteration":

```
### Attack-defense is a different loop

`tools/decide.py` budgets probes against one target and `tools/hooks.py` gates one
verified flag. Neither fits a contest where the flag rotates every tick, where you
are also the target, and where availability is scored. `tools/ad/` is a sibling
control plane: it never writes `challenges/<name>/state.json`, never calls
`hooks.py`, and keeps its own per-service ledger under `runs/<service>/`.

- The unit of state is **one service**, not one challenge:
  `runs/<service>/ledger.json`, owned by `tools/ad/tick.py`. `tools/state.py` must
  not read or write it.
- Defensive work is never budgeted. A controller that tells you to stop patching
  costs availability, and availability is the scored resource.
- Offensive work is budgeted in ticks: one open exploit idea per service, parked
  after two ticks with no flag, and at most one unverified patch in flight so a
  regression can be attributed to the patch that caused it.
- A defensive claim — "the persistence is evicted", "nothing was exfiltrated" —
  has no response behind it, so it is recorded with the command, its verbatim
  output, the coverage boundary and the recheck that would fail if the claim were
  false. `EVIDENCE_POLICY.md` holds the three grades; `tick.py` refuses an
  absolute-absence claim that names no coverage boundary.
```

### Proposal 5 — `CLAUDE.md`

Insert one row after `| Accepting a change to this system | test/run_all.sh |`, which
is line 34 and the table's last row:

```
| Running an attack-defense contest | `tools/ad/RUNBOOK.md` + `tools/ad/tick.py` |
```

And append two sentences to the Scope paragraph, which ends at line 41 with "not
during it." — the sentence wraps, so match on `during it.`:

```
Attack-defense runs a sibling loop under `tools/ad/`: `tools/decide.py` and
`tools/hooks.py` are the jeopardy controller and do not apply there. The proof
standard still does — a flag comes from a live response or a supplied artifact.
```

### Also stale, and worth fixing under the same approval

`AGENTS.md` section 0 says `52 skills: 8 thin routers + 25 bug classes` and
`bug-classes.json (25 classes) · chains/ (58 verified cards)`. Measured today: 60
skills, 9 routers, 32 classes, 69 chain cards, 56 solved notes. Re-count with
`ls -d skills/*/ | wc -l` and a `Counter` over `skills/registry.json`'s `skills` list
before writing any number, and write only what actually shipped.

---

## 12. Status

**Built, and verified by running it:** nothing in this plan. Every item below T0-1 is
unbuilt. What exists and works is the list in section 2: `tools/ad/`'s three tools
with a 16/16 offline selftest wired into a passing gate, `tools/forensics/` with a
passing selftest, eight `dfir-*` skills that are all `catalogue`, and a contest-day
runbook.

**Specified but unbuilt:** every item in sections 4 and 7. The specs carry real line
numbers, real command invocations and real measured failure modes, so a builder can
start at T0-1 without asking a question — but no line of any of it has been written,
and the minutes are estimates, not measurements.

**Measured on 2026-09-29, and safe to rely on:** the seven defects described in
sections 2 and 3 were each reproduced, not inferred — the `seen`-before-`submit`
ordering both by driving `tick()` and by running the real CLI twice; the five accepted
host notations; the capturing-group `findall` behaviour; the deleted **and** renamed
`sla_check` blindness; the `follow`-pipeline garbage with its 11 `HTTP/1.0`
occurrences; the credential-carrying replay; and the `immune` timeout/error/patch
confusion. The apt candidates, the `getcap` capabilities, the port occupancy, the
`.gitignore` rules, the `BLOCKED` and `DECLARES_BOUNDARY` sizes, the absent binaries
and the tree's own `last -f` self-contradiction were all checked directly.

**Guessed, and labelled as guesses everywhere it matters:** that duplicate submissions
are penalised by this event's scoreboard — an assumption about scoreboards in general;
that the scoreboard is the most loaded host in the contest — plausible and unmeasured,
though the durability argument does not depend on it; and every estimate in the
minutes column. The build-minute totals have already been revised once from an
optimistic 205 to a measured-out 315 by one layer and from 280 to 335 by another, so
treat the tier boundaries as the commitment and the individual numbers as guidance.

**Unknown, and cannot be resolved tonight:** everything in section 9. The scenario is
a reconstruction. Nothing is published about topology, OS mix, service list,
ransomware family, CVEs, flag format, tick length, SLA definition or scoring weights,
and every item in this plan is organised by format and by mechanism for exactly that
reason.
