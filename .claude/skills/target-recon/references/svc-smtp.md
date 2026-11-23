# Service recon: smtp

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SMTP banner: 220 <hostname> ESMTP <server version>.
VRFY <user> and EXPN - user enumeration oracles when enabled
(550 vs 252 vs 250). EHLO response lists supported extensions
= server capability map. A CTF mail port is usually a
user-enum or message-content surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
