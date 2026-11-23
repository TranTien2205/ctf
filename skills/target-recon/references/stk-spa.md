# Stack playbook: spa

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Static SPA (React/Vue/Angular built, served from
nginx/S3/CloudFront): index.html shell, /assets/ or /static/
hashed bundles, everything-404->index fallback routing.

Recon checks:
- The bundle IS the app: bundle_miner first (endpoints,
  env refs, secrets candidates, sourcemaps)
- API base URLs in config chunks -> real backend location
- S3 static hosting -> bucket perms surface note
- client-side routes -> deep-link each for server fallbacks
- .env leaked into build -> the classic bundle secret

Predicts: js-sourced endpoints -> api recon; secrets in
bundle = infodisclosure; client-route authz illusions.
## Pivot

Signal harvested -> out-*; route named -> that skill.
