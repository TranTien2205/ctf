# Recovery: trail gap

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Records stop mid-window: StopLogging/DeleteTrail/UpdateTrail/PutEventSelectors rows BEFORE the gap are the cause record; GuardDuty/Insight rows may still cover the gap; host-side evidence fills the rest.

## Rule

A recovery module names the fallback artifact when the primary store
is gone or degraded - the fallback record is still quoted verbatim.

## Pivot

Recovery exhausted -> `../dfir-antiforensics-trace/` for the
destroyed-artifact matrix.
