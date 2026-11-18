# Workflow — the detection → exploit order

## Step 1 — the recon — is a proxy in the path?

`curl -v http://t/` — the `Via:`, `X-Forwarded-*`, `Server:` headers
name the front-end — a `Server: nginx` + `X-Backend-Server:` pair is
the proxy+backend — `ctf-shapes.md`.

## Step 2 — the fold test — does `%0d%0a` survive?

```bash
python3 tools/web/crlf_probe.py --url "http://t/?host={M}" --value "ex.com"
```

The fold-matrix — does a control character fold a header or a body —
the CRLF-injection test — `crlf-injection.md`.

## Step 3 — the desync test — does TE/CL disagree?

```text
POST / HTTP/1.1
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

The CL.TE timing probe — does it hang? `detection.md` — 3x repetition +
absent-on-control.

## Step 4 — the pair — CL.TE or TE.CL?

The timing probe identifies CL.TE (hang). The TE.CL probe is the
404-poison:

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /404-poison HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

Then a normal `GET /` — the response is the 404's → TE.CL — `desync-taxonomy.md`.

## Step 5 — the obfuscation — TE.TE if both honor TE

If both honor `chunked` → obfuscate ONE parser — `Transfer-Encoding:
cow` — the parser that falls back to CL is the desync — `obfuscation.md`.

## Step 6 — the exploit — what's behind the filter?

- the internal route — `GET /admin`, `GET /flag` — `internal-routes.md`
- the session-hijack — the smuggle's `Cookie:` takes the victim's —
  `session-hijack.md`
- the cache-poison — the smuggle's response caches — `cache-poison-via-smuggle.md`
- the upgrade-tunnel — `Upgrade: ws` + a smuggle inside a frame —
  `upgrade-smuggling.md`
- the h2-downgrade — `content-length`/`transfer-encoding` inside h2 —
  `http2-smuggling.md`

## Step 7 — the readback — the next request's response

The smuggle's output goes to the NEXT request — self-poison or the
stored-param readback — `response-poisoning.md`.

## Step 8 — the flag — the verbatim excerpt

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

## The budget — 5 probes / 15 min per mechanism class

A spent budget escalates: `chain_match` → `reclassify` →
`writeup_search` → `novel_plan` → `fanout_sweep` → `solver_handoff` —
each recorded with `state.py --strategy-used <rung>`.

## The common ordering mistake — exploiting before detecting

Don't craft the smuggle before the desync pair is identified — the
pair determines whether the smuggle is `GET /admin` (TE.CL) or a
prefix-fragment (CL.TE) — detect first, then exploit.
