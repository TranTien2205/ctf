---
name: web-ssti
description: >
  Server-side template injection. Use when a request value is rendered by a
  template engine, template syntax appears in an error, or an arithmetic marker
  evaluates. Identify the engine first, then pull references/<engine>.md.
tags: [web, ssti, template-injection, rce]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "engine misidentified twice"
    - "sandbox escape fails 3 times with no new signal"
evidence_level: verified
---

# SSTI — Depth Skill

**Verified here.** Chains that prove this class: `htb-neonify-erb-ssti-newline-filter-bypass`, `htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce`.


## First probe

One arithmetic marker. Confirm the engine from the evaluated form, or from the
error string, before building any chain.

**Falsifier** - the observation that closes this class: the marker is reflected
literally, which is an XSS shape rather than template evaluation.

## Identify the engine before any chain

| Marker | Evaluates in |
|---|---|
| `{{7*7}}` | Jinja2, Twig, Mako |
| `${7*7}` | Freemarker, Velocity |
| `#{7*7}` | Thymeleaf, Ruby ERB |
| `<%= 7*7 %>` | ERB |
| `{{7*'7'}}` | `49` is Jinja2; `7777777` is Twig |

Confirm against the error text: a Jinja exception, a Twig error class, a
Freemarker core message. Full fingerprint table in
`references/engine-detection.md`.

If the marker is reflected literally rather than evaluated, this is not template
injection — go back to `../web-triage/` and consider XSS instead.

## One execution probe per engine, then depth

- Jinja2 — reach the operating-system module through a template global, then
  `references/jinja2.md`
- Twig — apply a system filter to a single-element array, then
  `references/twig.md`
- Freemarker — instantiate the utility execute class, then
  `references/freemarker.md`
- Velocity — reach the runtime through class inspection, then
  `references/velocity.md`

Use one harmless command first, such as printing the current user, and read the
exact output before building anything larger.

## Filter and sandbox bypass

Attribute names split and concatenated; indexes supplied through a request
parameter; character construction from codes; URL encoding of the delimiters.
Full catalogue in `references/ssti-bypass.md`.

## Variants

When this file lacks the needed variant, open one named file:
`../ctf-web/server-side-exec.md`.

## Discipline

- No evaluated arithmetic means no confirmed template injection. Do not fire an
  execution chain before the marker evaluates.
- Two wrong engine guesses: return to the identification table instead of
  forcing another engine's payload. See `../LOOP_DISCIPLINE.md`.

## Operational probe

One arithmetic marker, and identify the engine from the *evaluated form* before
any chain:

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-ssti \
  --url "$BASE/profile" --method POST --body 'name={{7*7}}' \
  --evidence-contains 49 --evidence-kind class \
  --on-match confirms --on-miss inconclusive
```

If `49` appears, try `${7*7}` and `#{7*7}` to separate the engine families before
opening any `references/<engine>.md`.

**Falsifier:** the marker is reflected literally — that is an XSS shape, not
template evaluation, so switch class rather than escalating payloads.

Pipe the result straight into the write gate: `http_probe.py` already emits the
shape `tools/hooks.py post-probe` wants, so the excerpt is verbatim and a
transport failure is recorded as `transport`, which can never confirm.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
