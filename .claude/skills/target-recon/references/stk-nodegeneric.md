# Stack playbook: nodegeneric

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Node generic: Express-style or frameworkless,
etag W/"<len>-<hash>", keep-alive, JSON-first APIs.

Recon checks:
- etag weak validator shape -> http.IncomingMessage style
- /api/ conventions + package.json leaks via static maps
- process.env refs in bundles -> bundle_miner secrets
- Source maps -> webpack/ts source = complete backend hints
- Node version in Server or error stacks
- PM2/cluster hints in headers

Predicts: nosqli, prototype-pollution, massassign, ssrf on
fetch/axios sinks, jwt auth surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
