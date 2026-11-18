# Common Mistakes — the traps that burn a budget

## "The parser errored = XXE is live"

An `XMLSyntaxError`/`SAXParseException` proves a parser exists — it
says NOTHING about whether entities resolve. Half the hardening configs
error loudly on entities while refusing to expand them. The internal-
entity echo is the discriminator.

## "External entity didn't echo = no XXE"

External-entity resolution can be disabled while INTERNAL entity
expansion stays on (`&probe;` echoes but `SYSTEM`-entities don't) —
that's `external-parameter-entities`/`nonvalidating-load-external-dtd`
splits. Test each tier: internal → external-file → external-DTD → OOB.

## Sending blind-OOB first, getting nothing, quitting

OOB requires (a) entities expand (b) param-entities work (c) egress is
open (d) your listener is reachable. Each is a separate falsifier — the
in-band ladder (`workflow.md` rungs 1–2) isolates which one died. Blind
as rung 0 wastes a budget on a chain of unknowns.

## Using `&x;` for exfil instead of `%x;`

External content inside a GENERAL entity `&x;` gets re-parsed as content
— a file containing `<`/`&` breaks the doc. Param entities `%x;` in the
DTD can carry arbitrary content into a URI — that's why blind exfil
uses `%`.

## `file:///etc/passwd` on a Windows target

`file:///etc/passwd` returns empty on Windows — the correct first file
is `file:///c:/windows/win.ini` or `file:///c:/windows/system32/drivers/etc/hosts`.
A "no data" on a Linux path on a Windows box is NOT a dead class — it's
the wrong path. Fingerprint the OS first (`/proc/` vs `c:\`).

## Forgetting the parser's own fetch can be the vuln

`SYSTEM "http://internal/..."` = SSRF — the parser fetches — you don't
need content echo to have impact. People spend a budget trying to get
the echo when the fetch itself reaches the internal admin panel —
`ssrf-via-xxe.md`.

## Submitting a flag-shaped string that was in the DOCTYPE

If YOU put `flag{...}` in the entity URI or the DTD, its echo proves
your payload round-tripped — not that the flag was read. Only flag-
shaped strings that come from file content or an internal service
count — `evidence-rules.md`.

## Wrapping the whole payload in one giant entity

`xxe_gen.py --oob --file` emits the RIGHT shape; hand-rolled attempts
often build `<!ENTITY x SYSTEM "file:///flag">` then put `&x;` in a URL
— the file content lands inside the URL un-URL-encoded → spaces/newlines
break the URI → OOB never fires. The `%file;`-in-param-entity-with-
`%wrap;` pattern exists precisely to solve this — `blind-xxe.md`.

## Not checking `Content-Type` the endpoint expects

Sending `application/xml` to a form endpoint that reads `xml=` field —
the body never reaches the parser. Match the content-type the endpoint
actually consumes — `content-type-confusion.md`.

## Not counting a killed class

`DOCTYPE rejected` + `XInclude refused` + `no XML input surface left` =
a clean kill. Record it and move on — don't re-try the same payloads on
the same endpoint.
