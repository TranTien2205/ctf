# Argus architecture

One file is the spec: `argus/loop.py` drives the loop; everything else is a
tool, a guard, or a store.

## The loop

```
seed (target + goal + auth context + scope description)
   │
   ▼
ClaudeClient.chat(messages, TOOL_SCHEMAS, system)   ← Anthropic tool_use API
   │
   ├─ text blocks   → logged to agent.log (reasoning trace)
   └─ tool_use      → dispatch(ctx, name, args)
                        │
                        ├─ ScopeGuard.check(url)     ← hard boundary
                        ├─ RateLimiter.wait()
                        ├─ GuardedClient.send()      ← the ONLY socket
                        └─ Session.record_exchange() ← evidence, r<n> id
                     result → tool_result → next turn
   │
   └─ finish(summary) or budget exhausted → report/markdown.py
```

Design choices and why:

- **Tool-calling, not free-text parsing.** Claude's `tool_use` gives typed,
  schema-validated calls; the loop never regexes commands out of prose.
- **One guarded client.** Every tool — `http_request`, `crawl`, probes,
  even `run_external` arg checking — funnels through `ScopeGuard` +
  `RateLimiter` + transcript recording. No tool opens its own socket.
- **Evidence gating at write time.** `Session.add_finding` asserts the
  excerpt is a substring of a cited response. Same idea as a flag gate,
  generalized: the machine validates the *truth* of a claim, not its shape.
- **Baseline-diffed probes.** Each `probe_*` returns `verdict` +
  `request_ids`, never "you are vulnerable". The agent confirms and
  rates severity itself.
- **Skills as retrievable knowledge.** 19 methodology modules (~2KB each)
  load on demand via `load_skill`. Detection signals, first probes,
  confirmation criteria, bypasses, honest severity guidance.
- **Budget-aware autonomy.** max_turns / max_requests / max_time are real
  limits; near the end the loop nudges once ("record and finish"), then
  stops. No human-in-the-loop inside scope by design.

## Trust boundaries

- The **model** can only act through tools; it cannot widen scope, spend
  past budgets, or write findings without verbatim evidence.
- The **transcript** is append-only JSONL; findings reference it by id.
- **Web content is untrusted data.** The system prompt teaches the model
  to treat in-page instructions as prompt-injection attempts and keep
  working the assessment.

## Extension points

- New probe: add a function in `tools/probes.py`, register in
  `tools/registry.py` (`_impl` + `_schema`). It must send via
  `ctx.client.send` — then scope, rate limit and evidence are free.
- New skill: drop `name.md` in `argus/skills/` + one row in `INDEX.md`.
- New report format: `argus/report/` takes `Session` + `Config`.
- Different model: `ClaudeClient` is ~40 lines of HTTP; `llm.ScriptedClient`
  shows the duck-typed interface (`chat(messages, tools, system)`).

## Team mode (`argus team`)

A second plane over the same primitives: a **lead** agent coordinates
role-specialized **workers** through a shared blackboard.

```
        ┌─────────── lead (AgentLoop, LEAD card) ───────────┐
        │  read_board · spawn_worker · emit_lead · finish    │
        └──────┬─────────────────────────────┬──────────────┘
               │ spawn (thread, own loop)     │ steer notes
        ┌──────▼───────┐             ┌────────▼────────┐
        │ recon worker │ emit_lead  │ exploit worker  │
        │ crawl/js/fuzz├───────────►│ pull→probe→proof│
        └──────────────┘  LEADQUEUE └────────┬────────┘
                                             │ record_finding
                                  ┌──────────▼──────────┐
                                  │ report worker       │
                                  │ findings → summary  │
                                  └─────────────────────┘
            ━━━ shared, code-enforced, never prompt-level ━━━
        ScopeGuard · RateLimiter · Session(transcript) · Board
```

- **Two LLM levels, deliberately.** Lead → workers is the deepest the org
  chart gets. A worker that needs help posts a `request_worker` to the
  board; the lead decides whether to spawn. Sub-division inside a worker
  is tool fan-out (crawl + js_recon + fuzz in parallel calls), not another
  LLM tier - each extra tier is another place to re-interpret intent.
- **Leads are typed artifacts, not chat.** `emit_lead` pushes a deduped,
  prioritized `Lead{kind,url,params,method,tech,source}`. The exploit
  worker never receives "the recon guy said maybe SQLi" - it receives the
  exact URL, params and the request_id it was seen at. Shared artifacts
  beat shared conversation: no context pollution, no hearsay findings.
- **Streaming pipeline.** `pull_leads` blocks while recon runs and returns
  `closed` only when the queue is closed AND drained - exploit starts on
  the first lead, not after recon finishes.
- **Role gating is dispatch-level.** Each card's `tools` set is enforced in
  `dispatch`, not just advertised to the model: a recon worker literally
  cannot call `record_finding`; only the lead's card carries
  `spawn_worker`/`finish_engagement`.
- **Shared guardrails.** One `ScopeGuard`, one `RateLimiter`, one
  `Session`. N workers can't N-fold the request rate; every exchange is
  tagged with its agent name in the transcript.
- **`run_exploit` runs manifests, not magic.** `resources/exploits/<id>/`
  holds `manifest.json` (command template, `affects`, `proof_marker`
  regex) + script. Target URL is scope-checked before substitution; a
  `proof=True` run id is citable as finding evidence.

## What it deliberately does not do

- No exploit payloads that persist (no webshells, no shells period).
- No authentication-agnostic scanning of foreign hosts — scope is explicit.
- `run_external` and `run_exploit` output is a lead, not evidence:
  scanner claims are verified through `http_request` (or a manifest's
  `proof_marker`) before `record_finding` accepts them.
