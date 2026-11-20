# Shimcache proves presence, never execution

The insert flag's 0x2 bit "tracked execution" in testing but
mandiant's own parser README says its purpose is unknown and must
not conclusively determine execution; Win10 has no flag. Written at
shutdown — a live capture can lack the newest entries.

## Presence

Path seen — the insert flag is not execution.

## Shutdown

Written at shutdown — live hives lack newest.
