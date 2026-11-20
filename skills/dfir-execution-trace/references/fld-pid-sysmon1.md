# ProcessId on Sysmon 1

**Field:** ProcessId — OS PID, reused, never the join.

**Artifact:** Sysmon 1 — execution + cmdline + parent + hash.

The field's presence/absence is itself evidence — a blank CommandLine is policy, not a missing record.
