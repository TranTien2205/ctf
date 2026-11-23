---
name: target-recon
description: >
  Recon for a supplied live target before any bug class is named. Turn one
  URL, host:port or domain into the signal list classify.py consumes: entry
  fetch, stack fingerprint, endpoint and parameter enumeration, front-end
  harvest - bounded to the supplied port and a cheap request budget. Recon
  produces observations; it never claims a vulnerability.
tags: [recon, enumeration, fingerprint, intake, web, live-target, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "every observation from the intake is recorded and classify.py has run"
    - "the target does not answer the supplied port: report unreachable"
    - "three enumeration targets return nothing new: hand off to classify"
evidence_level: catalogue
---
# Target recon - the intake before classification

**Catalogue method.** Recon is not a bug class: it produces the observations
that let `tools/classify.py` and the routers name one. It runs on a live
target with no signals yet - before `web-triage`, before any depth skill,
and always inside the supplied scope.

## First probe - the three-command intake

```bash
python3 tools/web_probe.py <url>            # entry page + stack headers
python3 tools/web_enum.py <url>             # standard-surface enumeration
python3 tools/web/bundle_miner.py <url>     # front-end: endpoints, maps, secrets
```

Three commands before any scanner runs. A raw TCP target instead:
`nc <host> <port>` once for the banner - a text prompt routes to
`pwn-binary-triage`.

## Intake by target type

| Supplied | First intake | Corpus |
|---|---|---|
| `https://host:port/` | the three commands above | `references/type-url.md` |
| `host:port` | one GET; if not HTTP, banner grab | `references/type-hostport.md` |
| domain | HTTP(S) on that host only, no vhost sprawl | `references/type-domain.md` |
| source + live | confirm deployed behavior, then intake | `references/type-sourcelive.md` |
| raw service | `nc` once, capture the prompt verbatim | `references/type-rawtcp.md` |

## What recon harvests

Headers (`Server`, `X-Powered-By`), cookie names and shapes, form fields,
script tags, error pages, redirect targets, `Allow:` methods, CORS/CSP,
WAF behavior, version strings, endpoint and parameter inventories.
`references/sig-*` names each signal's class weight; `references/fx-*`
maps fingerprint features to stacks.

## Enumeration, bounded

- `robots.txt`, `/sitemap.xml`, `/.git/HEAD`, `.env`, backups, common
  framework paths, API docs, `/graphql`, websocket endpoints - cheapest
  first; the tool choice per target is in `references/ex-*`.
- `ffuf`/`gobuster`/`feroxbuster` only after the page and JS are read, on
  the smallest wordlist that answers the question, with the negative
  baseline calibrated first.
- `nmap -p <port> -sV` on the supplied port only. Never a range scan on a
  shared host; keep rates low and record counts small.

## Scope

Only the supplied port and host. No subdomain or vhost sprawl unless the
scope grants it, no write-shaped probing during recon, no load that could
kill a shared instance. `references/scope-*` carries the rules.

## The handoff

The product is an observation list - stack, surface, params, oddities,
each with verbatim evidence. Then:

```bash
python3 tools/classify.py "<observation list>"
python3 tools/chain_match.py "<observation>"
python3 tools/state.py <name> --category <cat> --target <url>
```

Recon ends where classification begins. A strong chain card outranks any
fresh enumeration - run the matcher before inventing probes.

## Corpus index

`references/` carries ~1,400 modules: `work-*` pipeline, `type-*` target
kinds, `sig-*` signals, `probe-*` commands, `finger-*`/`fx-*` fingerprinting,
`enum-*`/`ex-*` enumeration, `js-*` front-end, `scope-*` rules, `nonweb-*`
raw-service intake, `out-*` handoff, plus `sx-*`/`rx-*` signal x class,
`tx-*` type x step and `dx-*` discovery x route matrices, each with a
`-route` companion.

## Discipline

- Observations only - a fingerprint is a hint, never a finding.
- Three commands before any wordlist; smallest list that answers.
- Verbatim evidence for every recorded observation.
- One router opens after recon: `web-triage` for HTTP, the category
  router the signals name otherwise. Budget as in `../LOOP_DISCIPLINE.md`.
