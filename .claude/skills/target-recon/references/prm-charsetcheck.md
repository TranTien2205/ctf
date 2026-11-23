# Param-level recon: charsetcheck

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Per-param charset check: which special chars
survive - quotes, angle brackets, backslashes, null bytes,
unicode, CRLF, template delimiters? Rejected vs escaped vs
raw-passed is the sanitizer picture per param - the
sanitizer_fuzz input list builds directly from this
recon.
## Pivot

Signal harvested -> out-*; route named -> that skill.
