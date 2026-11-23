# Service recon: vault

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Vault 8200: /v1/sys/health = sealed/initialized/
version verbatim, /v1/sys/seal-status. A vault API answering
= secret-store surface; unauth posture visible on health.
Transit/KV mounts need auth - recon stops at identity.
## Pivot

Signal harvested -> out-*; route named -> that skill.
