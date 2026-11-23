# Service recon: snmp

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SNMP: UDP 161 - community 'public'/'private' GET on
sysDescr.0 returns the device description = vendor+model+OS
verbatim. snmpwalk needs the community; the two defaults are
the documented check. Embedded/network-gear targets.
## Pivot

Signal harvested -> out-*; route named -> that skill.
