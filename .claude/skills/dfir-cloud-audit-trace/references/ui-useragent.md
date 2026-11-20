# userIdentity: userAgent as tooling tell

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`aws-cli/2.x Python/3.x Linux/...`, `console.amazonaws.com`, SDK identifiers (`Boto3/`, `aws-sdk-java/`), or a browser UA - the tool the operator drove. cli session name + cli userAgent + cli accessKey is the coherent intruder shape.

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
