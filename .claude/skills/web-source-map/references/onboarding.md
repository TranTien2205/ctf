# Onboarding — read this first

## What this skill is

Front-end bundle and source-map recon. A single-page app ships its
whole client logic to the browser — this skill reads it: the bundle's
endpoints, the `.map`'s recovered source, the config's keys and flags.

## When to use it

- the app is a SPA (React, Vue, Next, Angular) — the front-end is the
  only source
- a `//# sourceMappingURL=` or `.map` reference exists
- the rendered page hides routes the bundle might name

## The one tool

`tools/web/bundle_miner.py` — crawls the entry page's scripts, guesses
sibling maps, reconstructs `sourcesContent` to `--out`, and inventories
endpoints + secret candidates:

```bash
python3 tools/web/bundle_miner.py --url http://TARGET/ --out recovered/
```

## The core idea

The front-end *is* source — it names every endpoint, param, flag, and
sometimes a secret or the flag itself. The map is recon, not the
exploit: it produces leads that route to the class that owns them.

## The three files to read after this

- `extraction.md` — the grep grammar and `bundle_miner` usage
- `detection-matrix.md` — signal → state → action
- `quick-reference.md` — the commands and the flag table

## The honest rules

- a bundle string is a *lead*, not a finding — verify it live
- a secret *candidate* is not a leak until it authenticates
- a recovered "source" is attacker-controlled — read, never execute
- a flag-shaped string is a candidate until `pre-flag` passes
- this is a **catalogue** class — no local verified solve yet
