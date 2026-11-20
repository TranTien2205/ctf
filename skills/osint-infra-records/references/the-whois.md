# whois — the registration

    python3 tools/dns_query.py --whois <domain>

Registrar, creation/expiry dates, nameservers, the contact
pattern — the operator identity and sibling domains.

## What to read

- Registrar + creation/expiry — age and operator.
- The nameservers — match against a sibling's NS.
- Registrant/contact — privacy-protected or a real pattern.
- A repeated registrant email links sibling domains.

The whois is read-only; the answer is the pattern, not one field.

## The follow-up

A registrant email or a shared NS links sibling domains — query each sibling's records; the operator pattern widens the target.

## What it is not

whois names registration, not content — a whois answer is operator/history data, rarely the flag itself.
