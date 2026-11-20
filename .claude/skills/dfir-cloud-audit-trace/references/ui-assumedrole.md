# userIdentity: AssumedRole sessions

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`.userIdentity.arn` = `arn:aws:sts::<a>:assumed-role/<role>/<sess>` - the LAST segment is the session name (frequently the answer). `.userIdentity.userName` is ABSENT; it lives at `.sessionContext.sessionIssuer.userName`. Measured jq: `.userIdentity.arn | split("/") | last` -> `cli-session`.

## Query

```bash
jq -r '.Records[] | select(.userIdentity.type=="AssumedRole") |
  [.eventTime, (.userIdentity.arn | split("/") | last),
   .userIdentity.sessionContext.sessionIssuer.arn,
   .userIdentity.sessionContext.attributes.mfaAuthenticated] | @tsv'
```

## Evidence rule

The principal comes from userIdentity, never sourceIPAddress alone -
an IP is network evidence, the identity claim needs the arn/key record.

## Pivot

Identity mapped -> `api-*` for the action pattern on that identity.
