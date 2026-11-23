# Service recon: influxdb

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

InfluxDB 8086: /ping returns 204 + X-Influxdb-
Version header = identity without auth; /query?q=SHOW+
DATABASES unauth posture; /debug/pprof when enabled. The
query endpoint = the data surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
