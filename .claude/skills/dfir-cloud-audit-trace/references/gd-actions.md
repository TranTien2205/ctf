# GuardDuty: action.actionType values

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`awsApiCallAction` (`.api`, `.remoteIpDetails.ipAddressV4`), `dnsRequestAction` (`.domain`), `networkConnectionAction`, `portProbeAction` - the action type names which evidence field carries the observable.

## Evidence rule

A finding opens a window; the answer still comes from a quoted
CloudTrail or flow record inside it.

## Pivot

Window known -> back to `api-*` on the trail, or `vpc-*` on flows.
