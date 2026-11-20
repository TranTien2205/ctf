# Tap: -z io,phs (protocol hierarchy)

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

Which protocols are present in the capture at all, with frames and bytes per
layer. Run it before writing any display filter — a filter for a protocol the
capture does not contain returns silence that looks like a negative.

## Command

```bash
tshark -r capture.pcapng -q -z io,phs
```

## Reading the output

One indented table: protocol name, frames, bytes, then parenthesised
percentage-of-parent. The indentation is the layer stack — `tcp` above `http`
above `data` means HTTP payloads TCP could not hand to a dissector show up as
`data`. A large `data` share under `tcp` is itself a tell: traffic the
dissectors did not recognise.

## Evidence rule

The table proves presence and volume per protocol, nothing more. It cannot
name which host sent to whom — that is `endpoints,ip` or `conv,tcp`.

## Trap

A port running a non-native service still lands under that port's protocol.
`tcp` port 53 carrying TLS shows up as `dns` frames only if a DNS dissector
accepted the payload; otherwise it is `data`. Presence proves parse, not
service.

## Pivot

If `io,phs` shows only `tcp`/`udp`/`tls` with no suspicious share, take the
class falsifier check in `../SKILL.md` seriously — quote the table as the
negative.
