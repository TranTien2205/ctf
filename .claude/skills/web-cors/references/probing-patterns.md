# Probing patterns — the systematic measurement of a CORS surface

The ordered sequence of probes that fully characterizes a target's
CORS posture — each probe's input, the measurement, and the verdict
it produces.

---

## Probe 1 — the baseline — what does the endpoint return

```bash
# the unauthenticated baseline
curl -s -i "$BASE/api/me" | head -20
# the authenticated baseline
curl -s -i -b "$CJ" "$BASE/api/me" | head -20
# the difference → the session-scoped data
```

**Measures**: whether the endpoint's response changes with the session.
**Verdict**: a session-scoped response → a read target exists.

## Probe 2 — the foreign-Origin replay — the central measurement

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-(allow-origin|allow-credentials)|vary'
```

**Measures**: does a foreign Origin change the ACAO.
**Verdicts**: reflected → open; `*` → public; fixed → closed; absent → not CORS.

## Probe 3 — the credential-gate — does the cookie ride

```bash
# ACAC present?
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-credentials'
# the cookie's SameSite
curl -s -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
```

**Measures**: ACAC + the cookie's SameSite.
**Verdicts**: ACAC:true + SameSite=None+Secure → credentialed read; else → limited.

## Probe 4 — the `null`-Origin probe — the opaque-origin check

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: null' | \
  grep -i 'access-control-allow-origin'
```

**Measures**: is 'null' in the allowlist.
**Verdicts**: ACAO:null → an opaque-origin read works.

## Probe 5 — the lookalike battery — the check-shape

```bash
for o in 'https://target.com.evil.com' 'https://eviltarget.com' \
         'https://evil-target.com' 'https://sub.target.com'; do
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

**Measures**: which lookalike passes → the check-shape.
**Verdicts**: prefix/suffix/substring/subdomain → a bypassable check.

## Probe 6 — the URL-parse battery — the confusion check

```bash
for o in 'https://target.com@evil.com' 'https://evil.com?target.com' \
         'https://evil.com#target.com' 'https://target.com%2eevil.com'; do
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

**Measures**: a URL-parse or decode-order bug.
**Verdicts**: a confusion-origin that passes → the check is naive.

## Probe 7 — the preflight probe — the non-simple gate

```bash
curl -s -i -X OPTIONS "$BASE/api/me" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token' | \
  grep -iE 'access-control-allow-(origin|methods|headers|credentials)'
```

**Measures**: the preflight's permission.
**Verdicts**: permissive → non-simple reads work; strict → simple only.

## Probe 8 — the `Vary` probe — the cache check

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://a.com' | grep -i 'vary'
```

**Measures**: is the response per-origin.
**Verdicts**: `Vary: Origin` → clean; no Vary → a cache-poison surface.

## Probe 9 — the JSONP probe — the alternate read

```bash
curl -s -b "$CJ" "$BASE/api/me?callback=x" | head -1
```

**Measures**: is the endpoint JSONP.
**Verdicts**: `x({...})` → a script-tag read — no CORS needed.

## Probe 10 — the ws probe — the channel check

```bash
curl -s -i -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: x' \
  -b "$CJ" "$BASE/ws" | head -5
```

**Measures**: is there a ws endpoint.
**Verdicts**: a 101 upgrade → a CSWSH read channel.

## The probe-order — the sequence

```text
1. baseline — is the endpoint sensitive
2. foreign-Origin — is the CORS open
3. credential — does the cookie ride
4. null — an opaque bypass
5. lookalike — a check-shape bypass
6. url-parse — a confusion bypass
7. preflight — a non-simple read
8. vary — a cache check
9. jsonp — an alternate read
10. ws — a channel check
```

## The probe-count — the bounded sweep

```text
probes 1-3: the orientation — 3 commands
probe 4-6: the bypass battery — a batch of ~15 Origins in one sweep
probe 7-10: the alternates — 4 commands
total: ~20 commands for a full CORS characterization — a bounded
sweep, not an unbounded hunt
```

## The probe-ledger — the measurements recorded

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-probes: baseline=<sens?> acao=<v> acac=<t/f> cookie=<s> check=<shape>"
```
