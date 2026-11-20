# Class boundaries

- A handle/username → osint-identity-pivot.
- A media/doc file → osint-media-metadata.
- The live service's web answer → the web family.
- Only DNS/registration/cert records → this class.

## The distinction

This class is records extraction — the answer IS a DNS record, a
whois field, or a SAN. When the records merely point to a live
service whose answer is a web flag, the records are recon and the
web family owns the exploit.

## The hand-off

- The record IS the flag → stay here.
- The record names a host whose flag is web-side → the records
  were recon; classify the web answer next.
- The question is an identity/handle → osint-identity-pivot.

## Staying in class

A domain whose answer is literally a record value stays here; a domain that leads to a web service hands off — the record was recon.

## The hand-out

The question decides: a record-shaped question stays; a service-shaped question hands off to web.
