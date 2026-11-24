# Domain: AI attack and defense — agent hijack scenarios

Reference module for `contest-domain-map`. The event's theme is an AI or
insider seizing a swarm of autonomous systems. The vocabulary sounds like
"the model is compromised", "the agent takes orders from somewhere else",
"prompt injection", "the tool did something nobody asked".

## Route

- An LLM endpoint, a chat interface, a prompt surface -> `skills/ai-iot-triage/SKILL.md`
- The agent's tool surface — MCP-style tools, function calls, code
  execution the model can reach -> `skills/mcp-agent-security/SKILL.md`
- A model file (.pkl, .pt, .onnx, safetensors) -> `skills/ctf-ai-ml/SKILL.md`
  (deserialization and weight-level attacks)
- Agent DEFENSE — find the malicious instruction in a transcript or
  config -> mcp-agent-security's review path, not the exploit path

## Corpus families inside mcp-agent-security

`inj-*` (injection shapes), `perm-*` (permission boundaries), `vx-*`
(vector classes: unicode, translate, summarize, split, roleplay, format).

## The insider/agent-hijack playbook — the theme-specific part

A swarm controlled by a compromised agent has four surfaces; map which one
the challenge hands you:

1. **Instruction channel.** Where untrusted text enters the agent's
   context: a telemetry feed, a mission queue, an ops dashboard, another
   agent's output. The injection lives in the channel nobody treats as
   input. `inj-*` modules carry the payload shapes.
2. **Tool boundary.** What the agent can DO once instructed: `perm-*`
   names the boundary classes. The exploit is a tool call with attacker
   text inside an argument the schema accepts (a path, a URL, a node id
   in the swarm).
3. **Command persistence.** Insider control survives restarts: a poisoned
   system prompt in a config file, a memory-store entry the agent reloads,
   a "standing order" record in the mission database. Look for what
   re-arms the hijack — that is usually the answer artifact.
4. **Beacon out.** Hijacked agents phone home through legitimate tools:
   a telemetry POST carrying task summaries to an unexpected destination,
   a status channel whose subscriber list gained a member. Exfil via the
   tool surface, not a new socket — find it in the tool-call log.

## Defense direction

When the task is to DEFEND or to find the compromise (common in this
theme): diff the agent's effective instruction set against the shipped
baseline — system prompt, tool schemas, memory store, cron-like standing
tasks. The delta is the insider's foothold. `white-box-intended-path`'s
anomaly-map method applies directly.

## What not to do

- Treating model output as evidence. An agent saying "I am not
  compromised" is tokens, not a measurement — the tool-call log is the
  record that counts.
- Broad fuzzing on a shared contest instance: injection probes are
  write-shaped on a live agent (they change its state). Cheapest
  discriminating probe first, per the prompt budget.
