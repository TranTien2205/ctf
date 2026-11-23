# Class recheck: parser

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-parser-differential needs:
proxy/proxy+app pairs visible (headers from two stacks),
trusted-header posture (x-forwarded-* honored? which?),
normalization differences (path encoding, header casing,
duplicate headers accepted), and the fallback behavior when
the front's header is stripped.
## Pivot

Signal harvested -> out-*; route named -> that skill.
