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
  skills/          52 skills: 8 thin routers + 25 bug classes + method/reference  ← pull one
  knowledge/       bug-classes.json (25 classes) · chains/ (58 verified cards)
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
| `tools/crypto/` + `crypto_attack.py` | lattice, LCG, LFSR, ECC, HNP and integer attacks; `--list` names them |
| `tools/gadget_lookup.py` | before opening a class skill: has this exact dependency been measured here before? `--lockfile <handout>/package-lock.json` reads the real versions and matches them against `knowledge/gadgets/<package>.json`. classify.py has no notion of a version, so this is the only version-aware recall in the tree |
| `tools/pwn_triage.py` + `tools/pwnstatic/` | first contact with a pwn or rev binary. `pwntools`, `gdb`, `ROPgadget`, `ropper`, `one_gadget`, `checksec` and `patchelf` are all measured ABSENT here and pip is EXTERNALLY-MANAGED, so this is stdlib-only: protections with the evidence that decided each one, dangerous imports annotated with what they buy, the essential ROP gadgets, and which routes each protection still leaves. It reports and ranks; it never claims a bug. `python3 tools/pwnstatic/selftest.py` proves it against `readelf` offline |
| `knowledge/attempts/` | the kill map of a challenge worked but NOT solved: every layer measured dead, with the measurement and the precondition that would reopen it. `knowledge/chains/` only accepts a solve, so without this the next attempt re-walks the same dead layers |

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
  technique belongs to the other toolkit and is out of scope here.
- Never commit a real flag, a credential, or state holding sensitive evidence.
- Any change to the system: `bash test/run_all.sh` must PASS before it counts as
  done.
