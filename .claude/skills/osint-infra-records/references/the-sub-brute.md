# Subdomain brute-force

When AXFR fails: a wordlist against the domain — but the wildcard
trap inflates it; confirm each found name resolves to a real,
distinct answer.

## The method

- A common-subdomains wordlist against `<name>.<domain>`.
- Detect the wildcard first (a random name resolving).
- Confirm each hit is distinct — different IP/records from the
  wildcard's answer.
crt.sh SANs usually beat brute-forcing — try it first.
