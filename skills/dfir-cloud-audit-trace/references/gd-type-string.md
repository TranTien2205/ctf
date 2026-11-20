# GuardDuty: Type string anatomy

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`ThreatPurpose:ResourceTypeAffected/ThreatFamilyName.DetectionMechanism!Artifact` - e.g. `Recon:IAMUser/MaliciousIPCaller.Custom`. The parts tell which purpose, which resource, which family, which mechanism.

## Evidence rule

A finding opens a window; the answer still comes from a quoted
CloudTrail or flow record inside it.

## Pivot

Window known -> back to `api-*` on the trail, or `vpc-*` on flows.
