# Service recon: cassandra

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Cassandra 9042: CQL binary protocol - a
plaintext probe gets protocol errors; cqlsh needed for real
intake. 9160 thrift (deprecated) or JMX 7199 adjacent. The
cluster name surfaces via JMX or system.local. Protocol
identification only in recon.
## Pivot

Signal harvested -> out-*; route named -> that skill.
