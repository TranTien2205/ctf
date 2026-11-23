# Service recon: gitlab

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

GitLab/Gitea web: /users/sign_in, /api/v4/version
(auth returns version verbatim when unauth allows),
/explore public repos = source-surface recon (leaked configs,
keys in public code). Gitea :3000 with similar API.
Register-open posture = account surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
