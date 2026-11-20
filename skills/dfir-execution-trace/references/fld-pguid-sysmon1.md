# ProcessGuid on Sysmon 1

**Field:** ProcessGuid — the join key, PID-reuse safe.

**Artifact:** Sysmon 1 — execution + cmdline + parent + hash.

The field's presence/absence is itself evidence — a blank CommandLine is policy, not a missing record.
