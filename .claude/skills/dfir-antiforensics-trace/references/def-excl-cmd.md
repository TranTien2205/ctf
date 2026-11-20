# Defender: Exclusion command signatures

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Hunt CommandLine/4104 for `Add-MpPreference -ExclusionPath`, `-ExclusionProcess`, `-ExclusionExtension`, `Set-MpPreference -DisableRealtimeMonitoring $true`, `-DisableBehaviorMonitoring`, `-DisableIOAVProtection`, `reg add ...Defender\Exclusions`. The command names who did it when the registry write's attribution is gone.

## Evidence rule

Defender events carry few fields — quote the message text and the event id
together; the symbolic name is documentation, the message is the record.

## Pivot

Defender channel empty -> MPLog + quarantine (`qar-*`) still hold the
evidence; exclusions still live in the hive.
