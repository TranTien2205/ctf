# CloudTrail: Decompressing a whole trail

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`find . -name '*.json.gz' -exec gzip -dc {} +` - NOT `zcat CloudTrail/**/*.json.gz`: `**` needs `globstar` in bash and silently matches one level without it. Count records not files: `jq -r '.Records | length' | paste -sd+ | bc`.

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
