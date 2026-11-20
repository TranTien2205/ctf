# Signature: timestomp / SetFileTime tooling

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Meterpreter `timestomp`, `SetFileTime` API calls, `(Get-Item X).CreationTime = '...'` PowerShell property sets, `touch -d`/`-t` on POSIX. The PowerShell property-set is the commonest scripted form.

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
