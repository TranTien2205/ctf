# IoT/embedded recon: snmpwalk

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SNMP on embedded: sysDescr = full device
identity, sysObjectID = model OID, interface tables = network
topology, running-config communities on some gear. UDP -
one get request each for sysDescr/sysObjectID/sysName.
## Pivot

Signal harvested -> out-*; route named -> that skill.
