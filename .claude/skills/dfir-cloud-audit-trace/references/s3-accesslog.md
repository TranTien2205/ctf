# S3: S3 server access log

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Space-delimited lines, 27 fields (AWS, S3 server access log format): Bucket Owner, Bucket, Time, Remote IP, Requester, Request ID, Operation, Key, Request-URI, HTTP status, Error Code, Bytes Sent, Object Size, Total Time, Turn-Around Time, Referer, User-Agent, Version Id, Host Id, Signature Version, Cipher Suite, Authentication Type, Host Header, TLS version, Access Point ARN, aclRequired, Source region.

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
