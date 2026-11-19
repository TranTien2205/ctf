---
name: web-source-map
description: >
  Front-end bundle and source-map recon. Use when the app ships a JavaScript
  bundle (React, Vue, Next.js, webpack, Vite) and the front-end is the only
  source available. Recover original sources, endpoints, feature flags and
  secrets from bundles and .map files.
tags: [web, javascript, source-map, recon, ctf]
environment: [ctf, lab, authorized-testing]
---

# Front-end bundle and source-map recon

**Catalogue technique.** Nothing in this toolkit has solved a challenge with this
technique yet. Treat it as standard published knowledge and record real results
in `field-notes.md`.

## Recognise

A single-page app, `/_next/static/`, `/static/js/`, `/assets/index-*.js`, a
`//# sourceMappingURL=` comment, or a `*.js.map` reference. The front-end is
source too: it names every endpoint, parameter and sometimes a key.

## Operational probe

1. Fetch the entry page and list every script URL it loads.
2. Fetch each bundle and extract: URLs, route paths, parameter names, feature
   flags, `api/` prefixes, and any string that looks like a key or token.
3. Request the bundle's `.map` file (`<bundle>.js.map`) and, for Next.js, the
   `_buildManifest.js` and `_ssgManifest.js`.

```bash
curl -s "$BASE/" | grep -oE '/[A-Za-z0-9._/-]+\.js' | sort -u
curl -s "$BASE/static/js/main.js" | grep -oE '"/[A-Za-z0-9_./?=&-]+"' | sort -u
curl -s -o map.json -w '%{http_code}\n' "$BASE/static/js/main.js.map"
```

Expected confirmation is an endpoint, parameter, secret, or original source that
the rendered page did not expose. A minified bundle with no readable strings and
a 404 map is a falsifier for this route.

## Budget and stop_conditions

This is a **bounded recon pass**, not an exploit. Budget: one entry fetch, the
manifests, the map probes, one `bundle_miner` run, targeted greps, and one verify
pass per lead — within the shared five-probe / fifteen-minute mechanism budget.
stop_conditions:

- every lead is verified-or-dead and routed — stop; the exploit is the routed
  class, not a second mining pass
- a bundle set with no readable strings and no `.map` anywhere — stop; record a
  dead end and move to `web-triage`/`web-info-disclosure`
- every endpoint `404`s and every secret fails — stop; record the negatives

Never re-mine a dead bundle, and never claim a lead as a finding without its
live check.

## What to do with it

- Every endpoint found is a real endpoint: feed it to `../web-triage/` rather
  than directory brute force.
- A leaked key or token goes to `../web-auth-session/`.
- A hidden admin route goes to `../web-idor/` or `../web-logic-flaw/`.
- A `sourceMappingURL` that resolves means original source, not just minified
  code; read the real file names and logic.

## Traps

- A 200 with HTML for a `.map` request is a catch-all, not a source map; check
  the content type and the first bytes.
- Next.js chunks are per-route; the interesting endpoint is often in a page
  chunk, not `main`.
- Do not open the whole bundle into context; grep for the specific token.

## Routing

Shares signals with: `../web-triage/`, `../file-read-primitives/`,
`../web-info-disclosure/`. Depth, one named file at a time:
`../ctf-web/client-side.md`.

| Need | File |
|---|---|
| the bundle + map mechanism | `references/mechanism.md`, `references/mechanism-deep.md`, `references/bundle-lifecycle.md`, `references/mechanism-index.md`, `references/mechanism-map.md`, `references/mechanism-catalogue.md` |
| detect + fingerprint | `references/detection.md`, `references/detection-deep.md`, `references/detection-matrix.md`, `references/detection-index.md`, `references/detection-checklist.md`, `references/detection-surface.md`, `references/detection-map.md`, `references/detection-playbook.md`, `references/bundle-formats.md`, `references/per-file.md`, `references/per-artifact.md` |
| the `.map` recovery | `references/source-maps.md`, `references/source-maps-deep.md`, `references/map-playbook.md` |
| extract endpoints/params | `references/extraction.md`, `references/extraction-deep.md`, `references/extraction-index.md`, `references/extraction-playbook.md`, `references/extended-greps.md`, `references/endpoint-inventory.md`, `references/endpoint-playbook.md`, `references/param-surface.md`, `references/per-param.md`, `references/per-endpoint-class.md`, `references/bundle-mining.md`, `references/payload-patterns.md` |
| secret/config/flag mining | `references/secrets.md`, `references/secrets-catalogue.md`, `references/secrets-playbook.md`, `references/per-secret-class.md`, `references/config-mining.md`, `references/per-prefix.md`, `references/flag-mining.md`, `references/flag-playbook.md`, `references/route-guard.md` |
| routes / structure / comments / sinks | `references/route-table.md`, `references/per-route.md`, `references/structure-mining.md`, `references/comment-mining.md`, `references/sink-mining.md`, `references/per-sink.md`, `references/graphql-surface.md`, `references/lead-grammar.md` |
| per-framework internals | `references/frameworks.md`, `references/webpack-internals.md`, `references/nextjs-internals.md`, `references/vite-internals.md`, `references/vue-internals.md`, `references/angular-internals.md` |
| service worker / adjacent / authed / dev | `references/service-worker-mining.md`, `references/adjacent-disclosure.md`, `references/authenticated-bundle.md`, `references/dev-build.md`, `references/deobfuscation.md`, `references/obfuscation-formats.md` |
| the ordered pass | `references/workflow.md`, `references/workflow-playbook.md`, `references/workflow-map.md`, `references/workflow-checklist.md`, `references/playbook.md`, `references/first-hour.md`, `references/field-manual.md`, `references/field-manual-map.md`, `references/checklist.md`, `references/field-checklist.md`, `references/quick-map.md`, `references/probe-catalogue.md`, `references/decision-table.md`, `references/operator-notes.md`, `references/worked-examples.md`, `references/recon-order.md`, `references/preconditions.md`, `references/onboarding.md` |
| a lead to its class | `references/lead-triage.md`, `references/per-target.md`, `references/per-check.md`, `references/per-route.md`, `references/per-surface.md`, `references/per-vector.md`, `references/per-boundary.md`, `references/class-boundary.md`, `references/attack-shapes.md`, `references/multi-step-chains.md`, `references/scenarios.md` |
| evidence / falsifiers | `references/evidence-rules.md`, `references/evidence-playbook.md`, `references/evidence-map.md`, `references/verification-protocol.md`, `references/falsifiers.md`, `references/per-falsifier.md`, `references/falsifier-map.md` |
| dead ends / cases | `references/negative-results.md`, `references/negative-map.md`, `references/case-studies.md`, `references/real-world-cases.md`, `references/verified-chains.md`, `references/closing-notes.md` |
| edge cases / mistakes / fixes | `references/edge-cases.md`, `references/common-mistakes.md`, `references/anti-patterns.md`, `references/troubleshoot.md`, `references/troubleshooting-map.md`, `references/evasion.md`, `references/evasion-deep-2.md` |
| reference | `references/theory.md`, `references/glossary.md`, `references/summary.md`, `references/common-questions.md`, `references/mechanism-index.md`, `references/extended-corpus.md`, `references/index.md`, `references/field-notes-deep.md` — every file also has a `-deep`/`-index`/`-checklist`/`-map` variant |

The full index is `references/README.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
