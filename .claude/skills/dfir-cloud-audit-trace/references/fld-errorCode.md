# Field table: errorCode / errorMessage

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Absent = success; AccessDenied/Client.*/SignatureDoesNotMatch/InvalidClientTokenId/ExpiredToken - denied calls still record full requestParameters.

## Pivot

Field mapped -> the ev-* module for the call that carries it.
