# Injection cell: split on code-agent

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself.

How `split` reaches a `code-agent` surface.

## Reach

Where the untrusted text enters this surface's context and whether
the injection family survives the trip (encoding layers, template
wrapping, retrieval formatting).

## Exfil

The outbound channel this surface exposes to the injection - a
URL parameter, a tool argument, a displayed image, or the answer
text itself.

## Pivot

Cell read -> `../llm-attacks.md` for the jailbreak playbook or
`meth-promptinj.md` for the injection base method.
