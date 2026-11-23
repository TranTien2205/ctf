# Worked example: empty-enum

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: intake produced a bare shell, zero
routes after JS+robots+common probes.

1. base-wildcardcheck: 404 works normally - server DOES 404,
   the surface is genuinely thin.
2. bundle_miner deeper: /static/main.<hash>.js -> 30+ api
   calls recovered = the real surface was all JS-driven.
3. Observations: SPA-shape, api base /internal/v2,
   endpoints from bundle verbatim.
4. classify on the extracted list - 'empty enum' was the
   neg-emptyenum recorded negative, not a dead end.
## Pivot

Signal harvested -> out-*; route named -> that skill.
