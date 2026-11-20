# ProcessGuid, not PID — the join rule

`ProcessGUID` is "a unique value for this process across a domain"
(Microsoft Learn) — Sysmon emits it precisely because Windows reuses
PIDs. A PID join attaches a later process's connection to an earlier
process's creation. The same GUID is on Sysmon 3, 5, 7, 8, 10, 11,
12/13 and 22 — the chain is Sysmon 1 -> ProcessGuid -> Sysmon 3/11/22.

## The rule

GUID, not PID — reuse attaches the wrong connection.

## The set

The same GUID on 3,5,7,8,10,11,12/13,22.
