# Falsifier map — the kill map at a glance

## The eight cells

```
┌─────────────────────┬────────────────────────┬──────────────────┐
│ cell                │ kill probe             │ re-open          │
├─────────────────────┼────────────────────────┼──────────────────┤
│ endpoint-exposure   │ POST /session refused  │ another port/    │
│                     │ on all candidates      │ route answers    │
├─────────────────────┼────────────────────────┼──────────────────┤
│ file-read           │ file:// nav + source   │ execute fetch or │
│                     │ error/empty            │ another scheme   │
├─────────────────────┼────────────────────────┼──────────────────┤
│ js-execution        │ execute 1+1 -> error   │ execute/async or │
│                     │                        │ CDP Runtime.eval │
├─────────────────────┼────────────────────────┼──────────────────┤
│ loopback-reach      │ localhost nav shows    │ another internal │
│                     │ nothing extra          │ port/route       │
├─────────────────────┼────────────────────────┼──────────────────┤
│ reproduction        │ cannot copy bot spec   │ source found or  │
│                     │ (no src, no obs)       │ more observed    │
├─────────────────────┼────────────────────────┼──────────────────┤
│ exfil-channel       │ goto own tunnel =      │ another tunnel;  │
│                     │ interstitial/refused   │ same-origin; DNS │
├─────────────────────┼────────────────────────┼──────────────────┤
│ flag-in-reach       │ flag on no reachable   │ a new surface    │
│                     │ surface                │ found            │
├─────────────────────┼────────────────────────┼──────────────────┤
│ bot-flow            │ no bot; JS canary      │ a real bot flow; │
│                     │ proves a fetch not a   │ it's actually    │
│                     │ browser                │ SSRF             │
└─────────────────────┴────────────────────────┴──────────────────┘
```

## The compound rule

The class is dead when **both** uses are dead:

- attack surface dead = endpoint-exposure dead (no endpoint) OR
  flag-in-reach dead (endpoint but no flag reachable)
- debugging aid dead = bot-flow dead (no bot) — reproduction dead only
  weakens, does not kill

## The per-cell note

- **endpoint-exposure**: test *all* candidates (`9515`,`4444`,`9222`,
  proxied `/session`,`/wd/hub`) before the cell is dead — one refused
  port is one route, not the whole surface.
- **file-read**: `file://` *navigation* and `execute` `fetch("file://")`
  are separate primitives — a nav block does not kill the JS read.
- **js-execution**: dead JS leaves navigation reads alive — the cell
  closes the JS primitive, not the surface.
- **reproduction**: a failed reproduction is a *weakened* state — the
  class still has the live fire; record it as weakened, not dead.
- **flag-in-reach**: the subtle cell — an open endpoint with no
  reachable flag is dead for *this* flag path, but a new surface
  re-opens it.

## The falsifier is not a guess

A cell is dead on a *measured* state — the probe ran, the kill state
observed. "Didn't try it" is not a falsifier; "ran it, it refused" is.
