# CloudTrail: Bounding the window

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

eventTime is UTC seconds. The earliest record is a floor set by when the trail started - say 'first RECORDED action', never 'first action'. The trail's own delivery lag (minutes) means the last record is not 'the last thing that happened' either.

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
