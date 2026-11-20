# A blank 4688 CommandLine is policy, not a miss

"By default Process Command Line field is empty" (Microsoft Learn) —
the policy `ProcessCreationIncludeCmdLine_Enabled` fills it.
Substitutes: Sysmon 1, 4104, classic 400 `HostApplication`, prefetch,
Amcache, PSReadLine history.

## Policy

Empty by default — the substitutes carry it.

## The substitutes

Sysmon 1, 4104, 400, prefetch, Amcache, history.
