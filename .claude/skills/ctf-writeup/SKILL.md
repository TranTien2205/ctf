---
name: ctf-writeup
description: Generates a single standardized submission-style CTF writeup for competition handoff and organizer review. Use after solving a CTF challenge to document the solution steps, tools used, and lessons learned in a structured format.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash and Python 3.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "true"
  argument-hint: "[challenge-name]"
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "every claim in the draft has a verbatim evidence excerpt"
    - "a claim cannot be backed by recorded evidence: cut it, do not soften it"
---

# CTF Write-up Generator

Generate a standardized submission-style CTF writeup for a solved challenge.

Default behavior:

- During an active competition, optimize for speed, clarity, and reproducibility
- Keep writeups short enough that a teammate or organizer can validate the solve quickly
- Always produce a `submission`-style writeup
- Prefer one complete solve script from challenge data to final flag

## Workflow

### Step 1: Gather Information

Collect the following from the current session, challenge files, and user input:

1. **Challenge metadata** — name, CTF event, category, difficulty, points, flag format
2. **Solution artifacts** — exploit scripts, payloads, screenshots, command output
3. **Timeline** — key steps taken, dead ends, pivots

```bash
# Scan for exploit scripts and artifacts
find . -name '*.py' -o -name '*.sh' -o -name 'exploit*' -o -name 'solve*' | head -20
# Check for flags in output files
grep -rniE '(flag|ctf|eno|htb|pico)\{' . 2>/dev/null
```

### Step 2: Generate Write-up

Write the writeup file as `writeup.md` (or `writeup-<challenge-name>.md`) using the submission template below.

---

## Templates

### Submission Format

```markdown
---
title: "<Challenge Name>"
ctf: "<CTF Event Name>"
date: YYYY-MM-DD
category: web|pwn|crypto|reverse|forensics|osint|malware|misc
difficulty: easy|medium|hard
points: <number>
flag_format: "flag{...}"
author: "<your name or team>"
---

# <Challenge Name>

## Summary

<1-2 sentences: what the challenge was and the core technique. Keep it direct.>

## Solution

### Step 1: <Action>

<Explain the key observation in 3-8 short lines. Keep it direct.>

\`\`\`python
<one complete solving script from provided challenge data to printing the final flag>
\`\`\`

### Step 2: <Action> (optional)

<Only add this when a second short step genuinely helps readability, such as separating the core observation from final verification.>

### Step 3: <Action> (optional)

<Use only if the challenge really needs it. Keep the total number of steps small.>

## Flag

\`\`\`
flag{example_flag_here}
\`\`\`
```

Guidance:

- Prefer 1-3 short steps total
- Keep code to the smallest complete solving script
- Do not split "recover secret", "derive key", and "decrypt flag" into separate partial snippets
- The script should start from the challenge data and end by printing the flag
- Avoid long background sections
- Avoid dead ends unless they explain a key pivot
- Avoid multiple alternative solves; pick one clean path
- Redact the flag only if the user explicitly asks for redaction

---

## Best Practices Checklist

Before finalizing the writeup, verify:

- [ ] **Metadata complete** — title, CTF, date, category, difficulty, points, author all filled
- [ ] **Flag handling matches request** — keep the real flag unless the user asked for redaction
- [ ] **Reproducible steps** — a reader can follow your writeup and reproduce the solution
- [ ] **Code is runnable** — exploit scripts include all imports, correct variable names, and comments
- [ ] **No sensitive data** — no real credentials, API keys, or private infrastructure details
- [ ] **Length stays concise** — the writeup is short enough for fast review
- [ ] **Tools and versions noted** — mention specific tool versions if behavior depends on them
- [ ] **Proper attribution** — credit teammates, referenced writeups, or tools that were essential
- [ ] **Grammar and formatting** — consistent heading levels, code blocks have language tags

## Quality Guidelines

**DO:**
- Explain just enough for fast verification
- Include one complete solving path, not multiple alternative routes
- Include one complete script that goes all the way to the final flag
- Show actual output (truncated if very long) to prove the approach worked
- Tag code blocks with language (`python`, `bash`, `sql`, etc.)
- Keep the main path front-loaded so a reader can validate it quickly

**DON'T:**
- Copy-paste raw terminal dumps without explanation
- Paste several partial snippets that force the reader to reconstruct the final solve
- Leave placeholder text in the final writeup
- Include irrelevant tangents that don't contribute to the solution
- Assume the reader knows the specific challenge setup

## Repository integration

In this tree a writeup is not the end of a solve - it is one output of it. Two
things must happen alongside it, or the solve does not feed the knowledge base:

1. **The flag must have passed the write gate.** A writeup documents a flag
   that went through `tools/hooks.py pre-flag` from a live response or a
   supplied artifact. If the flag was never gated, the writeup is premature -
   verify first, write after.
2. **The chain card comes first.** `tools/classify_solve.py --chain <id>`
   files the solve into the right bug-class skill and the card lands in
   `knowledge/chains/`. The writeup is the human-readable companion of that
   card - card first, writeup second, never writeup instead of card.

### Solved-challenge ancestry

A solved challenge lives under `solved/` with its evidence ancestry - the
probe responses and artifacts the flag was read from. The writeup's Flag
section should cite that ancestry (the response file or artifact path), not
just the flag string, so a reviewer can re-derive the proof rather than trust
the text.

### What the writeup must never contain

- A flag the write gate never saw, presented as solved.
- A claimed mechanism the evidence does not show - if the writeup says
  "SSTI via Jinja2", the Solution section must quote the response that proved
  it (the evaluated marker), not only the payload that worked.
- Negative results erased from the timeline. A dead end that burned budget
  belongs in the Timeline as a proved negative - the next solver of a similar
  challenge needs to know it was closed and by which measurement.
- Tool output the tool did not produce. If `sqlmap` or `radare2` output is
  quoted, it is pasted verbatim from a run that happened; a reconstructed
  "typical output" is fabrication and fails the evidence policy.

### Category-specific evidence rows

| Category | The writeup's proving excerpt |
|---|---|
| web | the verbatim response bytes carrying the flag or the confirming oracle delta |
| pwn | the transcript showing the flag read (e.g. `cat flag` output) from the exploited service |
| rev | the recovered key/flag check passing, or the decompiled predicate that produces it |
| crypto | the decryption output from the derived key/params, with the math stated once |
| forensics/osint | the artifact + tool invocation whose output contains the answer |
| misc | the interpreter/carrier output producing the flag bytes |

### Where it lands

Write the writeup beside the challenge state (`challenges/<name>/` is the
working dir; `solved/<name>/` holds the evidence ancestry). The card, the
ancestry, and the writeup are three views of one solve - they must agree, and
any disagreement is a defect to fix in the evidence, not in the prose.

## Challenge

$ARGUMENTS

## Corpus index

`references/` carries the writeup material: `sec-*` section guides,
`cat-*`/`cls-*`/`cls2-*` per-class evidence shapes, `evidence-*`/
`verbatim-*`/`neg-*`/`fmt-*`/`submit-*`/`length-*` rules, plus `sx-*`/
`qx-*`/`sa-*`/`fe-*`/`cq-*` matrices, each with a `-route` companion.
