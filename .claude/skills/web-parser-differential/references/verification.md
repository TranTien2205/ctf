# Verification — proving the parser-differential reach, and the readback

The proof discipline — the differential confirm, the bypass evidence, the readback.

---

## 1. The differential confirm — the proof

```bash
# the card's first confirming probe — a normal request then a stripped request
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/restricted" -d 'data'
#   a 401/403 — the normal request is gated
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/restricted" -d 'data' \
  -H 'Connection: keep-alive, X-Real-IP'
#   a 200 — the stripped request reached → the differential confirmed
```

## 2. The bypass evidence — the response bytes

```text
a differential confirmed → the bypass's evidence is the response —
a 200 on the gated route — the check bypassed — the route reached —
the response's bytes carry the route's output.
```

## 3. The readback — the downstream read

```bash
# the readback — the downstream's effect read back
python3 tools/web/http_probe.py --method POST --url "$BASE/api/restricted" \
  --body 'data' --header 'Connection: keep-alive, X-Real-IP' --save
#   the response carries the restricted route's output — the bypass's
#   reach — the downstream's read
```

## 4. The differential's falsifier — the dead path

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```

## 5. The differential's falsifier — a proxy that doesn't strip

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
→ the proxy's header stays → a different class.
```

## 6. The differential's falsifier — a proxy that strips the client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails → the hop-by-hop bypass is the vector.
```

## 7. The differential's falsifier — a proxy that verifies

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails → the hop-by-hop
bypass is the vector.
```

## 8. The differential's falsifier — a non-header check

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 9. The differential's falsifier — the same parse

```text
the proxy and the app normalize the same way → no confusion → a
different class.
```

## 10. The differential's falsifier — a stored copy

```text
a stored copy that serves YOUR input → a cache-poisoning (a store) →
not a parser-differential (a parse).
```

## 11. The differential's falsifier — a desync

```text
a front-end and a back-end that parse the request boundary differently
→ a request-smuggling (a desync) → not a parser-differential (a parse).
```

## 12. The differential's falsifier — a non-parser read

```text
a fetch that reads bytes → web-cors (a real read) → not a parser-
differential.
```

## 13. The verification's evidence — the response bytes

```text
the verification's evidence is the response bytes — a 200 on the gated
route — the check bypassed — the route reached — the downstream's
read — the response's bytes carry the route's output.
```

## 14. The verification's falsifier — a false positive

```text
a false positive — a 200 on a non-gated route — the route wasn't gated
→ a different class.
```

## 15. The verification's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
