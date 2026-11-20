# ioc_scan.py output — anatomy

- Strings ≥ --min, with byte offsets.
- IOC pass: paths, URLs, IPs, domains, emails, flag tokens.
- --utf16 for wide strings; --pattern for a custom regex;
  --strings-only to skip the IOC pass.
Offsets give provenance — where in the image it lived.
