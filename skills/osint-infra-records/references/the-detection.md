# Detection — when this class applies

A domain/host/cert is supplied and the answer lives in DNS,
registration, or certificate records.

## Signals

- The handout is a domain or an IP, not a file or a service.
- The question is "what's in the records" or "what hosts exist".
- A flag may be planted as a TXT string or a SAN hostname.
- Confusable: osint-identity-pivot (a handle, not a domain).

## Not this class

- A file's metadata → osint-media-metadata.
- A username/handle → osint-identity-pivot.
- A live web service → the web family.
Only when the answer IS the record does this class apply.

## First check

Is the handout a domain/IP/cert and the question records-shaped? Then this class; otherwise the sibling classes own it.

## The handout

A bare domain, an IP, or a cert — the records are the target. A service URL is recon first, web second.

## The question

Where the answer lives — a record value — is the test; a domain whose answer is elsewhere is recon.
