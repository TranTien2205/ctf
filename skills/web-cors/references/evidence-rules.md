# Evidence rules — the CORS proof standard

A CORS `confirms` needs a credentialed cross-origin READ of
sensitive data — not "the ACAO header reflected". The bar.

---

## 1. The confirms bar

```text
a `confirms` verdict needs:
- an ACAO that allows YOUR origin (reflected, null, or bypassed)
- ACAC:true (credentials allowed) — for a credentialed read
- the actual read working — the sensitive data exfiltrated
NOT:
- "ACAO reflected" alone — that's a candidate, not the read
- "ACAO:*" on a sensitive endpoint — no credentials, a public read
- a theoretical shape with no exfil evidence
```

## 2. The candidate-vs-confirm split

```text
candidate — ACAO reflected/null/bypassed + ACAC:true — the READ is
            possible; a strong candidate, not yet a confirm.
confirms — the actual cross-origin read of session data happened
            and exfiltrated to you.
```

## 3. The `*` falsifier — a common false-confirm

```text
ACAO:* + ACAC:true → the browser REJECTS — no credentialed read.
a `*` on a sensitive endpoint is NOT exploitable — it's a public
read of data anyone can fetch. record 'not-exploitable'.
```

## 4. The SameSite falsifier — the cookie doesn't ride

```text
a reflected ACAO + ACAC BUT the session cookie is SameSite=Lax/
Strict → the fetch doesn't attach it → a non-credentialed read —
reads public data only. not the vuln unless a non-cookie credential
exists.
```

## 5. The exfil evidence — the read's proof

```text
the exfil is the readback: the data arrives at YOUR listener. the
hit on oob_listener is the live evidence:
python3 tools/web/oob_listener.py hits
the response body/params contain the exfiltrated data.
```

## 6. The preflight-vs-actual split — a measured divergence

```text
a permissive preflight that lets the request fire vs a strict
actual-response check — record which held. a strict preflight that
blocked the request is a refutes for that shape; a simple-request
bypass is a separate test.
```

## 7. The flag rule

```bash
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /x?d=...' --evidence '<the oob hit body>'
# the flag read from a live exfil — not a guess or a static string
```

## 8. The negative-result recording

```text
each gate that held → a refutes with evidence:
- 'ACAO fixed-allowlist, no bypass' 
- 'ACAC absent — no credentialed read'
- 'SameSite=Lax — the cookie doesn't ride'
- 'the endpoint returns public data — nothing sensitive'
- 'strict preflight + no simple read'
```

## 9. The attribution — was it YOUR read?

```text
the exfil data must be attributable — the specific endpoint's data
arriving on your listener, not ambient noise. a marker in the read
(a unique field) attributes it.
```

## 10. The ledger template

```bash
# candidate
python3 tools/state.py <c> --hypothesis \
  "candidate: ACAO reflected + ACAC on /api/x"
# confirms
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-cors --evidence-kind impact \
  --evidence 'read /api/me cross-origin; data exfiltrated' \
  --response '<the exfil hit>'
# refutes
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-cors --evidence-kind class \
  --evidence 'ACAO fixed-allowlist, no bypass' --response '<headers>'
```
