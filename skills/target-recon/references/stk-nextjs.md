# Stack playbook: nextjs

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Next.js fingerprints: /_next/static/ assets,
__NEXT_DATA__ JSON blob in every page, x-nextjs-* headers,
/_next/data/<build>/ JSON routes.

Recon checks:
- __NEXT_DATA__ -> props leak (server data rendered client-side)
  = free infodisclosure harvest
- /_next/data/<buildId>/<page>.json -> same data direct
- buildManifest.js + page chunks -> every route enumerated
  without crawling
- Middleware/API routes /api/* -> serverless surface
- getServerSideProps pages -> server-fetch behavior = ssrf
  prediction candidates

Predicts: infodisclosure (__NEXT_DATA__), ssrf (server props),
idor on /_next/data params, xss in hydration data.
## Pivot

Signal harvested -> out-*; route named -> that skill.
