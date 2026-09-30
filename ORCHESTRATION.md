# ORCHESTRATION.md — how to make subagents carry the hours

You are the conductor. Subagents do not solve the challenge; they absorb the part
of it that is not the solve. This file is the method, and every number in it was
measured in this repository.

There is **no time target here**. A challenge takes what it takes. The question is
what fraction of it can happen at the same time as everything else, and the whole
method is about making that fraction bigger.

---

## 1. The model: a short serial spine, and a large parallel mass

Decompose any challenge into two parts.

**The spine** is the chain that actually reaches the flag. Each step depends on the
answer to the one before, so nothing can compress it — and it is almost always
short. Measured on Speednet: once the GraphQL schema was on screen, the whole
chain (IDOR → a dev mutation → password reset → 2FA → alias batch) took minutes.

**The mass** is everything else: proving that fifteen other things are *not* the
answer, reading source, mining a bundle, researching a library, building a tool.
None of it depends on the rest. This is where the hours go.

The decomposition is not a metaphor. `knowledge/attempts/htb-prying-eyes.json`
records a full session:

| | |
|---|---|
| layers closed | **17** |
| needed a prior layer's answer | **2** |
| **independent of every other layer** | **15** |

Fifteen independent measurements, walked one at a time. That session's spine was
two layers and a login gate; the other fifteen were a mass I serialised by hand
for no reason other than that I was the only one measuring.

**So the speedup is not a constant, it is a ratio.** A challenge that is mostly
spine barely moves. A challenge that is mostly mass — which is what a hard one
looks like — moves by roughly the number of agents you keep busy. Three to four
hours becomes one to two when five or six agents are working while you drive the
spine, and it stays three to four when they sit idle waiting to be told something.

---

## 2. One agent costs 7–10 minutes. That is a floor, not a budget

| agent | wall | tools | tokens | what it produced |
|---|---|---|---|---|
| `ctf-web-recon` | 9.7 min | 38 | 105k | full inventory, and three broken commands in its own definition |
| `ctf-web-recon` | 10.2 min | 22 | 95k | full inventory, the auth gate, and two bugs in the shared HTTP layer |
| `ctf-writeup-scout` | 7.3 min | 17 | 67k | one primary source, and an honest refusal on the rest |
| `ctf-web-session` | 10.2 min | 16 | 95k | a 1165-line tool, 27 selftests, 6 mutation proofs |

Spawn-to-report is 7–10 minutes whatever the task. Read that as a **granularity
floor**: never hand an agent something you could finish in five minutes, because
the round trip costs more than the work. It is **not** a ceiling on how many you
may run. A four-hour challenge has room for many waves; a twenty-minute one has
room for one, launched at the start.

The only rule the number really imposes: **never spawn and then wait.** If you are
idle while an agent runs, you have converted parallel time back into serial time.

---

## 3. The actual skill: converting spine into mass

Anyone can run agents on work that is already obviously parallel. The lever that
moves a four-hour challenge is noticing that work you are about to do **serially**
does not have to be.

Four conversions, each one taken from something I did the slow way:

**Ask every question at once, not in the order they occurred to you.** On Prying
Eyes I asked "is it the alpha channel?", then "is it the filename?", then "is it
the declared content type?" — one after another, each a full round trip. All three
were independent. That was one wave pretending to be three hours.

**Speculate ahead of the spine.** While you drive the current step, put agents on
the layers you will reach *if this one dies*. When it dies — and most do — the
next answer is already sitting in the workspace. The cost of a wrong speculation is
one agent; the cost of not speculating is the whole round trip, every time.

**Build tools beside the probe, not before it.** `gqlkit.py` — 1165 lines, 27
selftests — was written by an agent in ten minutes while other work continued. I
had hand-written a throwaway version of the same thing mid-solve, which is ten
minutes of the spine spent on something that was never on the critical path.

**Send research out the moment the name is known.** A writeup or a library
question has a 7–10 minute latency whether you start it at minute 5 or minute 50.
Start it at minute 5, and keep probing while it runs.

The test for whether you are orchestrating or just delegating: **at any moment,
is anything running that you are not doing yourself?** If not, you are the
bottleneck.

## 3b. Re-check for a handout on every fold, not only at OPEN

Measured on Desire, 2026-09-30, to the second:

| | |
|---|---|
| challenge opened, black-box | 06:20:28Z |
| the handout appeared on disk at `challenges/Desire/` | 06:35:28Z |
| I was told it existed | ~06:37Z |
| source read -> working exploit -> flag | **06:39:31Z** |

Eighteen minutes of black-box work were unavoidable: the handout did not exist
yet. The next twelve were not — it sat on disk while four agents and I kept
reconstructing a 236-line Go file from HTTP responses. **A handout can arrive
after OPEN.** So `ls challenges/<name>*` is part of every FOLD, not just Wave 0,
and it costs one command.

The bill for guessing what a source read would have told us, on this one
challenge: nineteen distinct measurements, of which **three** were on the spine —
"which cookie is the identity", the source read, and the four-step exploit. The
other sixteen were black-box substitutes for one file. Breadth is the right
answer when there is no source. It is the expensive answer when there is.

## 3c. A negative about an input is only as good as the write path you also read

The single most instructive failure of that session. A `ctf-web-files` agent
measured the `username` cookie exhaustively and correctly:

- `/register` rejects `/`, `.` and `\` — four shapes, all `400 Invalid Username`
- every dot-segment cookie answers `500`
- eight injection shapes answer `500`

and concluded: *the cookie must name an existing database row.* Every
measurement true, the conclusion wrong. The cookie had to name an existing
**redis key**, and the login handler hands out redis keys *before* it checks the
password — so any string at all could be minted. The cookie was the answer.

An input that fails every probe is not closed until you have also read **who
fills the map it is looked up in**. Write that into the brief: *if this input is
dereferenced against a store, name the code that writes that store before you
report it dead.*

And the mirror image, from my own work on the same challenge: I confirmed Zip
Slip off an asymmetry (`../x` returns 202 while `x` collides) and was wrong —
`mholt/archiver` *silently skips* an escaping entry, so 202 meant "discarded".
What broke it was a **control on something I knew existed**: upload the same
escaping entry twice, and upload a path that certainly exists. Neither collided.
A positive control is one request, and it is the difference between a primitive
and a fiction.

## 4. The wave structure

### Wave 0 — recall, before anything (1 agent, or skip)

```bash
python3 tools/chain_match.py --source <handout> --record <name>
python3 tools/classify.py --source <handout> --record <name>
```

Run these **yourself**; they take seconds. Spawn `ctf-killmap-scout` only when
there is a handout big enough that you would otherwise read it for ten minutes.

If `chain_match` returns `status: candidate`, **stop orchestrating**. Run that
card's `first_confirming_probe`. A known answer beats any number of parallel
guesses, and `subagent_fanout --web` will tell you so in `strong_chain_match`.

### Wave 1 — breadth, immediately

```bash
python3 tools/workspace.py <challenge>
python3 tools/subagent_fanout.py --web <handout> \
        --challenge <name> --target <url> --write-budget 5
```

Read `source_signals_that_fired` on every brief before launching anything:

- **empty** → that family is the cheapest to **park**, not to run. Nothing in the
  source points at it.
- **`already_measured_dead_elsewhere` non-empty** → do not spawn. Read the prior
  measurement and spend the slot elsewhere.

Then launch the surviving families **in one message so they run concurrently**.
Three to six is the useful range; ten is a sweep, not a wave.

**While they run, you drive the spine yourself**: entry page, bundle, schema, the
first discriminating probe.

### Every wave after: keep the pipe full

This is the part that decides whether a four-hour challenge becomes two.

**The moment a wave lands, launch the next one.** Do not read all the reports,
decide, and then think about what to delegate — by then the agents have been idle
for as long as it took you to read. The order is: skim for anything that breaks a
falsifier, **launch**, then read properly.

What goes in a later wave:

- the layers the first wave named but could not close
- the branches you will need **if the current spine step dies** — speculation is
  cheap, and most steps die
- a tool you are about to hand-write (an agent writes it while you keep probing)
- a library or writeup question, the moment a name for it exists

**Stop launching when a wave comes back with nothing new twice running.** That is
not an agent problem, it is a shape problem: change mechanism layer rather than
spending another wave on the same idea. `tools/decide.py` will say `switch_class`
for the same reason.

## 5. What you never delegate

| Never | Because |
|---|---|
| `tools/hooks.py`, `tools/state.py` | `decide.py` enforces five probes per class and twenty-five per challenge. Ten agents recording probes spend that in one round and force a class switch on classes nobody worked. |
| The verdict | An agent's conclusion is `hypothesizer` output. Only a verbatim response excerpt through `post-probe` confirms anything. |
| What happens next | `decide.py` decides. An agent proposing the next step is proposing, not deciding. |
| The flag | `hooks.py pre-flag`, from a live response or a supplied artifact, and the excerpt is **pasted from the tool's output**, never typed. Measured: I typed one from memory and the gate accepted it because it only checks for emptiness. |
| A destructive write | A delete, a bulk update, or a write touching an object you did not create comes back to you whatever the brief's `write_budget` says. |

Agents **measure**. You **record, decide and verify**.

---

## 6. Writing a brief that comes back usable

Every good report this session came from a brief that did these five things:

1. **Hand over everything already measured**, in a file, and say *do not re-derive
   this*. `scratchpad/facts.md` did that for four agents at once.
2. **Ask ONE question.** "Which image library is this, exactly?" produced a ranked
   answer with doc citations. "Look into the image pipeline" would not have.
3. **Name the falsifier.** What result would mean the lead is dead? An agent with
   a falsifier returns a usable negative; one without returns prose.
4. **Say what it may not do**, with the reason. `write_budget`, the ledger rule,
   and *measure the rate limiter before raising throughput* — that last one is in
   every brief because ignoring it cost a stalled instance.
5. **Demand the shape back.** `python3 tools/subagent_fanout.py --contract`, then
   `--validate` each report before believing any of it.

Add one line that has earned its place: *"an unmarked guess from a specialist is
worse than no answer, because it will be believed."*

---

## 7. Failure modes measured here, and the guard for each

| Failure | Measured | Guard |
|---|---|---|
| Agents die mid-flight | four parallel agents lost to `EAI_AGAIN`; three workflow agents lost to `ECONNREFUSED` | treat a dead agent as **no result**, never as a negative. Re-read the brief's question and decide whether to re-spawn or do it yourself. |
| Agents collide in scratch | two agents chose `scratchpad/mut`; one `rmtree` destroyed the other's staged work | `tools/workspace.py <challenge> --agent <name>` gives each a private directory; `--web` puts it in the brief. |
| Absolute claims | "the only home of `verified_by`", "no `evidence_level` exists for it anywhere" — both false; 18 such overstatements needed fixing | re-measure every load-bearing sentence before acting. A narrow true claim inflated into a false absolute is the characteristic agent failure. |
| A summary of an unread page | two AI summaries of one blocked page contradicted each other — one said file read, the other file write | a summary is not a source. Require the URL **and** the HTTP status; `nothing_found_for` is a valid answer. |
| A selftest that cannot fail | four tools shipped green selftests that survived deleting the behaviour they claimed to test | make the agent break its own tool on a copy and prove the check catches it. |
| A negative that is really an unread write path | an agent closed the `username` cookie on 12 correct probes; the value only needed a redis key a pre-auth code path minted | ask in the brief WHO writes the store an input is looked up against, before accepting "this input is dead". |
| A confirm built on an asymmetry | `../x` -> 202 while `x` -> collision read as "traversal works"; the extractor was silently discarding the entry | run a positive control on something you know exists, and repeat the probe -- a landed write must collide the second time. |
| Breadth read as coverage | ten families reporting is not ten families closed | a family that returned `not-measured` was never closed; one whose signals were empty was never pointed at. Say both. |

---

## 8. Verification runs both ways

This is not oversight theatre. In this session:

- Agents found **two real bugs in my own shared code** — `httpkit` collapsing
  repeated `Set-Cookie` headers, and `http_probe` not emitting the fix — plus a
  wrong claim I had made about a target.
- I found **18 factual overstatements** in what agents wrote, and had to stop a
  brute force I launched myself that stalled the instance.

So: re-measure their load-bearing claims, and let them audit yours. The cheapest
high-value agent all session was the one whose only job was to attack my own work.

---

## 9. The drill

Phases, not a clock. Each one ends when its condition is met, and the pipe stays
full throughout.

```
OPEN     workspace + fanout --web. Read source_signals_that_fired and the kill-map
         hints. Launch Wave 1 (3-6 families) in ONE message, with a facts file and
         a write_budget. Nothing is delegated that you could finish in five minutes.

DRIVE    You work the spine while they run: entry page, bundle_miner, schema or
         source read, first discriminating probe. You are never idle.

FOLD     A wave lands -> skim for a broken falsifier -> LAUNCH THE NEXT WAVE ->
         then read properly. --validate each report, --merge them, record through
         hooks.py. Park the families whose falsifier held.

REPEAT   DRIVE and FOLD alternate. Each fold seeds the next wave from: layers left
         open, branches for when the current step dies, a tool you were about to
         write by hand, a question that now has a name.

CLOSE    Flag -> hooks.py pre-flag with an excerpt PASTED from the tool's output.
         No flag -> knowledge/attempts/<id>.json with every dead layer and the
         precondition that would reopen it, so the next attempt starts where this
         one stopped instead of where it started.
```

Two stopping conditions, and neither is a clock:

- **Two consecutive folds with nothing new** → the shape is wrong. Change mechanism
  layer; do not spend another wave on the same idea.
- **`tools/decide.py` says `switch_class` or `stop_report`** → it is counting
  probes and minutes per class precisely so that you do not have to, and it is not
  fooled by relabelling the class.

## 10. After the solve

```bash
python3 tools/agent_prompt_forge.py --from-solve <chain-id>
```

The card's traps, first probe and blast radius go into the prompt of every agent
that owns its class. Without this the fleet learns nothing from a solve — measured
before it existed: 70 cards carried 403 traps and not one sentence reached any
subagent prompt.

A challenge worked and **not** solved is worth the same step in reverse: write
`knowledge/attempts/<id>.json` with every layer measured dead and the precondition
that would reopen it, or the next attempt walks all seventeen again.
