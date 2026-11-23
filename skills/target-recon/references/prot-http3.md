# Protocol recon: http3

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

HTTP/3 (QUIC): Alt-Svc: h3=... header announces it;
the QUIC port is UDP - recon records the alt-svc verbatim,
the HTTP/1.1+2 surface remains the working target unless the
challenge is specifically QUIC.
## Pivot

Signal harvested -> out-*; route named -> that skill.
