---
name: extending-argus
description: Add a vulnerability class, a probe ladder, a CVE exploit script, an MCP tool or a model profile to argus. Use when a new class or CVE needs supporting, when a tool should be exposed to the agents, or when a model needs tuning.
---

# Extending argus

Four extension points. Three of them are data files, and the fourth is one
decorated function.

## 1. A new vulnerability class

`argus/ledger/proof.py`. A class is a `ProofSpec`, and the only hard question is
**what observation could not have happened if the vulnerability were absent**.

```python
_spec("prototype-pollution", "browser_execution", "medium",
      "a polluted property observably changing behaviour in a browser or a server response",
      ("a real browser executed it",), verify_browser_execution,
      aliases=("proto-pollution",)),
```

- reuse a verifier if the evidence shape matches one (`command_output`,
  `data_extraction`, `file_read`, `oob`, `differential`, `browser_execution`,
  `template_eval`, `state_change`, `token_forgery`, `secret_leak`)
- write a new verifier only when the shape is genuinely new; it takes
  `(records, spec)` and returns a list of `_check(name, ok, detail)`
- `required_checks` must name the checks that make it a proof, including the
  **control** for any differential class
- if the class cannot be proven honestly, register it with `verify_refused` and a
  reason, the way `dos` is

Then add it to `test/cases/proof_cases.json` with one evidence set that must
grade `proven` and one that must not. The gate runs them.

## 2. A probe ladder

`argus/knowledge/playbook.json`. Cheapest discriminating step first, the proof
step last, marked with `proves`. Every step names a real tool and says *why* it
exists — the `why` is what the model reads, and a step without one is a step that
gets skipped or misused.

## 3. A CVE or technique script

```
scripts/exploits/<id>/
    meta.json     what it proves, the tier it needs, its arguments
    run.py        reads one JSON argument, prints one JSON object
```

`meta.json`:

```json
{"id": "cve-2026-9999-widgets-deser",
 "cve": "CVE-2026-9999",
 "vuln_class": "deserialization",
 "tier": "intrusive",
 "summary": "one line",
 "preconditions": ["version 3.4.0-3.4.2", "the import module is enabled"],
 "proves": "command_output",
 "entry": "run.py",
 "args": {"cookie": "string, optional"}}
```

`run.py` prints a single JSON object on its last line:

```json
{"ok": true,
 "summary": "the nonce came back in the import response",
 "next": "record the finding",
 "evidence": {"nonce": "<the nonce it was given>",
              "command": ["id; echo <nonce>"],
              "stdout_span": "<verbatim, bounded>",
              "response": {"status": 200, "body_span": "..."}}}
```

The evidence is graded by the same matrix as everything else, so use the field
names the verifiers read. The script runs with `python3 -I`, so it cannot import
from the directory it sits in — pass everything it needs as arguments.

**The script must stay benign.** It demonstrates; it does not persist, exfiltrate
or escalate. A script that writes must say so in `meta.json`, needs the intrusive
tier, and must record its own cleanup.

Register it in `scripts/exploits/registry.json`, then
`exploit.list_scripts` shows it and `exploit.run_script` runs it. No code in the
package changes.

## 4. An MCP tool

A module under `argus/broker/servers/` with a `SERVER = Server(...)` and one
decorated function:

```python
@SERVER.tool(
    "web.cors_probe",
    "One sentence of what it measures, then what the result means.",
    {"properties": {"target": {"type": "string"}}, "required": ["target"]},
    tier=config.TIER_ACTIVE, step="cors-probe", proves=None,
)
def cors_probe(context, target):
    ...
    return {"summary": ..., "result": "signal"|"no-signal",
            "data": {...}, "output": "...", "evidence": {...},
            "next": "what to do with this"}
```

The framework wraps it: scope check, tier check, hypothesis check, budget check,
evidence recording, redaction, bounded observation. Add the module name to
`SERVER_NAMES` in `argus/broker/servers/__init__.py`.

Three things a tool author owes the model:

- **`summary` first.** A model reads the first lines of a tool result far more
  reliably than the last.
- **`next`.** What this result means for the decision, including when it means
  "stop, this class is dead".
- **honest `result`.** `signal` when something discriminating happened,
  `no-signal` when nothing did. The controller reads it.

## 5. A model profile

`argus/runtime/profiles/models.json`. The fields that matter are not the name but
the loop shape: `max_steps`, `observation_cap`, `history_chars`,
`restate_contract_every`, `one_tool_per_step`, `tool_dialect`, and the cost. A
model missing from the file still runs, on the defaults — add an entry when you
have measured that the defaults are wrong for it.

`strengths` and `roles` are routing hypotheses. Measure them before trusting
them, and when a measurement contradicts the file, change the file.
