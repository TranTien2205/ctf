# Path enum: debugsurfaces

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Debug-surface probes: /debug /_debug /trace
/__debug__/ /actuator /metrics /console /elmah.axd /server-status
/server-info /_profiler /telescope. Any 200 here = high-value
surface: request logs, config, stack, heap - record which one
answered with its verbatim status and a response excerpt.
## Pivot

Signal harvested -> out-*; route named -> that skill.
