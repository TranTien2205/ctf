# CloudTrail: CloudTrail envelope shape

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

One gzip member = one JSON object, one key `Records`, an array (AWS, CloudTrail record contents). File name `<acct>_CloudTrail_<region>_<YYYYMMDD>T<HHmm>Z<rand>.json.gz` under `AWSLogs/<acct>/CloudTrail/<region>/<Y>/<M>/<D>/`; `AWSLogs/<O-ID>/` for an org trail; siblings `CloudTrail-Insight`, `-NetworkActivity`, `-Aggregated`.

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
