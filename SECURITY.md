# Security and authorisation

This repository contains an offensive security toolkit and a deliberately
vulnerable test fixture. Both are for authorised testing only.

## The fixture

`test/fixtures/vulnapp.py` plants one weakness per vulnerability class so the
proof matrix can be exercised offline. It binds 127.0.0.1 only. Do not deploy it,
do not expose it on a routable interface, and do not reuse its code.

## What the system refuses by construction

- no shell: every tool is an argv list
- no target outside the declared scope; an empty scope allows nothing
- no denial of service: the proof would be the damage
- no persistence, lateral movement, credential dumping or exfiltration
- code execution is demonstrated with `id; echo <nonce>` and stops there
- the intrusive risk tier will not open without an authorisation note naming who
  authorised the engagement and over what window

## Reporting a problem in this code

Open an issue describing the class of problem and how to reproduce it. Do not
include a working exploit against a third party, and do not include evidence
from a real engagement.
