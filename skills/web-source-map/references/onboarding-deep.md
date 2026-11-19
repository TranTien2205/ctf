# Onboarding (deep) — the full orientation

## What this skill is, in one paragraph

A single-page app ships its entire client logic to every visitor —
there is no server render to hide behind. `web-source-map` reads that
shipped source: the bundle's endpoint strings, route definitions,
param names, feature flags, config values, and sometimes a secret or
the flag; and the `.map`'s `sourcesContent`, which is the original
commented source. It is a **recon layer** — it produces *leads* that
route to the class that owns them; it does not itself find the bug.

## When you reach for it

- the app is a SPA (React/Vue/Next/Angular) — the front-end is the only
  source
- a `//# sourceMappingURL=` or `.map` reference exists
- the rendered page hides routes the bundle might name
- you need the *real* endpoint list, not a brute-forced guess

## The one tool

`tools/web/bundle_miner.py` — crawls the entry page's scripts, guesses
sibling + inline + header maps, reconstructs `sourcesContent` to
`--out`, and inventories endpoints, routes, flags, `process.env` refs,
and secret candidates:

```bash
python3 tools/web/bundle_miner.py --url http://TARGET/ --out recovered/
```

## The mental model

The bundle is a *compressed spec* — minification removes readability,
not information; the strings the program needs survive. The map is a
*disclosure* — `sourcesContent` is the developer's actual commented
source. The manifests are the *inventory* — the build's own route and
asset list.

## The lead → finding distinction

A bundle string is a *lead* (surface/claim evidence). It becomes a
*finding* only when its live check passes AND the routed class exploits
it. The recon layer's job is the lead; the finding is downstream.

## The reading order after this file

1. `detection.md`/`detection-deep.md` — is there a bundle/map
2. `extraction.md`/`extraction-deep.md`/`bundle-mining-deep.md` — the
   mining grammar + `bundle_miner`
3. `per-target-deep.md`/`lead-triage.md` — what each lead is worth
4. `verification-protocol.md`/`per-check-deep.md` — the live checks
5. `attack-shapes-deep.md`/`multi-step-chains-deep.md` — how it chains
6. `quick-reference-deep.md`/`checklist-deep.md` — the operator sheets

## The honest rules

- verify every lead live — a bundle string is a claim
- a secret is a candidate until it authenticates
- a recovered source is attacker-controlled — read, never execute
- a flag shape is a candidate until `pre-flag` passes
- **catalogue** — no local verified solve
