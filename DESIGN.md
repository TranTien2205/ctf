# CTF-Only Design

## Scope boundary

`~/ctf` is for jeopardy and attack-defense CTFs, including whitebox and
blackbox challenges. It does not read or import the red-team machine toolkit,
its knowledge-base, upstream writeups, or machine triage scripts.

## Strengths

- Fast classification without nmap, machine fingerprinting, or broad retrieval.
- Whitebox source scan finds flag candidates and high-signal sinks in one pass.
- Blackbox route returns one category and a single next action.
- Public writeup lookup is available early and cached for 24 hours.
- CTF categories have their own skill namespace.

## Weaknesses

- Planning and workflow notes are operator aids, not an autonomous solver.
- State persistence is atomic but single-writer; concurrent updates are not merged.
- Command logging records explicit processes, not a sandbox or evidence-verification engine.
- Static source signatures can produce false positives and cannot prove exploitability.
- Writeup search depends on network access and search-engine quality.
- Some inherited CTF notes contain historical machine-flavoured examples and need
  curation before being treated as trusted CTF evidence.
- Attack-defense needs a dedicated service-health, patch-diff, and reliability workflow.
- No automatic flag submission is included; event credentials stay outside the toolkit.

## Speed policy

1. Route once.
2. Open only the selected CTF skill.
3. Run one cheapest probe.
4. Search writeups immediately when challenge name and event are known.
5. Treat writeups as hints; verify flags from the target or challenge artifact.

Do not copy HTB/VulnLab machine chains into this tree. Add CTF writeups only
after recording category, signal, exploit primitive, and verification evidence.
