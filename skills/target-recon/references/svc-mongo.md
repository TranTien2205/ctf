# Service recon: mongo

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

MongoDB wire protocol on 27017: binary handshake,
not text. nc returns binary garbage = the shape confirms it;
the hello/isMaster command needs a driver. Version surfaces in
the handshake response. A mongo port answering = route to the
nosqli/database depth, not web.
## Pivot

Signal harvested -> out-*; route named -> that skill.
