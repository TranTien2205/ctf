# S3: Data events off by default

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

'By default, trails and event data stores do not log data events' (AWS, Logging data events) - an ABSENT GetObject in CloudTrail is not evidence nothing was read. Data events carry eventCategory=Data and resources.type AWS::S3::Object when on; otherwise the server access log is the only object-read record.

## Parse

```bash
python3 -c "import re,sys
for l in sys.stdin:
    f = re.findall(r'\[[^\]]*\]|"[^"]*"|\S+', l)
    if len(f) >= 12: print(f[5], f[6], f[7], f[11])" < s3.log
```

## Evidence rule

Quote the Operation + Key + Requester fields verbatim; a byte sum is
derived, name the fields it summed.

## Pivot

S3 quiet -> `vpc-*` for the wire, `api-*` for the control plane.
