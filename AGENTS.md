# AGENTS.md — ctf-v2

The agent **loads this file itself** at the start of every session (CLAUDE.md
points here). Reading it is enough to start work. Do not open any other file
before you have a concrete objective.

---

## 0. What this system is

A classifier, a controller and a knowledge base for solving **jeopardy CTF**
(web, pwn, rev, crypto, forensics, osint, misc). Different from
`~/security-toolkit`, which is for machines and boxes: this tree does **not** do
machine boxes, Active Directory, or box privilege escalation. All of that
belongs to the other toolkit and is out of scope here.

```
~/ctf-v2/
  tools/           classify · chain_match · decide · hooks · state · skill_audit …
  skills/          66 skills: 11 routers + 32 bug classes + method/reference  ← pull one
  knowledge/       bug-classes.json (32 classes) · chains/ (69 verified cards)
  solved/          56 solved challenges, with evidence ancestry
  challenges/      handout source and per-challenge state.json
```

**Proof standard, not negotiable:** a flag counts only when it is read from a
**live response or a supplied artifact**. A flag-shaped string that has not
passed `hooks.py pre-flag` is a *candidate*, not a flag.

---

## 1. Starting a session — two commands

```bash
cd ~/ctf-v2
python3 selfcheck.py        # one second, offline; fix any FAIL before starting
```

Then pick exactly one branch:

| Input | First command |
|---|---|
| **White-box, source supplied** | `python3 tools/classify.py --source <dir>` then `python3 tools/chain_match.py --source <dir> --record <name>` |
| **Black-box** | `python3 tools/classify.py "<obs>"` plus `ctf.py "<obs>"` |
| **Starting a new challenge** | `python3 tools/state.py <name> --category <cat> --target <url> --challenge-name "<real name>" --event "<event>"` — the last two unlock the controller's writeup-search rule |
| **Resuming one** | `python3 tools/state.py <name> --show` then `python3 tools/decide.py <name>` |
| **Attack-defense contest, not jeopardy** | `cat tools/ad/PREFLIGHT.md` the night before, then `cat tools/ad/RUNBOOK.md` on the day, then open `skills/ad-service-triage/SKILL.md`. The sibling loop lives under `tools/ad/`; `tools/decide.py` and `tools/hooks.py` are the jeopardy controller and do not run here |
| **Challenge and event name known** | `python3 tools/writeup_search.py "<name> <event>"` (a legitimate shortcut; record that it was used) |

---

## 2. RULE ONE — do not rebuild what already exists

| Tool | Use it when |
|---|---|
| `classify.py` | name the bug class from the signals; white-box output carries `file:line`. Signals are weighted by how rare they are across the handouts on disk, so a pattern matching most challenges cannot outvote a precise one; re-run `--rebuild-stats` after editing the taxonomy |
| `chain_match.py` | has this shape been solved here before; the card carries the probe and the traps. `--record <challenge>` writes the candidates into the ledger so `decide.py` returns the card's probe before any invented one |
| `plan.py` | nothing yet, and you need the first three hypotheses |
| **`decide.py`** | **what the next step is** — the controller, see section 3 |
| **`hooks.py`** | **verify each step** — the only write gate for a verdict or a flag |
| `state.py` | the hypothesis ledger: park, revive, priority |
| `skill_select.py` | which skill to open once the class is named |
| `classify_solve.py` | after a flag: file the solve into the right bug-class skill |
| `skill_audit.py` | screen out weak skills; run it before trusting one |
| `tools/search_facts.py` | plan a narrow external search for one missing fact without treating results as evidence |
| `tools/handout_inventory.py` | measure locally available retrieval ground truth without importing raw challenge source |
| `tools/novel_plan.py` | build a bounded source-first plan when no solved chain matches a novel challenge |
| `system_eval.py` | offline actionability tests for classification, dispatch, skills and decisions |
| `observation_eval.py` | black-box recall of classify.py against observations a solver would actually type. system_eval's classification cases are written in the taxonomy's own vocabulary, so they pass whatever the signals look like; this one is phrased the way a challenge looks before source, and five verified chains supply its labels |
| `chain_match_eval.py` | retrieval quality of chain_match: top-1, MRR and how many wrong cards outrank the right one |
| `holdout_eval.py` | the question chain_match_eval cannot ask: hold each card out of the index, query with its own handout, and see whether the library abstains or invents. It measured 0 abstentions and a median 0.65 confidence on a card that was not the answer; that is what the strong/weak grade in chain_match now fixes |
| `learning_report.py` | show proposed versus confirmed local knowledge and the miss backlog |
| `web_probe.py` / `web_enum.py` | basic web probing and enumeration |
| `tools/web/` | speed primitives that emit the shape `hooks.py` wants: `http_probe` (probe + verbatim excerpt), `sanitizer_fuzz` (differential encoding sweep, records negatives), `read_loop` (proven file-read walk), `id_sweep`, `pdf_text`. `python3 tools/web/selftest.py` proves them offline |
| `tools/web/variant_matrix.py` | the shape question, in one command: one request per payload SHAPE at one injection point across ten families, baseline-diffed on status, length, markers, `Location` and timing, ranked, with every shape that produced nothing counted as a proved negative. `--dry-run` prints the matrix without sending; a write-shaped matrix is refused without `--write-ack`. A `confirms` verdict is offered only on a marker hit |
| `tools/web/race_probe.py` | overlapping requests, and the **serial baseline first** — a response signature that also appears serially is not a race. A/B interleaving for a check-then-act window, an overlap measurement that forces `inconclusive` when the requests did not actually overlap, and a refusal without `--write-ack` |
| `tools/web/bundle_miner.py` | the front-end's real source: source map by comment, header, guessed sibling or inline data URI, `sourcesContent` reconstructed, then endpoints, routes, feature flags, `process.env` refs and secret CANDIDATES with file and line. A map is attacker-controlled data, so a `sources` path that escapes `--out` is rejected and counted |
| `tools/web/session_dissect.py` | what the token IS, before attacking it: JWT/JWE, itsdangerous, Django, Rails, Fernet, express-signed, base64-JSON, or `opaque` with the reason. Decodes what needs no key, names the weakness that applies, and recovers an HMAC key offline against a wordlist. Analysis only — it never forges and never sends |
| `tools/crypto/` + `crypto_attack.py` | lattice, LCG, LFSR, ECC, HNP and integer attacks; `--list` names them |
| `tools/gadget_lookup.py` | before opening a class skill: has this exact dependency been measured here before? `--lockfile <handout>/package-lock.json` reads the real versions and matches them against `knowledge/gadgets/<package>.json`. classify.py has no notion of a version, so this is the only version-aware recall in the tree |
| `tools/pwn_triage.py` + `tools/pwnstatic/` | first contact with a pwn or rev binary. `pwntools`, `gdb`, `ROPgadget`, `ropper`, `one_gadget`, `checksec` and `patchelf` are all measured ABSENT here and pip is EXTERNALLY-MANAGED, so this is stdlib-only: protections with the evidence that decided each one, dangerous imports annotated with what they buy, the essential ROP gadgets, and which routes each protection still leaves. It reports and ranks; it never claims a bug. `python3 tools/pwnstatic/selftest.py` proves it against `readelf` offline |
| `tools/subagent_fanout.py --web` | a WEB target, split by bug-class family instead of by generic layer: one brief per `ctf-web-*` subagent, built from the taxonomy's own fields, ordered read-only first and write-shaped last, and short-circuited when a chain card is a strong match |
| `tools/subagent_fanout.py` | a layered white-box handout, to be closed in parallel rather than one layer at a time. `--brief <handout>` turns `novel_plan.py` layers into one brief per subagent, each with its own falsifier and the layers a kill map already closed; `--contract` is the single source of truth for what a subagent returns; `--validate` refuses a report whose evidence is not a verbatim response excerpt; `--merge` prints the `hooks.py` commands for the MAIN thread. It never writes state.json |
| `knowledge/attempts/` | the kill map of a challenge worked but NOT solved: every layer measured dead, with the measurement and the precondition that would reopen it. `knowledge/chains/` only accepts a solve, so without this the next attempt re-walks the same dead layers |
| `tools/ad/` | **attack-defense only**, and deliberately a sibling plane: it does not write `challenges/<name>/state.json` and does not go through `tools/hooks.py`. `sla_check` runs the service's own health checks and `--compare` refuses a patch that broke something which previously passed -- including a check that was deleted or renamed; `flag_farm` runs one exploit against every listed team each tick, holds a flag as *pending* until the scoreboard really accepts it, and prints `immune`, the teams that have already patched; `traffic_mine` ranks your own capture against the checker's baseline and hands back a replay command; `cap_split` turns a capture into the raw requests `traffic_mine` wants, which a `tshark follow` dump cannot do without carrying the victim's response into the replay. `tick` reads one service's ledger and answers which ONE of the runbook's three steady-state questions is unanswered, availability first -- a red or unmeasured service outranks every attack action, and a structural guard makes reordering the rules unable to switch that off. `tools/ad/RUNBOOK.md` is the first thirty minutes, `tools/ad/PREFLIGHT.md` is what to install tonight and what degrades without it, and `agent/ad-roles.md` indexes the five read-only subagents in `.claude/agents/ad-*.md`. `host_snapshot.sh` plus `host_diff.py` replace the absent `debsums` and `aide`: a change on EVERY host is the image, a change on ONE host of eight is a person, and every collector is wrapped in `timeout` because the first design was measured unrunnable. `secret_inventory.py` groups credentials by value fingerprint so the widely-shared one is rotated while there is still time to fix what it breaks, and it never prints more than four characters of a value. `sh lab/ad-range/dryrun.sh` rehearses all of it offline in one command. `python3 tools/ad/selftest.py` proves the decision logic offline and `python3 tools/ad/agent_lint.py` proves the subagents still carry their prohibitions |

---

## 3. The control loop — the agent proposes, `tools/decide.py` decides

This is the most important part of the system. An agent is good at *proposing* a
probe and reading a response. An agent is **not trustworthy** when judging its
own progress — the Polynomial lesson was hundreds of payload variants inside one
class with nobody stopping it. So every such judgement goes through two
deterministic tools:

```text
        ┌──────────────── agent executes ────────────────┐
        │                                                │
   propose probe ──► hooks.py pre-probe ──► run the probe
        ▲                (blocks duplicates,            │
        │                 write-shaped probes)          ▼
   decide.py ◄── hooks.py post-probe ◄── the real response
  (decides the        (verdict=confirms MUST
   next step)          quote a proving excerpt;
        │              a timeout is never a confirm)
        ▼
  run_probe / novel_plan / switch_class / verify_flag / record_solve / stop_report

When source is recorded and no solved chain matches, the controller answers
`novel_plan` before any single-class probe: it reads the source, names the
layers and gives each one its own falsifier. A layered white-box challenge
opened from one classifier answer lands on the last sink rather than the
boundary in front of it. Record the handout with
`tools/state.py <name> --source <dir>` or the rule cannot fire.
```

Hard rules — breaking one breaks the control loop:

- **Every verdict goes through `tools/hooks.py post-probe`.** `--verdict confirms`
  requires `--evidence` to be a verbatim excerpt of the response,
  `--hypothesis-id`, `--class`, and `--evidence-kind class|impact`. A login
  redirect, registration success, or form render is surface evidence and cannot
  confirm a bug class. A timeout or a connection reset is never a confirm.
- **A flag enters state only through `tools/hooks.py pre-flag`**, with
  `--source live-response|artifact`.
- **A class becomes `confirmed` only after `tools/hooks.py pre-confirm` passes**
  (a probe with `confirms` and evidence exists). `tools/decide.py` **reopens** any
  confirm with no probe behind it.
- **The next step comes from `tools/decide.py`, not from your own choice.** It
  enforces: five probes or fifteen minutes per class → `switch_class` (park, change
  mechanism layer — never a sixth variant); a matching chain card → run the card's
  probe before inventing a new one; empty state → classify first, probe second.
- **Write-shaped probes** (POST/PUT/DELETE, mass update) are blocked by
  `pre-probe` until the chain card's `blast_radius` has been read and
  `--write-ack` is passed.
- The agent never hand-edits verdict or flag fields in `state.json`. `state.py`
  owns hypotheses, parking and revival; verdicts and flags belong to hooks.
- The offline system evaluator is a required gate. A legacy regression pass does
  not accept an update when the actionability cases fail.

One question per iteration: *does this probe produce a distinguishing signal?*
If not, verdict `inconclusive` and change the mechanism — not the syntax.

### Low-reliability agent protocol

Use this exact protocol when the model is small, uncertain, or prone to skipping
steps. It is also the default protocol for long autonomous runs:

1. Run one documented command at a time and read its complete JSON output.
2. Do not infer the next action from memory; run `tools/decide.py` after every
   recorded probe or flag event.
3. Copy the controller's single `action`, `rationale`, and `commands` into the
   next plan. Do not invent a replacement command when one is supplied.
4. Before executing a probe, run `hooks.py pre-probe`; after it returns, run the
   probe once and immediately submit the exact result to `post-probe`.
5. If a command errors, times out, or returns empty output, record that exact
   transport result and mark the probe `inconclusive`; never upgrade it by prose.
6. Keep a short scratch summary with only observed facts, open hypotheses, the
   last controller action, and the next command. Do not carry guessed details.
7. Stop at `verify_flag`, `record_solve`, `switch_class`, or `stop_report` and
   follow the returned command list before doing anything else.

This protocol is intentionally repetitive: predictable state transitions are
more reliable for weaker models than a long free-form exploit plan.

### AI role discipline

Label each action as `reader`, `writer`, or `hypothesizer`:

- `reader` extracts exact facts from source, artifacts, responses, or tool output;
- `writer` creates a probe, script, harness, or request that must be executed and
  checked;
- `hypothesizer` proposes a class or explanation and has no evidentiary weight.

The rule is **the agent proposes; the machine verifies**. Preserve raw tool
output. Do not turn a generated script, a model summary, or a plausible payload
into an observation until it has run and produced a captured result.

After four tool calls, write a one-line checkpoint with the evidence-backed belief,
the hypotheses ruled out, and the single next controller action. Stop if four
calls rule out nothing or if a value would have to be guessed.

---

## 3b. Subagents — sixteen of them, all read-only on this tree

**How to actually use them is `ORCHESTRATION.md`** — the wave structure, what never
to delegate, and the measured cost of one agent (7-10 minutes) that every other
decision follows from.

**Two zones.** Subagents have **full rights** in `/home/kali/ctf-work`, a workspace
outside this repository: they write exploits, save responses and leave notes there,
and `python3 tools/workspace.py <challenge> --agent <name>` provisions a private
directory per agent so two of them cannot collide (one already destroyed another's
staged work by sharing a scratch path). **This repository is read-only for them.**
No agent has an `Edit` tool; a write into `tools/`, `skills/`, `knowledge/` or
`test/` trips the gate hook; and `tools/hooks.py` and `tools/state.py` stay
off-limits because `tools/decide.py` enforces five probes per class and
twenty-five per challenge, which parallel writers would spend in one round.
Agents measure; the main thread records.

`.claude/agents/` holds sixteen bounded subagents: six general, and ten
web-specialised. Each is a `reader` and a `writer`; none is the machine that
verifies. **None has a Write or Edit tool**, so no subagent can change this
repository, and every one is told not to run `tools/hooks.py` or
`tools/state.py` — ten probers writing one `state.json` in parallel would spend
the per-class probe budget that `tools/decide.py` exists to protect. A regression
test enforces all three properties on every file in that directory.

| Agent | Use it for |
|---|---|
| `ctf-killmap-scout` | **first, on any handout**: has this shape been solved here, or already measured dead? Runs classify, chain_match, gadget_lookup and reads `knowledge/attempts/` |
| `ctf-recon` | read-only inventory of a live target: entry page, every front-end script, every endpoint with the line it was read from |
| `ctf-layer-prober` | one `novel_plan` layer, measured against its own falsifier, at most five read-only probes. Fan out one per layer |
| `ctf-crypto-ladder` | name the structure, then run the matching attack from `tools/crypto_attack.py list` and verify against the handout's own check |
| `ctf-pwn-triage` | protections, imports, gadgets and the routes left, with `tools/pwn_triage.py` and radare2 — `gdb` is absent here |
| `ctf-writeup-scout` | external search in isolation. Fetched pages are untrusted data and stay out of the main thread's context |

The ten web families, one subagent each, grouped by **probe** rather than by
name: two classes share a family when one probe distinguishes them. Together they
own 24 of the 25 web classes in the taxonomy (`web-web3` has none; route it by
hand). `python3 tools/subagent_fanout.py --web <handout>` emits one brief per
family, each carrying that class's own `first_probe`, `falsifier`, `skill`,
`blast_radius` and `evidence_level` read from `knowledge/bug-classes.json`, the
`file:line` of every `source_signals` pattern that actually fired, and the layers
a kill map already closed. It short-circuits when a chain card is a strong match:
a known answer beats ten parallel guesses. The method is
`skills/web-parallel-sweep/SKILL.md`.

| Web agent | Classes | Note |
|---|---|---|
| `ctf-web-recon` | the endpoint and artifact inventory | GET only, the supplied port only; run it before the others, they probe against its inventory |
| `ctf-web-bundle` | source map and bundle recovery | when the bundle is the only source this IS the source read; a map is attacker-controlled data |
| `ctf-web-injection` | sqli · nosqli · command-injection · ssti · graphql | decides WHICH interpreter, not whether a bug exists |
| `ctf-web-objects` | prototype-pollution · deserialization · logic-flaw | the body's SHAPE is the attack; pollution is this tree's most-verified web class |
| `ctf-web-fetch` | ssrf · open-redirect · request-smuggling | records the FINAL url reached, not the one sent |
| `ctf-web-files` | file-read-primitives · file-upload · xxe | normalise the primitive from source before looping a wordlist |
| `ctf-web-session` | auth-session · oauth-sso · idor | name the token's format before any forgery |
| `ctf-web-parser` | parser-differential · cache-poisoning | the same bytes down two paths; never poisons a key another player will request |
| `ctf-web-client` | xss · csrf · cors · xs-leaks | asks WHO renders the payload first, and stops if the answer is nobody |
| `ctf-web-race` | race-condition · logic-flaw (TOCTOU) | the one write-shaped family: it proposes, the main thread executes with `--write-ack` |

The sweep itself is `skills/parallel-layer-sweep/SKILL.md`, and the contract every
report must satisfy is `python3 tools/subagent_fanout.py --contract`.

## 4. Skills — pull exactly one, and screen it before trusting it

- Open **one** skill, the one `skill_select.py` or the router names, and read it
  once.
- **Verified vs catalogue:** a `verified` skill has a chain card proving the class
  was solved here; a `catalogue` skill is published knowledge that nothing here
  has solved. Never say "this technique worked here" about a catalogue skill.
- **Run `python3 tools/skill_audit.py --apply` when a skill reads as generic.**
  The audit reports structural quality and local evidence separately. A `pass`
  skill with `local_evidence: stub` is structurally usable but has no local solve
  history; do not present it as verified experience.
- The best skill is usually a **chain card plus confirmed field notes**, because
  that is real experience from this machine.

---

## 5. Closing the learning loop — required after every flag

1. `hooks.py pre-flag <challenge> --value <flag> --source live-response --evidence '<excerpt>'`
2. `python3 tools/decide.py <challenge>` → must return `record_solve`
3. Write the chain card `knowledge/chains/<id>.json` → `tools/validate_card.py`
4. `python3 tools/classify_solve.py --chain <id>` — seeds a field note into the
   right bug-class skill, as `proposed`, awaiting review
5. `python3 tools/classify_solve.py --review` — the operator reviews:
   `--confirm <class> <anchor>`
5b. **`python3 tools/agent_prompt_forge.py --from-solve <chain-id>`** — push the new
   card's traps, first probe and blast radius into the prompt of every subagent that
   owns its class. This is the step that makes the fleet better after a solve instead
   of only the knowledge base: without it a card's `known_traps` never reach the agent
   that meets the same trap next. Measured before it existed: 70 cards carried 403
   traps between them and not one sentence appeared in any subagent prompt.
6. `bash test/run_all.sh` — the gate must PASS before this counts as done

Use `python3 tools/learning_report.py` during review to see the queue. Confirmed
notes must be promoted only after checking the chain card and exact evidence; the
tool never auto-confirms them.

Filing rule: a note belongs to the class whose **first probe opens the chain**,
not the class of the final payload. When the evidence does not decide between
classes, the tool refuses to file — that is correct behaviour, so do not force it.

---

## 6. Known traps inside this system itself

| Do not | Because |
|---|---|
| Confirm a class without `pre-confirm` | `decide.py` reopens it on the next round; the confirm means nothing |
| Hand-write a flag into state.json | the flag gate does not recognise a source outside hooks |
| Run a sixth probe in the same class "to be sure" | decide still returns `switch_class`; a syntax variant produces no new signal |
| `--verdict confirms` with "timeout" as evidence | the hook refuses; a timeout is evidence about availability, not about a bug |
| Trust a catalogue skill as local experience | nothing here has solved that class; record the real result in field notes |
| Hand-edit bug-classes.json to raise catalogue → verified | the label rises only through a chain card and classify_solve, never by editing |
| Ignore the audit's `field-notes stub` flag | that is the backlog: classes with no local experience, stated plainly instead of pretended |
| Forget to clean up probe or test objects on a shared instance | a write probe that passed `--write-ack` still has to be cleaned up afterwards |

---

## 7. Rules

- Touch only **authorised** targets: jeopardy CTF, labs, attack-defense.
- If the event forbids AI assistance, this system is for practice **before** the
  contest.
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
- Never commit a real flag, a credential, or state holding sensitive evidence.
- Any change to the system: `bash test/run_all.sh` must PASS before it counts as
  done.
