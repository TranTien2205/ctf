# CloudTrail: eventSource values

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

iam.amazonaws.com (identity changes), signin.amazonaws.com (ConsoleLogin), sts.amazonaws.com (GetCallerIdentity/AssumeRole), s3.amazonaws.com (bucket ops; object ops only with data events on), plus ec2/lambda/secretsmanager/kms/cloudtrail etc - the source names which service recorded it.

## Query

```bash
find . -name '*.json.gz' -exec gzip -dc {} + | jq -r '.Records[] |
  [.eventTime, .eventName, .eventSource, .sourceIPAddress,
   (.errorCode // "-")] | @tsv' | sort
```

## Evidence rule

Quote the record - field name plus verbatim value. 'A suspicious call'
is surface; `eventName=CreateAccessKey` on a quoted row is class
evidence.

## Pivot

Envelope mapped -> userIdentity (`ui-*`) for who, then `api-*` for the
action pattern.
