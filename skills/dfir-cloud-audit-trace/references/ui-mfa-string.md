# userIdentity: mfaAuthenticated is a STRING

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`"false"` on a role session proves nothing: AWS documents it false by design for federated/assumed-role requests; true only for an IAM user or root with MFA. Do not report 'MFA bypassed' off an assumed-role `mfaAuthenticated=false`.

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
