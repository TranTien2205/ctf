---
name: white-box-intended-path
description: >
  Find the one vulnerability the author actually wrote. Use on a high-value,
  low-solve white-box challenge, and the moment a session has spent more than
  one mechanism budget without reaching impact. Diff the handout against a stock
  app, put every author-deliberate oddity in an anomaly map, and refuse to
  commit to a chain until its cheapest reachability falsifier has been run.
tags: [white-box, process, method, anomaly-map, falsifier, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "an anomaly is still unexplained after the current chain is fully built"
    - "a chain is about to be worked before its reachability falsifier has been run"
    - "two mechanism budgets spent with no anomaly newly explained"
evidence_level: catalogue
---
# White-box intended path — Process Skill

**Catalogue method.** No chain card proves this method; it is the retrospective
of a session in this repository that was **lost** — `CSCV2026/diemthi/`, CSCV
2026, 464 points. Every oddity below was noticed on day one and none was ever
written into an "explained by" table, so two by-design-dead chains were driven
for a whole session. Treat what follows as a procedure to run, not as local
experience of a solve.

A high-scoring, low-solve challenge has **one authored vulnerability**. The
author had to add code to create it, and usually had to add more code to stop
the cheap unintended paths. Both kinds of addition are visible in the diff.

## First probe

Do not send a request. Get the stock app of the same type — `npm pack` the
framework's generator output, `pip download` the library, `docker pull` the
upstream image, or clone the upstream repository at the pinned version — and
diff the handout against it. The first probe is the answer to one question:

> **What did the author ADD, REMOVE or GUARD that upstream does not have?**

**Falsifier** — the observation that closes this method: the diff against stock
is empty apart from branding and configuration, i.e. the challenge is an
unmodified application and the bug is in a dependency, not in the handout. Then
leave this skill and open `../white-box-dependency-measurement/`.

## The anomaly map

Two columns. Left: every author-deliberate oddity. Right: the hypothesis that
**explains why the author wrote it**. An oddity with an empty right-hand cell is
the loudest signal in the challenge.

What counts as an author-deliberate oddity:

| Shape | Why it is deliberate |
|---|---|
| A bespoke sanitizer, hand-rolled next to a library that already does the job | the author needed a specific gap, or needed to close a specific hole |
| A narrow whitelist that permits exactly **one** odd input shape | that shape is either the intended route or the decoy for it |
| An explicit block on the **sibling** of a permitted shape | the author tested the sibling and it worked |
| One literal word filtered out of every string | the word names the thing the intended path must not reach directly |
| An unusual raw-output sink (triple-stash, `|safe`, `innerHTML`, `dangerouslySetInnerHTML`) in a file unrelated to the feature under test | a sink nobody asked for is a sink somebody planted |
| A leftover test record, fixture row, scratch file or commented payload | the author's own scratch work; may be a hint or may be stale |
| A code comment that explains a *defence* | the author is telling you which route is closed by design |
| A pinned or downgraded dependency version | the intended bug lives in that exact version |
| A setuid helper, an extra container, an internal-only network | the flag's real location, and the trust boundary that must be crossed |

**The rule: an unexplained anomaly means the intended path is elsewhere — stop
digging where you are.** A chain that explains none of the anomalies is almost
certainly not the authored one, however elegant it is.

Record the map with the companion tool so it cannot be kept in your head:

```bash
python3 tools/anomaly_map.py <challenge> --add-anomaly "..." --where <file:line> --kind whitelist
python3 tools/anomaly_map.py <challenge> --explain <anomaly-id> --hypothesis "..."
python3 tools/anomaly_map.py <challenge> --show
```

## Worked example — what a filled map would have said

From `CSCV2026/diemthi/` (Express + handlebars → jsreport 2.9.0 → an
internal-storage service holding the prize). Five anomalies, all noticed, none
ever explained:

| Anomaly (verbatim, on disk) | Explained by? |
|---|---|
| `server/index.js:137` `isDataReference()` accepts a `data.name` object **only** when its single key is `$ref` | never filled |
| `server/index.js:143` `containsArrayReferenceEnvelope()` rejects `$values` **anywhere** in the tree | never filled |
| `server/sanitize.js:13` `removeBlockedWord()` deletes the literal `secret` from every string, iteratively | never filled |
| `server/mail.js:12` a `{{{name}}}` triple-stash in the **email body**, a file the export feature never uses | never filled |
| shipped `data/scores.db` carries the author's rows `999/Probe` and `walstage2/{{{childTemplate payload}}}` | never filled |
| `Dockerfile:14` `# Templates are sent inline with each render request — jsreport's store stays empty.` | never filled |

Read the left column alone and it is already a sentence: the author built a
reference-resolution feature for one field, closed its sibling envelope, made
sure the one secret's *name* can never be typed, planted a raw sink in an
unrelated file, and wrote a comment saying the store route is closed. Two of
those cells exist to stop something. Three exist to enable something. The
session instead spent itself on the two the comment and the config had already
closed.

The lesson is mechanical, not clever: **a five-row table that took ten minutes
would have redirected the session.** An anomaly you have only *noticed* is not
an anomaly you have *used*.

## Reachability falsifier — per candidate chain, before any time is committed

For every candidate chain, write down, before working it:

1. the **precondition** the chain cannot survive without;
2. the **cheapest observation** that would show that precondition is false;
3. the **cost** of that observation, in minutes.

Then run the cheapest observation **first**. This is the same discipline as
`../LOOP_DISCIPLINE.md`, one layer up: a falsifier kills a whole chain, not a
payload variant.

The two chains lost to skipping this, both killable in minutes:

| Chain | Precondition | Cheapest falsifier | Actually closed after |
|---|---|---|---|
| jsreport `{#child}` → prototype pollution → vm2 escape | the jsreport template store is non-empty on a stock deploy | `grep -n store Dockerfile` — line 14 says the store stays empty by design; plus one `GET /odata/templates` → `[]` | a full session, and a hand-populated local store had produced a false positive that had to be retracted on a pristine rebuild (`CSCV2026/diemthi/TICKET.md`, "Pristine re-measurement") |
| HTML injection → headless-Chromium `file://` read | some file the read primitive can name has a triple-stash in a **non-text** HTML context (attribute, URL, `<script>`) | one on-disk scan of the container — 4605 NUL-free files, **0** hits | a full session |

Both falsifiers were a single command. Neither was run until the chain had
already consumed its budget.

The tool refuses to let a chain be worked silently:

```bash
python3 tools/anomaly_map.py <challenge> --add-chain "<name>" --falsifier "<cheapest observation>" --cost 5
python3 tools/anomaly_map.py <challenge> --ran <chain-id> --result "<verbatim output>" --killed
```

`--show` prints every chain whose falsifier has not been run. That list is the
work you are not allowed to start yet.

## Blast radius

This skill sends nothing, so it has none of its own. Two second-order risks:

- A falsifier must be **read-only**. If the cheapest observation is a write, use
  the second-cheapest read instead, and read `blast_radius` on the matching
  chain card first (`tools/chain_match.py`).
- Anomalies are recorded from source you already have. Do not copy handout
  source into `knowledge/`; the map holds a one-line description plus
  `file:line`, nothing more.

## Route to depth

- The anomaly is a version pin, a vendored module, or an upstream behaviour you
  are about to reason about from documentation → `../white-box-dependency-measurement/`
- The diff against stock is empty → `../white-box-dependency-measurement/`
- The map is filled and one anomaly names a mechanism → `tools/classify.py --source <dir>`,
  then `tools/skill_select.py`, then exactly one bug-class skill
- An anomaly matches a shape solved here before → `tools/chain_match.py "<the anomaly>"`
  and run that card's `first_confirming_probe` before inventing one
- The map is filled, every anomaly is explained, and impact is still out of
  reach → `tools/decide.py <challenge>`; expect `switch_class` or `stop_report`,
  and report the map as the evidence of what was closed

## Discipline

- An anomaly with an empty "explained by" cell outranks any chain you are
  currently enjoying. Fill it or change layer.
- Never start a chain whose reachability falsifier has not been run.
- A negative falsifier result is a **recordable measurement**, not a failure.
  State it as a number ("0 of 4605 files"), see `../white-box-dependency-measurement/`.
- A leftover author record may be a stale scratch note, not a hint. Treat it as
  an anomaly to explain, and accept "the author abandoned this" as a valid
  explanation only after checking the version actually shipped.
- A comment that explains a defence is evidence about the author's intent, not
  about the code. Confirm it against the running system before trusting it.

## Field notes

`field-notes.md` in this directory grows every time this method decides a
session. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
