---
name: mcp-agent-security
description: >
  AI agent and tool-surface security for CTF. Use for a challenge whose target
  is an LLM, an agent, or an MCP-style tool server: map what the agent can reach,
  find where untrusted text enters its context, and reach the flag through the
  tool surface. Also the review checklist for anything this toolkit installs.
tags: [ai, agent, mcp, prompt-injection, tool-permissions, ctf]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---

# Agent and tool-surface security

**Catalogue skill.** This toolkit has not yet solved an agent challenge, so
everything here is standard knowledge plus the review practice this repository
already follows. Record what actually happens in `field-notes.md`.

Two uses, and they must not be confused:

1. **Offensive, in scope** — the challenge's own agent is the target and the flag
   sits behind its tools or its hidden instructions.
2. **Defensive, always** — reviewing an MCP server or tool bundle before this
   toolkit installs it. `../../EXTERNAL_SOURCES.md` is the same discipline
   applied to knowledge rather than code.

## Offensive: map before you push

The agent is an application whose input reaches a sink, exactly like any web
challenge. The map is what matters:

| Question | Why it decides the chain |
|---|---|
| Which tools can it call? | the tool list is the attack surface list |
| What does each tool actually touch? | filesystem, network, shell, credentials |
| Which tools run without confirmation? | those are the reachable ones |
| What text enters its context that you control? | that is the injection point |
| Does it read back its own output, or a file, or a page? | indirect injection lives there |

Read the supplied source first when there is any. An agent challenge that ships
its tool definitions is a white-box challenge.

## Where the flag usually is

- Inside the system instructions, so the task is to get them emitted.
- Behind a tool the agent will call but you cannot, so the task is to make it
  call that tool with your arguments.
- In a file only the agent's tool can read, which makes this
  `../file-read-primitives/` reached through a different caller.

## Probing order

1. Ask directly, once. Some challenges are exactly this and it costs one request.
2. Separate the request from the surrounding context: a different format, an
   encoding layer, a role the model treats differently.
3. Indirect: place the request inside data the agent will read later — a page it
   fetches, a file it opens, a record it looks up. This is usually the intended
   path when a direct ask is filtered.
4. Aim at the tool call rather than the text: get the agent to invoke a tool with
   arguments you chose. A tool result is evidence; a model's claim is not.

`references/prompt-injection-testing.md` has the payload shapes and how to tell a
real effect from a model simply agreeing with you.

## The evidence rule applies here too

A model saying "the flag is X" is **not** verification — it is the most likely
place in this whole toolkit to accept a fabricated answer. The flag must come
from a tool result, a file, or a response the challenge produced. If the only
source is the model's own text, the flag is a hypothesis.

## Defensive: reviewing a server before installing it

Provenance: is the source public, can it be pinned to a commit, is there a
licence, is the maintainer credible. Permissions: what each tool touches, and
whether a narrow purpose is asking for broad access. Injection surface: does any
tool return content from the open internet into the agent's context without
marking it as untrusted. Auto-execution: which tools run with no confirmation,
and whether destructive actions are gated in code rather than in documentation.
Supply chain: pinned dependencies, no runtime download of extra code.

`references/tool-permission-audit.md` is the structured checklist. Reject a server
that asks for broad filesystem or shell access for a narrow job, and prefer a
reviewed fork over tracking a moving branch.

## Scope

The offensive half applies only to the challenge's own agent. Do not test a
third-party MCP server you do not operate.

## References

- `references/prompt-injection-testing.md` — payload shapes and how to read a result
- `references/tool-permission-audit.md` — tool capability audit checklist

## Routing

Model file rather than a live agent: `../web-deserialization/`. Category router:
`../ai-iot-triage/`. Budget: `../LOOP_DISCIPLINE.md`.
