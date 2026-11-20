# userIdentity: HIDDEN_DUE_TO_SECURITY_REASONS

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

A mistyped username records `userName` as `HIDDEN_DUE_TO_SECURITY_REASONS` - a literal VALUE in the record, not a redaction to undo. It still counts as a failed login attempt against the account.

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
