# Security Policy

## Intended use

Argus is an LLM-driven agent for **authorized** web penetration testing only —
engagements where you hold written permission for the target, plus CTF and lab
work. Pointing it at a system you do not own or have not been engaged to test
is prohibited and may be unlawful.

The tool enforces a hard target scope (the target is the positional argument
to `argus run`, plus optional `--scope`/`--exclude`), request budgets, and
rate limits in code — not in prompts.
These guardrails exist to keep an authorized engagement inside its letter of
authorization; they are not a license to point at anything.

## Reporting a vulnerability

If you find a security issue in Argus itself — for example a way to bypass
`ScopeGuard`, the evidence gate, the proof matrix (a claim reaching `proven`
without the vulnerability), the lab's command allowlist, role tool
restrictions, or the transcript hash chain — please do NOT open a public
issue. Report it privately to the
maintainer via GitHub's "Report a vulnerability" flow (Security tab → Advisories)
or by contacting the repository owner directly.

Please include: the component, a minimal reproduction, and whether the issue
lets an attacker-controlled target escape scope, forge findings, or tamper
with audit artifacts.

## What the audit chain proves

The hash chain over `transcript.jsonl` is **tamper-evident, not
forgery-resistant**, and the distinction matters when a report is read by
someone who did not watch the run. Unkeyed, each link is
`sha256(previous + entry)` - computable by anyone with this code - so it
proves no entry was edited, inserted or removed after the run, and proves
nothing about whether the run happened. `--seal-key <key-or-keyfile>` (or
`ARGUS_SEAL_KEY`) makes each link HMAC-SHA256 instead; only a holder of the
key can then produce a chain that verifies. The key is never written to any
artifact - `meta.json` records only that the chain is keyed - and
`argus verify --seal-key ...` is how a keyed run is checked. Without the key
verify reports that it cannot check rather than reporting every line as
tampered.

## Known constraints

- The bundled `lab/vulnapp.py` is intentionally vulnerable. Bind it to
  localhost only; never expose it on a network interface. Its `/ping`
  endpoint **really executes commands** so that the rce proof requirement is
  reachable: argv through a seven-command allowlist (`id`, `whoami`,
  `uname`, `hostname`, `pwd`, `echo`, `cat`), never a shell, `cat` confined
  to the lab's fake filesystem, and the server binds `127.0.0.1`. A
  destructive or networked payload returns `command not found`. The
  injection is real; the blast radius is bounded by the allowlist, not by
  string matching on the payload.
- LLM credentials resolved from `~/.claude/.credentials.json` or OpenCode are
  used in memory only and never written to transcripts or reports.
- The private-address check resolves every record via `getaddrinfo` before
  each request AND inspects the connected peer address, so a hostile DNS
  server that answers differently at connect time (rebinding into private
  space) is refused. Residual: a hostile resolver could still bind the
  hostname to a different *public* address than the operator intended, and
  external tools own their sockets (their peer can't be inspected) — do not
  point Argus at targets whose DNS you believe is attacker-controlled.
