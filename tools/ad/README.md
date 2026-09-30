# tools/ad — the attack–defense control plane

Jeopardy and attack–defense are different games, and this tree was built for the
first one. `tools/hooks.py` gates **one** verified flag; `tools/decide.py` budgets
probes against **one** target; a chain card records **one** solve. None of that
fits a contest where the flag rotates every tick, where you are also the target,
and where the best source of exploits is your own inbound traffic.

So this is a sibling control plane, not a replacement. It does not write
`challenges/<name>/state.json` and it does not go through `hooks.py`. The
jeopardy loop is untouched.

Placed here rather than in a separate tree on purpose — the measurement behind
that choice is in the `ctf-v2-specialize-tools-not-split-tree` memory: `skills/`
does not bloat per-session load, and what was actually web-biased was `tools/`.

## The four assumptions that change

| Jeopardy (the rest of this tree) | Attack–defense (here) |
|---|---|
| one target, one flag, `hooks.py pre-flag` is the finish | flags rotate every tick; you need a farm, not a verdict |
| you only attack | you are also the target, and availability is scored |
| hypotheses come from source and chain cards | the best ones arrive in your own capture, written by other teams |
| a probe budget stops you sinking time | over-patching costs more than the exploit did |

## The tools

| File | What it is for |
|---|---|
| `sla_check.py` | run the service's own health checks; `--compare` refuses a patch that broke something which previously passed, including a check that was deleted or renamed |
| `flag_farm.py` | run one exploit against every team every tick, submit new flags, hold a flag as *pending* until the scoreboard really accepts it, and name the teams that have stopped yielding |
| `traffic_mine.py` | rank captured requests against a baseline and hand back a replay template — this is how you steal another team's exploit |
| `cap_split.py` | turn a capture into the one-request-per-file input `traffic_mine.py` wants. A `tshark -q -z follow,tcp,ascii,<n>` dump cannot do this: it carries the server's response into the request, and then into the replay command |
| `selftest.py` | offline proof of all of the above; no network, no sockets, no subprocess |
| `RUNBOOK.md` | the first thirty minutes, and the steady-state loop |
| `PREFLIGHT.md` | the night before: what to install, what cannot be installed here, and what degrades without it |

Each `.py` prints JSON on stdout, like the rest of the tree.

## The skills that go with them

Five exist, and every one is `evidence_level: catalogue` — standard published
knowledge, with no solve in this tree behind it. Treat them as checklists, not as
experience, and record what actually happened in their field notes.

| Skill | When |
|---|---|
| `skills/ad-service-triage/SKILL.md` | first, once per service. Routes; never solves |
| `skills/ad-traffic-mining/SKILL.md` | as soon as any other team has attacked you |
| `skills/ad-patch-without-breaking-sla/SKILL.md` | before the first patch, and before every one after it |
| `skills/ad-planted-backdoor-hunt/SKILL.md` | immediately after rotating credentials |
| `skills/ir-live-estate-triage/SKILL.md` | when the estate has already been hit and recovery is scored too |

The eight `dfir-*` skills cover the incident-response half of the scenario. All
eight are `catalogue` as well.

## The one output to read every tick

`flag_farm.py` prints `immune`: the teams that ran the exploit to completion and
returned nothing while the others returned flags. They have patched, and their
patch is the shortest and most precise description of the bug you are exploiting
— reading it is faster than re-deriving it. That is why this tool reports per
team rather than a total.

A team can return no flag for three different reasons and only one of them is a
patch, so the non-yielding teams are split by the status that was actually
recorded. Read the one that matches before acting:

| Field | What was recorded | What it is evidence of |
|---|---|---|
| `immune` | the exploit ran to completion and produced nothing | they patched — go read the patch |
| `unreachable` | the exploit timed out | their availability, not your bug. One manual curl, not a patch hunt |
| `exploit_broken` | the exploit raised before it could finish | your own exploit. Fix it before reading anything into the tick |

Each carries a `*_note` that says the same thing in the output itself, and each
is empty when it has nothing to claim. In the first hour after an incident hosts
being down is the default state, which is exactly when a single list that
swallowed timeouts would be trusted most and be most wrong.

## Guards, deliberately

`flag_farm.py` refuses to start unless the config names an `authorized_event`,
and every team host goes through `check_host()`, which accepts one explicit
address or one hostname and nothing that can expand into more than one. There is
no discovery and no expansion in this tool. Measured on 2026-09-29 against the
code in this directory: eight range, list and metacharacter notations
(`10.60.1.0/24`, `10.60.1.*`, `10.60.1.1-254`, `10.60.1.{1,2}`,
`10.60.1.1,10.60.1.2`, `10.60.1.[1-9]`, `$(id)`, `a;id`) were all refused, and
four legitimate single hosts (`10.60.1.1`, `web1-2.example.com`,
`team_3.ad.local`, `2001:db8::1`) were all accepted. The second number matters as
much as the first: a guard that rejects `web1-2.example.com` is a guard the
operator switches off at hour four.

Be precise about what that buys. `run_exploit()` calls
`subprocess.run(argv, ...)` with no `shell=True`, so a metacharacter in a host
was never a shell injection into `flag_farm.py` itself. The exposure the guard
closes is one level out: a range reaching a tool the operator's **own** exploit
shells out to, or an exploit script that uses `$1` unquoted. Measured here,
`nmap -sL -n '10.60.1.*'` prints `Nmap done: 256 IP addresses (0 hosts up)
scanned`. One typo in a config turns one exploit into a sweep of 256 addresses
the event did not assign you.

`load_config` reports **every** offending team rather than the first, so an
operator fixing a twelve-host list does not learn about one error per run.

`CLAUDE.md` scopes this repo to authorized CTF and lab work, jeopardy and
attack–defense; that scope is what this directory is for.

## Status — measured 2026-09-29

Earlier versions of this file said none of this had been executed. That is no
longer true, and the sentence is removed rather than softened. What follows was
run on this box on the date in the heading.

- `python3 tools/ad/selftest.py` → `{"mode": "ad-selftest", "cases": 76,
  "passed": 76, "failed": [], "offline": true}`. The count rises as cases are
  added, so treat 76 as the figure on the date above; what has to hold is
  `passed == cases` with `failed: []`. It is pure-function only — no sockets, no
  subprocess, no non-stdlib import — which is what makes it safe to run inside
  the gate.
- `flag_farm.py` on a config with no `authorized_event` and two CIDR/wildcard
  hosts exits **1** with all three problems listed at once, before any network
  call.
- `flag_farm.py --once --dry-run` with two teams whose exploit returns the same
  flag reports `new_flags: 1`, `total_unique: 1`, `pending_flags: 1`, and a
  `pending_note` saying the flags are held, not lost.
- the same tool with three teams — one returning a flag, one sleeping past
  `exploit_timeout`, one exiting non-zero with no output — reports
  `teams_yielding: [1]`, `unreachable: [2]`, `immune: [3]`, `exploit_broken: []`.
  A single non-yielding list would have claimed two patched teams where there was
  one.
- `sla_check.py` on a spec with no checks exits **3** — not 1 — with
  `"a spec with no checks always passes, which is worse than no check at all
  because it reads as a green light"`.
- `sla_check.compare()`: a check that passed and now fails → `REVERT THE PATCH`;
  a check that passed and has **vanished** from the spec → `REVERT THE PATCH`,
  naming the missing check; a check that was already red and is still red →
  `safe to keep`. The asymmetry is deliberate and is the third case, not the
  second.
- `cap_split.py --from-fields tools/ad/fixtures/http_requests.fields` rebuilt
  **4** requests from 3 streams and skipped **3** malformed rows.
- `traffic_mine.py` over those 4 live requests against a 2-request baseline
  returned **3** ranked candidates, top two scoring 9, each carrying its own
  reasons (`path /static never appears in the baseline`, `payload looks like path
  traversal`) and a `curl` replay line that contains the request only.

Not measured by this edit: the wall-clock cost of `bash test/run_all.sh`, and
whether the gate passes with the current working tree. Run it yourself before
treating any change here as accepted.

## Defects found by reading the code before it ever ran

Kept because they say what kind of mistake to look for in the rest of this
directory. All four are fixed; the location of each fix is named so the claim is
checkable.

- `traffic_mine.score()` matched only the raw query and body. Real payloads are
  URL-encoded, so `id=1'%20OR%201=1--` never matched a pattern written with
  `\s+`. **Fixed** — `score()` now builds its blob from the path, query and body
  and scans both the raw and the `unquote_plus` form.
- the Java serialization magic bytes `AC ED 00 05` were unmatchable: the capture
  is decoded with `errors="replace"`, so those bytes arrive as U+FFFD. **Fixed** —
  the deserialization pattern in `SUSPECT` now uses `rO0AB`, the same header in
  the base64 form it travels in.
- `flag_farm.run_exploit()` scanned only stdout, and carried a leftover
  `proc.returncode * ""`. **Fixed** — it now concatenates stdout and stderr
  before extracting. Losing a flag because the exploit printed it to the other
  pipe is a silly way to lose points.
- `flag_farm.tick()` compared `t.get("id") != cfg.get("skip_self")`, which
  silently dropped every team with no id when `skip_self` was unset. **Fixed** —
  `tick()` only filters when `skip_self is not None`, and `load_config` sets a
  `_warnings` entry when it is unset, because without it your own team is in the
  attack list.

## What the gate does and does not cover here

State this precisely, or the next builder orphans a top-level tool on the
strength of a half-remembered rule:

- `test_every_tool_is_named_somewhere` globs `(ROOT / "tools").glob("*.py")` —
  **top level only**. Nothing in `tools/ad/` is visible to it, so that check will
  never notice an undocumented tool in this directory. Documenting a new file
  here is a discipline, not something the gate enforces.
- `test_every_tool_path_named_in_prose_resolves` **does** match
  `tools/ad/<name>.py` wherever it is written, and requires the file to exist —
  but its sources are `skills/**/*.md`, the control-plane list, `AGENTS.md` and
  `.claude/commands/*.md`. This README is not among them. Naming a file here that
  does not exist fails silently.
- `test/run_all.sh` runs `tools/ad/selftest.py` in its tool-layer selftest loop
  (line 37 as of this writing), next to `tools/web`, `tools/crypto`,
  `tools/pwnstatic` and `tools/forensics`. That is the one place this directory is
  genuinely gated, and it is why the selftest must stay stdlib-only.

`AGENTS.md` already carries this layer: one row in the branch table for an
attack-defense contest, and one consolidated `tools/ad/` row in the tool table.
No more rows are needed.

## What is missing

The knowledge layer is no longer empty — five skills landed, listed above — but
none of them is backed by a solve in this tree. The remaining gaps, and the
things that cannot be fixed on this box at all, are in `PREFLIGHT.md` with the
measurement behind each. Read that rather than a wishlist here.
