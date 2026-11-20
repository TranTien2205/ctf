# S3: A copy writes TWO records

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

REST.COPY.OBJECT_GET + REST.COPY.OBJECT_PUT - summing Bytes Sent over a copy double-counts it. For exfil volume, sum the GET side only.

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
