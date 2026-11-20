# Question: Question: logging tampered

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

DeleteTrail / StopLogging / UpdateTrail / PutEventSelectors(0) / DeleteLogGroup / DeleteLogStream - the anti-forensics calls land in the trail itself until they succeed; the gap after them is the second half of the answer.

## Answer shape

eventTime + eventName + the verbatim field the question asked for +
which artifact (trail/access log/flow) it was quoted from.

## Pivot

Question not in the cloud plane -> `cross-*` to the host or network
class.
