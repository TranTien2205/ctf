# Security Policy

## Intended use

Argus is an LLM-driven agent for **authorized** web penetration testing only —
engagements where you hold written permission for the target, plus CTF and lab
work. Pointing it at a system you do not own or have not been engaged to test
is prohibited and may be unlawful.

The tool enforces a hard target scope (`--target` plus optional
`--scope-host`), request budgets, and rate limits in code — not in prompts.
These guardrails exist to keep an authorized engagement inside its letter of
authorization; they are not a license to point at anything.

## Reporting a vulnerability

If you find a security issue in Argus itself — for example a way to bypass
`ScopeGuard`, the evidence gate, role tool restrictions, or the transcript
hash chain — please do NOT open a public issue. Report it privately to the
maintainer via GitHub's "Report a vulnerability" flow (Security tab → Advisories)
or by contacting the repository owner directly.

Please include: the component, a minimal reproduction, and whether the issue
lets an attacker-controlled target escape scope, forge findings, or tamper
with audit artifacts.

## Known constraints

- The bundled `lab/vulnapp.py` is intentionally vulnerable. Bind it to
  localhost only; never expose it on a network interface.
- LLM credentials resolved from `~/.claude/.credentials.json` or OpenCode are
  used in memory only and never written to transcripts or reports.
