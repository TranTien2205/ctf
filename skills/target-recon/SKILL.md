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

## Stack identified -> its playbook

Once the fingerprint names a stack, open `references/stk-<stack>.md` -
wordpress, django, drf, rails, laravel, express, nextjs, nuxt, spring,
aspnet, flask, fastapi, graphqlsvc, grpc, phpgeneric, javageneric,
gogeneric, nodegeneric. Each playbook carries that stack's default
paths, auto-generated endpoints, predictable parameters, and which bug
classes its conventions make likely. API-shaped targets get
`references/api-*`; a login is in scope gets `references/au-*`; a
non-HTTP banner gets `references/svc-*`.

## Passive recon for domains

When the input is a domain (and scope allows): crt.sh SANs, DNS
records, PTR, whois freshness, wayback endpoints - the `pasv-*`
modules. Passive sources yield names, params and stack hints without
a single request to the target.

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
fresh enumeration - run the matcher before inventing probes. When a class
is named, `references/cls-<class>.md` lists the exact recon evidence that
depth skill needs (e.g. cls-sqli wants injectable params + a DBMS prior +
one oracle) - check the recheck list once before opening the depth skill.

## Corpus index

`references/` carries ~3,500 modules. `walk-*` are worked end-to-end
examples per target type (a URL web target through a websocket
endpoint) - open one when the intake shape is unfamiliar: `work-*` pipeline, `type-*` target
kinds, `chk-*` per-type checklists, `sig-*` signals, `probe-*` commands,
`finger-*`/`fx-*` fingerprinting, `enum-*`/`ex-*`/`ex2-*` enumeration,
`js-*` front-end, `scope-*` rules, `nonweb-*`/`svc-*` service intake
(web banners through k8s/docker/snmp), `iot-*` embedded targets,
`wx-*` websocket depth, `word-*` wordlist selection, `snap-*` visual/
DOM recon, `out-*`/`obs-*` handoff, `stk-*` stack playbooks (18 + 9
more incl. coldfusion/tomcat/weblogic/iis/spa), `pasv-*` passive recon,
`api-*` API recon, `au-*` authenticated recon, `pd-*`/`pe-*` param and
path depth, `prm-*` per-parameter checks, `inp-*` input-surface
taxonomy, `cls-*` per-class recheck (what evidence each depth skill
needs), `rsp-*`/`rdc-*`/`cki-*`/`hdr-*` response, redirect, cookie and
header depth, `base-*` baselines, `tlx-*` tool-output parsing,
`prt-*` port priors, `vh-*` vhosts, `cdn-*`/`tls-*` edge and transport
identity, `cld-*` cloud-platform recon (provider id, metadata
surfaces, bucket permutations, cloud error fingerprints),
`net-*` IPv6/internal addressing, `mob-*` mobile endpoint
extraction, `prot-*` HTTP/2/3 depth, `surf-*` second-order
surfaces, `erd-*` error depth, `rl-*` rate limits, `crawl-*`
strategy, `ctf-*` CTF specifics, `neg-*` negatives, `trap-*`
traps, plus `sx-*`/`rx-*`/`rx2-*`/`rx3-*` signal x class,
`tx-*` type x step, `dx-*`/`dx2-*` discovery x route and the
`stk-*-*/pasv-*-*/svc-*-*/pd-*-*/pe-*-*/inp-*-*/cld-*-*`
matrices, each with a `-route` companion. `agg-index` is the corpus's
own index file, `tool-inventory` the local tool table, `q-*` the intake
questions.

## Discipline

- Observations only - a fingerprint is a hint, never a finding.
- Three commands before any wordlist; smallest list that answers.
- Verbatim evidence for every recorded observation.
- One router opens after recon: `web-triage` for HTTP, the category
  router the signals name otherwise. Budget as in `../LOOP_DISCIPLINE.md`.
