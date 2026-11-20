# Multiple domains — a batch

Several related domains (same registrant/NS) — query each; a flag
planted in one sibling's TXT while the others are clean is the
pattern.

## Finding siblings

- whois registrant/contact — the shared email.
- Shared nameservers — domains on the same NS.
- crt.sh — other domains on the same SAN or issuer pattern.
Each sibling gets the full sweep.

## The sweep per domain

Each sibling gets the full first-three queries — a flag planted in one sibling while others are clean is the pattern.
