# S3: S3 log Time field

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`[%d/%b/%Y:%H:%M:%S %z]` UTC inside brackets - the reason a space split fails. Parse with `re.findall(r'\[[^\]]*\]|"[^"]*"|\S+', line)` - measured here: naive split gives 30 tokens on a real line, the regex gives 27.

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
