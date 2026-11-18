# Attack-Defense XXE — the contest-mode angle

## Where XXE appears in attack-defense

An XML-parsing service — a SOAP API, an XML-RPC endpoint, a config
importer, a report-generator, an order/inventory XML path — the
"the service speaks XML" shape.

## The service-recon — find the XML surface

```
GET / HTTP/1.1          — is there an XML endpoint?
?wsdl                   — SOAP
/xmlrpc.php             — XML-RPC
/saml                   — SAML
POST text/xml           — does text/xml get parsed?
POST application/xml
POST image/svg+xml      — upload surface
```

Map the XML input first — the AD clock favors a known-parse.

## The flag-read — AD flags are usually short and local

```
file:///flag
file:///flag.txt
file:///home/ctf/flag
file:///app/flag
file:///var/flag
file:///proc/1/environ    — docker-injected FLAG env
```

The AD flag is usually a file in a known spot or an env var — the
short ladder.

## The flag-rotation — the flag moves every tick

AD flags rotate — the file/env reads once isn't enough — build a
repeatable read: a `xxe_gen.py --file /flag`-style one-liner the
farm script replays each tick — `tools/ad/` context.

## The "the service's own XML is the attack surface" — XXE-as-attack

Your exploit sends the XXE payload; their service parses it → the
flag is in the response — the standard jeopardy chain applied to a
scored service.

## The "the traffic shows the shape" — `traffic_mine`

`tools/ad/traffic_mine` replays captured XXE traffic — a working
`file:///` read visible in the capture is a farm-ready replay — the
learned-shape problem AD poses.

## The patch — how defenders kill XXE

- `disallow-doctype-decl` / `DtdProcessing.Prohibit`
- `resolve_entities=False` / `libxml_set_external_entity_loader`
- strip DOCTYPE / reject `text/xml`
- `setXIncludeAware(false)` / `.nonet`
- egress-filter outbound

Patching your own service against XXE = kill the entity config —
`hardening-configs.md`.

## The patch-check — `--compare` the SLA

`tools/ad/sla_check --compare` — the patch that killed XXE must not
break the service's own health-checks — a service that NEEDS XML
(e.g. SOAP) can't just reject `text/xml` — patch the parser config,
not the transport.

## The "the XXE was a cover" — the deeper bug

A service with XXE often has more — a deserializer, a file-write, a
template — the XXE is the beachhead — once read is proven, pivot to
the source-read → the bigger bug.

## The "your own service has XXE" — defending

If YOUR service parses XML — check the parser config NOW —
`hardening-configs.md` — a default-live config is the attack your
opponents will find. Patch before flag-stealing starts.

## The "the XXE is the SLA check" — the self-test

Your checker probes the service — if the checker sends an XML probe,
the checker's own XXE is a health-signal — `sla_check` baseline.

## Record — the AD-ledger shape

- which endpoint, which entity-tier, which flag-path, per tick
- the replay command — the farm's repeat payload
- the patch applied + the `--compare` result
