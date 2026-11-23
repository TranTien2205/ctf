# Service recon: postgres

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

PostgreSQL: startup needs a client handshake;
the ErrorResponse on a wrong-user attempt carries the server
version field verbatim. SSLRequest probe tells whether TLS is
supported. A postgres port + a web app = the DB the sqli
skill assumes exists.
## Pivot

Signal harvested -> out-*; route named -> that skill.
