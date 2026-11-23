# Handoff format: negativerecord

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Negative record format: <target>: <what
was tried> -> <result> [reopen-if]. Example - /.git/HEAD:
GET -> 404 [reopen-if vhost differs]. A recorded negative
stops the same probe re-running and says what changes it.
## Pivot

Signal harvested -> out-*; route named -> that skill.
