# CTF-specific recon: flagpathhints

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Flag-path hints during recon: /flag /flag.txt
/robots.txt disallowed paths, 'flag' strings in JS/comments/
headers, env vars named FLAG*, a /admin route that clearly
gates it. Recon names WHERE the flag likely lives - reaching
it is the depth skill's chain.
## Pivot

Signal harvested -> out-*; route named -> that skill.
