# Negative results — recording the CORS gates that held

Every gate that held is a measured negative — record it with the
evidence so the next pass doesn't re-walk it.

---

## 1. The `*` on a sensitive endpoint — not the vuln

```text
a `*` on /api/me reads public data only — the browser rejects `*`+
credentials. record: 'ACAO:* on sensitive endpoint — public read —
not-exploitable' — a class-negative, not a candidate.
```

## 2. The non-credentialed read — ACAC absent

```text
a reflected/allowed ACAO but no ACAC → the cookie doesn't ride →
a non-credentialed read of public data. record: 'ACAO allowed,
ACAC absent — non-credentialed only'.
```

## 3. The SameSite-gated cookie — the credential doesn't attach

```text
a SameSite=Lax/Strict cookie doesn't ride a cross-site fetch — the
read is non-credentialed regardless of ACAO. record: 'cookie
SameSite=Lax — doesn't attach cross-site'.
```

## 4. The strict allowlist — no origin bypass

```text
an exact-match allowlist — no reflect/null/lookalike/subdomain
bypass. record: 'ACAO fixed-allowlist — no bypass — closed'.
```

## 5. The preflight-blocked request — a custom-header dead end

```text
the preflight's ACAM/ACAH doesn't allow your method/header → the
request never fires. record: 'preflight denied — custom header
blocked'.
```

## 6. The public-data endpoint — nothing sensitive to read

```text
the CORS read works but the endpoint returns public/nonsensitive
data — no flag. record: 'read works — endpoint returns public data'.
```

## 7. The `*+ACAC` invalid combo — the rejected request

```text
ACAO:* + ACAC:true → the browser rejects — a failed request, not a
vuln. record: '*+ACAC — invalid combo — rejected'.
```

## 8. The non-CORS endpoint — no ACAO at all

```text
no ACAO on the response — the browser blocks the read — not the
CORS class. record: 'no ACAO — not CORS-open'.
```

## 9. The alternate-read dead-end — no JSONP/ws/postMessage

```text
CORS closed AND no JSONP endpoint, no ws channel, no postMessage
broadcast — the read surface is closed. record: 'no alternate-read
channel — CORS surface dead'.
```

## 10. The bot-reachability negative — the exfil can't leave

```text
the read works but the bot can't reach the listener AND no
write-back/postMessage readback exists — the exfil is blocked.
record: 'read works — exfil unreachable — airgapped bot'.
```

## 11. The per-negative ledger rows

```bash
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-cors --evidence-kind class \
  --evidence 'ACAO:* — public read — not the vuln' \
  --response '<the headers>'

python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-cors --evidence-kind class \
  --evidence 'ACAO fixed-allowlist — no bypass' \
  --response '<the headers>'
```

## 12. The falsifier ledger — the 'closed' record

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-closed: ACAO fixed + no bypass + no alternate channel — pivot"
```

## 13. The kill-map entries — what was measured dead

```json
{"layer":"cors-aco","status":"closed","evidence":"fixed-allowlist,no bypass","reopen":"a lookalike or null passes"}
{"layer":"cors-acac","status":"closed","evidence":"ACAC absent — non-credentialed","reopen":"ACAC appears on a retry"}
{"layer":"cors-cookie","status":"closed","evidence":"SameSite=Lax","reopen":"a non-cookie credential exists"}
{"layer":"jsonp","status":"closed","evidence":"no callback param","reopen":"a JSONP endpoint found"}
{"layer":"ws","status":"closed","evidence":"no ws endpoint","reopen":"a ws channel found"}
```
