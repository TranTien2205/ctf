# Signature: Add/Set-MpPreference exclusions

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`Add-MpPreference -ExclusionPath/-ExclusionProcess/-ExclusionExtension/-ExclusionIpAddress`; `Set-MpPreference -DisableRealtimeMonitoring $true -DisableBehaviorMonitoring -DisableIOAVProtection -DisableScriptScanning` — 5007 New value strings name the changed path.

## Where it fires

Sysmon 1 CommandLine, Security 4688 CommandLine, PowerShell 4104 script
blocks, PSReadLine history, Amcache/Shimcache execution evidence.

## Evidence rule

A signature match is a candidate: quote the command line verbatim, then
pair it with the resulting artifact change (clear event, exclusion key,
journal pattern) before reporting tampering.

## Pivot

Signature seen without the artifact change -> inconclusive; artifact
change without signature -> hunt the API/service route.
