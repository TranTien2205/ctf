# S3: Error Code field semantics

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

HTTP status + S3 Error Code columns pair (403 + AccessDenied, 404 + NoSuchKey) - a 403-run on many keys is the key-probing shape; `-` fields are normal in either column.

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
