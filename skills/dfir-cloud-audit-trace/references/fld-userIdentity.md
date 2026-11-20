# Field table: userIdentity block

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

type + principalId + arn + accountId + accessKeyId + sessionContext{sessionIssuer,attributes{mfaAuthenticated,creationDate},sourceIdentity} - the 'who' record.

## Pivot

Field mapped -> the ev-* module for the call that carries it.
