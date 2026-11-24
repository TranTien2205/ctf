---
name: contest-domain-map
description: >
  Domain router for a multi-domain contest whose organisers publish focus
  areas in advance. Use when the challenge statement, the event brief or a
  teammate's summary says which domains the event runs -- log forensics and
  attack-chain reconstruction, OSINT identity tracking, AI attack and
  defense, Linux exploitation, embedded and hardware analysis, memory
  forensics and malware -- and the job is to open the right router, not to
  guess one. Maps each domain to its router, its first three commands and
  the corpus families inside it. Routes; never solves.
license: MIT
compatibility: Requires filesystem-based agent with bash and Python 3.
allowed-tools: Bash Read Write Edit Glob Grep
metadata:
  user-invocable: "false"
evidence_level: catalogue
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "the domain is named and one router is open -- this file's work is done"
    - "two domains tie: open the one whose artifact or target is already in hand"
    - "the input is a bare live target -- skills/target-recon runs first, not this map"
---

# Contest domain map - router for a published-domain event

A multi-domain contest advertises its six areas before the first flag drops.
This file maps each domain label to the router that owns it, the three
commands that start the loop, and the corpus families worth opening first.
It never names a bug class and never answers an investigation question -
it hands a domain to the skill that does.

## The map

| Domain label (event vocabulary) | Router to open | First commands |
|---|---|---|
| system logs, attack-chain reconstruction, "what did the attacker do" | `skills/dfir-sherlock-triage/SKILL.md` | `python3 tools/state.py <id> --category dfir`, inventory the bundle, then `tools/subagent_fanout.py --dfir` |
| OSINT, identity, fake accounts, "who is this handle" | `skills/osint-triage/SKILL.md` | extract the unique pivot, then `python3 tools/classify.py "<handle>"` |
| AI attack/defense, agent hijack, model or tool abuse | `skills/ai-iot-triage/SKILL.md` or `skills/mcp-agent-security/SKILL.md` | `python3 tools/classify.py "<obs>"` -- LLM endpoint to ai-iot-triage, tool surface to mcp-agent-security |
| Linux exploit, binary pwn, remote service | `skills/pwn-binary-triage/SKILL.md` | `python3 tools/pwn_triage.py <binary>` then the protection-to-route table |
| embedded, hardware, firmware, swarm protocol | `skills/ai-iot-triage/SKILL.md` | file-type the artifact: pcap to forensics-pcap-carve, image to rev-triage, live device to target-recon |
| memory forensics, malware on a host | `skills/forensics-memory-analysis/SKILL.md` or `skills/ctf-malware/SKILL.md` | image -> memory-analysis find-* families; binary -> ctf-malware pe/c2/obf |

A domain that is a **bare live target** (URL, host:port, domain, IP) does not
enter this map at all: `skills/target-recon/` runs the bounded intake first,
and its observation list is what `tools/classify.py` consumes.

## Out of scope

Local Windows privilege escalation and machine-box methodology are the other
toolkit's territory -- the scope boundary in `AGENTS.md` holds here. A remote
Linux service exploit or a pwn binary is in scope and routes above.

## Corpus index

| Family | Contents |
|---|---|
| `dom-logs-*` | area: log forensics -> attack-chain reconstruction; artifact-to-router table and the cross-artifact correlation method |
| `dom-osint-*` | area: identity tracking; pivot selection, sockpuppet tells, cross-platform handle reuse |
| `dom-ai-*` | area: AI attack/defense; agent-hijack surface, tool poisoning, model supply chain |
| `dom-linux-*` | area: Linux exploitation; binary to protections to route; the scope note |
| `dom-embedded-*` | area: hardware and swarm protocols; MQTT, MAVLink, CAN, ROS intake and artifact routing |
| `dom-memory-*` | area: memory forensics and malware; image vs binary split, find-* families, c2/obf |
| `walk-*` | an end-to-end intake trace: challenge statement to domain to router |

## Stop rule

This file routes. Once one domain's router is open, the contest loop in
`tools/contest/` and `tools/decide.py` owns the clock. Spending a second
budget here reading playbooks sideways is reading, not routing.
