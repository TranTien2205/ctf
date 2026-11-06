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

## What it deliberately does not do

- No exploit payloads that persist (no webshells, no shells period).
- No authentication-agnostic scanning of foreign hosts — scope is explicit.
- No parallel agent fan-out inside a run; one loop, one target, one
  transcript keeps evidence clean. Parallelizing across targets is a
  wrapper-script concern.
- `run_external` is a lead generator, not evidence: scanner claims are
  verified through `http_request` before `record_finding` accepts them.
