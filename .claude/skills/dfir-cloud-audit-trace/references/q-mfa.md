# Question: Question: did MFA hold

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

ConsoleLogin: additionalEventData.MFAUsed Yes/No + MFAIdentifier. API assumed-role: mfaAuthenticated=false is normal - the string trap. Entra: clientAppUsed legacy on success = MFA skipped.

## Answer shape

eventTime + eventName + the verbatim field the question asked for +
which artifact (trail/access log/flow) it was quoted from.

## Pivot

Question not in the cloud plane -> `cross-*` to the host or network
class.
