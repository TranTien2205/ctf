# CloudTrail: Core record fields

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`eventTime` (UTC seconds, `2023-07-19T21:44:40Z`), `eventName` (the API action), `eventSource` (the service - iam/signin/sts/s3 .amazonaws.com), `awsRegion` (where the call landed), `sourceIPAddress`, `userAgent`, `errorCode`/`errorMessage`, `requestParameters`/`responseElements` (null when readOnly).

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
