# Closing notes — what a complete pass proves

## The done-state

A `web-source-map` pass is done when:

1. **the bundle set is enumerated** — every entry `<script src>` + every
   lazy chunk a manifest names, deduped
2. **the map surface is probed** — `sourceMappingURL`, sibling `.map`,
   `SourceMap` header, `/static/maps/`, inline `data:` — each checked and
   a real map confirmed as `application/json` `{"version":3`
3. **every surface is mined** — endpoints, params, secrets, config,
   flags, routes, structure, comments, sinks, GraphQL — from EVERY
   chunk, not `main` alone
4. **every lead is verified-or-dead** — each endpoint `curl`'d, each
   secret authenticated-or-dead, each flag's endpoint probed for a
   server check, each flag-shape `pre-flag`'d
5. **every lead has provenance** — `string, source_file, verify_result,
   verdict` — and every dead lead carries the falsifier that killed it
6. **the live leads are routed** — each to its class's depth skill

## What a complete pass proves

- the front-end's named surface is fully enumerated and live-checked
- every credential candidate is either verified-live or recorded-dead
- every client-side gate is either proven server-enforced or routed as
  a client-gate finding
- the recovered source (when a map exists) is reconstructed, mined, and
  its sinks routed
- the route is either handed to a live lead's class or recorded as a
  clean dead end with the falsifiers that fired

## What a complete pass does NOT prove

- that a dead endpoint was never live (the route may have been renamed,
  or gated behind auth the recon lacked)
- that a publishable-looking secret is safe (a `pk_live_` may still
  unlock a permissive backend — a `403` that stays `403` is the proof)
- that an opaque bundle has no surface (a deeply obfuscated bundle can
  hide endpoints string-mining misses — the surface may need a runtime
  capture)
- that a clean bundle ends the challenge — the surface may be
  server-side, not shipped in the bundle at all

## The honest close

Report what the map produced: `N leads, M live, K dead`. A live lead is
handed to its class; a dead lead is a recorded negative; a clean
nothing-actionable pass is itself a finding ("the front-end is not the
surface"). Never present a lead as a find, a flag-shape as a flag, or
a catalogue shape as "worked here" — the class carries no local
verified solve.
