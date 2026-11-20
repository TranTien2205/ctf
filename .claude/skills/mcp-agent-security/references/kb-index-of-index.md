# Index of indexes

The corpus grew to several hundred modules; this file is the high-level map
so a task can name the family without reading every entry.

## Families

| Prefix | Content |
|---|---|
| `work-*` | Reading order, evidence rules, the corpus's frame |
| `meth-*` | Offensive and audit methods (tool map, injection shapes, exfil, audit shape, protocol internals, schema abuse, confused deputy) |
| `inj-*` | Injection vector families (system extract, persona, encoding, split, translate, summarize, completion, few-shot, negation, overflow, format, tag-spoof, unicode) |
| `exf-*` | Exfil channel families (tool-arg, URL param, image render, DNS, answer text, file write, tool chain, side channel) |
| `perm-*` | Permission audit rows (inventory, fs, net, shell, cred, auto-exec, untrusted input, narrow-vs-broad, default-deny) |
| `mcp-*` | Protocol internals (JSON-RPC, tools/list, tools/call, resources, prompts, sampling, roots, notifications, auth, server trust) |
| `tool-*` | Adapter inventory (browser, proxy, shell, OOB, docs, code-index) and the audit output shape |
| `scen-*` | Challenge scenarios (flag-in-prompt, behind-tool, file-via-agent, exfil-via-fetch, indirect-doc, audit, tool-enum) |
| `def-*` | Defensive audit modules (provenance, perm-gap, injection surface, auto-exec, supply, schema truth, secrets, logging) |
| `wf-*` | Workflow modules (offensive loop, map-first, injection order, exfil choice, evidence, audit loop, field notes) |
| `ev-*` | Evidence shapes (tool result, verifier, model-assertion-never, callback, file bytes, state change) |
| `kb-*` | Knowledge bank (confused deputy, lethal trifecta, tool poisoning, rug pull, sampling abuse, shadowing, context integrity, multi-agent, etc.) |
| `tx-*` | Tool-type x risk matrix cells |
| `vx-*` | Injection-vector x channel matrix cells |
| `fx-*` | Flag-location x reach-method matrix cells |
| `*-route` | Route companions - one per module, naming when to open it |

## The base files

`prompt-injection-testing.md`, `tool-permission-audit.md`,
`adapter-selection.md` - the three hand-written references the corpus
surrounds. The corpus is detail; the three files are the spine.
