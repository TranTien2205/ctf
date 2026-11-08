---
name: web-parallel-sweep
description: >
  Run a web challenge as ten bounded measurements at once instead of one
  hypothesis at a time. Split the target by bug-class FAMILY with
  subagent_fanout --web, spawn one ctf-web-* subagent per family, and merge the
  returned measurements through a validator that refuses any report claiming more
  than it measured. Use it on a web target once recon exists and no chain card is
  a strong match; skip it when a card matches, and never let it become ten
  parallel guesses.
tags: [process, method, subagents, fan-out, web, falsifier, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "a report arrives whose evidence is not a verbatim response excerpt"
    - "two sweeps produce no family whose falsifier broke"
    - "the only remaining measurement is write-shaped"
evidence_level: catalogue
---
# Web parallel sweep — Process Skill

**Catalogue method.** No chain card proves it. What grounds it is a measured
result from this repository: a real contest where 2 of 3 web challenges were
solved but **much slower than other teams**, and a 464-point challenge
(`CSCV2026/diemthi`) where eleven mechanism layers were each closed by a cheap
read-only measurement, **one after another**, and the challenge was lost on the
clock rather than on the technique. Ten independent measurements run serially is
the time sink. Treat what follows as a procedure, not as experience of a solve.

Distinct from [[parallel-layer-sweep]], which splits a handout into
`novel_plan.py`'s generic layers. This one splits by **bug-class family**,
because that is what the ten `ctf-web-*` subagents are specialised on and what
decides which probe each one sends first.

## When not to use it

- **`chain_match.py` returns a candidate.** `--web` prints
  `strong_chain_match` and tells you to run that card's own
  `first_confirming_probe` instead. A known answer beats ten parallel guesses,
  and the card carries the traps that cost time the first time.
- The target is one endpoint with one sink. There is nothing to fan out.
- No recon exists yet. Run `ctf-web-recon` and `ctf-web-bundle` first — every
  other family probes against the endpoint inventory those two produce.

## First probe

Do not send a payload. Split the target, and look at what is already closed:

```bash
python3 tools/subagent_fanout.py --web <handout> \
        --challenge <name> --target <base-url>
```

Every field in the output is read from `knowledge/bug-classes.json` — each
class's own `first_probe`, `falsifier`, `skill`, `blast_radius` and
`evidence_level` — plus the `file:line` of each `source_signals` pattern that
actually fired in the handout, and `already_measured_dead_elsewhere` drawn from
every kill map in `knowledge/attempts/`.

The first probe is the answer to one question:

> **Which families does the handout actually point at, and which has this
> repository already measured dead?**

A family whose `source_signals_that_fired` is empty is the cheapest to **park**,
not the cheapest to run: nothing in the source points at it. A family a previous
attempt closed does not get a subagent at all — read its `measurement` and its
`reopen_if` and spend the budget on a family nobody has touched.

## The ten families

| Family | Subagent | Classes it owns |
|---|---|---|
| recon | `ctf-web-recon` | the endpoint and artifact inventory everything else probes against |
| bundle | `ctf-web-bundle` | when the front-end bundle is the only source, this IS the source read |
| injection | `ctf-web-injection` | sqli · nosqli · command-injection · ssti · graphql |
| objects | `ctf-web-objects` | prototype-pollution · deserialization · logic-flaw |
| fetch | `ctf-web-fetch` | ssrf · open-redirect · request-smuggling |
| files | `ctf-web-files` | file-read-primitives · file-upload · xxe |
| session | `ctf-web-session` | auth-session · oauth-sso · idor |
| parser | `ctf-web-parser` | parser-differential · cache-poisoning |
| client | `ctf-web-client` | xss · csrf · cors · xs-leaks |
| race | `ctf-web-race` | race-condition · logic-flaw (TOCTOU) |

That is 24 of the 25 web classes in the taxonomy. `web-web3` has no family;
route it by hand to `skills/web-web3/SKILL.md`, which is **catalogue**.

The grouping is by **probe**, not by name: two classes share a family when one
probe distinguishes them. `web-sqli` and `web-nosqli` share one because a single
probe decides whether the value stayed a string or became an object.
`web-ssrf` and `web-xss` do not, because nothing one of them sends tells you
anything about the other.

## The sweep

Spawn the read-only families **in parallel** — they cannot interfere, none of
them writes to the target or to this repository, and none has a `Write` tool.
Each returns the contract JSON from `python3 tools/subagent_fanout.py --contract`.

`race` is the exception and the only write-shaped family: it **proposes** the
interleaving run and the main thread executes it, after reading the chain card's
`blast_radius` and passing `--write-ack`, and whoever runs it cleans up the probe
objects afterwards.

Then validate before believing any of it:

```bash
python3 tools/subagent_fanout.py --validate report.json
python3 tools/subagent_fanout.py --merge reports/*.json --challenge <name>
```

`--merge` prints the `tools/hooks.py post-probe` commands for **you** to run. It
never writes `state.json`, and neither can the subagents.

## The failures this method has, and the guard for each

**A subagent summarising instead of quoting.** "The template evaluated
arithmetic" is hypothesizer output; the evidence is the literal `803701` in the
response. `--validate` refuses a report whose `evidence` is not a verbatim
substring of its own `response_excerpt`. Measured on eight adversarial reports:
six refused with the exact reason, two honest ones accepted — including a
negative.

**Parallel subagents racing the ledger.** Ten of them calling
`tools/hooks.py post-probe` would write one `state.json` at once and spend the
per-class probe budget in parallel, destroying the one rule `tools/decide.py`
exists to enforce. So no `ctf-web-*` agent has a `Write` tool and every one is
told not to run the hooks. You merge; they measure.

**Breadth reading as coverage.** Ten families reporting is not ten families
closed. A family that returned `not-measured` was never closed, and a family
whose `source_signals_that_fired` was empty was never pointed at. Say both
plainly, and write every family whose falsifier **held** into
`knowledge/attempts/<challenge>.json` with its measurement — or the next attempt
walks it again, which is the failure this skill exists to prevent.

## The web speed primitives each family reaches for

`python3 tools/web/selftest.py` and each tool's own `--selftest` prove these
offline before you trust one:

| Instead of | Run |
|---|---|
| twenty hand-written requests to find which shape the input reacts to | `variant_matrix.py` — one request per payload shape at one injection point, baseline-diffed and ranked, with every negative counted |
| a hand-rolled thread pool for a race | `race_probe.py` — overlapping requests with a **serial baseline first**, because a signature that also appears serially is not a race |
| re-deriving endpoints from minified JavaScript | `bundle_miner.py` — source-map recovery and an endpoint inventory; a map is attacker-controlled data, so a traversal in `sources` is rejected and counted |
| twenty minutes working out what the cookie is | `session_dissect.py` — name the format, then the one weakness that applies. Analysis only; it never forges and never sends |
| forty encodings of a blocked byte | `sanitizer_fuzz.py` — differential sweep that records how many cases proved a negative |
| a loop over a proven file-read | `read_loop.py` |
| an id-enumeration loop | `id_sweep.py` |

## Roles

Every `ctf-web-*` agent is a `reader` and a `writer` in the `AGENTS.md` sense.
None is the machine that verifies. The agent proposes; `tools/hooks.py` and
`tools/decide.py` decide.
