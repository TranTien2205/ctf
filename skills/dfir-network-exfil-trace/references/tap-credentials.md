# Tap: -z credentials

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

Cleartext credentials the dissectors recognised: FTP USER/PASS, HTTP Basic,
SMTP AUTH, telnet, SNMP communities and friends, printed with frame and
protocol.

## Command

```bash
tshark -r capture.pcapng -q -z credentials
```

## Reading

Each line names the protocol, the packet, and the credential pair as
dissected. For an exfiltration question this answers "did a credential leave
in cleartext" — a different question than "did data leave", so name which you
answered.

## Evidence rule

Quote the credential line verbatim but mask nothing — the bytes are the
evidence. Note which dissector produced it; a credential inside a tunnelled
or encrypted session never reaches this tap.

## Trap

Only recognised protocols parse. Credentials inside a custom binary protocol,
a TLS session, or a base64 body the dissector does not decode are invisible
here — absence is a coverage fact, not proof none left.

## Pivot

Found credential -> `dfir-authentication-trace` for where it was used;
credential inside HTTP -> `chan-http-post-*`.
