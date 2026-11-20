# userIdentity: awsRegion on ConsoleLogin means little

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Root lands in us-east-1/us-east-2/us-west-2; an IAM user on the global endpoint lands in us-east-2/eu-north-1/ap-southeast-2 with an account-alias cookie, us-east-1 without - only a regional sign-in endpoint records where the user WAS. Do not geo-locate off it.

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
