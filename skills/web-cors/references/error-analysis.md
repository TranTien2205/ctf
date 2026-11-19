# Error analysis — what each CORS error actually means

The browser's CORS errors and the curl signals — what each tells you
about which gate held.

---

## 1. The browser console errors

```text
'Access to fetch ... has been blocked by CORS policy:
 No Access-Control-Allow-Origin header is present'
→ the response has NO ACAO — the read is blocked — not CORS-open.

'... The value of the Access-Control-Allow-Origin header in the
 response must not be the wildcard * when the request's credentials
 mode is include'
→ ACAO:* + a credentialed fetch — the invalid combo — rejected.

'... The value of the Access-Control-Allow-Credentials header in the
 response is which must be true when the request's credentials mode
 is include'
→ ACAC absent/false — the credentialed read denied.

'... Request header field X-Token is not allowed by
 Access-Control-Allow-Headers in preflight response'
→ the custom header's ACAH gate held — the request never fired.

'... Method PUT is not allowed by Access-Control-Allow-Methods in
 preflight response'
→ the ACAM gate held — the method blocked.
```

## 2. The curl signals — what the headers say

```bash
# a reflected ACAO — your Origin echoed
ACAO: https://evil.com       → reflected — the check is open

# a `*` — public
ACAO: *                      → public read — never credentialed

# a null — opaque-allowed
ACAO: null                   → an opaque-origin read works

# a fixed value — a closed allowlist
ACAO: https://app.target.com → only that origin — closed to you

# no ACAO — no CORS
(absent)                     → the read is blocked — not CORS-open
```

## 3. The `*+ACAC` error — the invalid combo

```text
ACAO:* + ACAC:true → the browser rejects the credentialed fetch —
'... must not be the wildcard * when credentials mode is include'.
the endpoint LOOKS open but the credentialed read always fails.
```

## 4. The preflight-error — the request that never fires

```text
a non-simple request whose preflight's ACAO/ACAM/ACAH denies it —
the request never leaves the browser. the error names the gate:
'not allowed by Access-Control-Allow-Methods' or '-Headers' or a
missing ACAO on the OPTIONS.
```

## 5. The fetch-succeeds-but-public-data case

```text
the fetch returns 200 but the data is 'unauthenticated' or public —
the credential didn't ride (SameSite-gated cookie, no Bearer) — a
non-credentialed read, not the vuln.
```

## 6. The exfil-error — the read worked, the exfil failed

```text
the CORS read returned the data but the exfil fetch to your
listener failed — a CSP on the exfil page, a blocked domain, or an
unreachable listener — a separate gate.
```

## 7. The same-origin-error — a fetch that refused

```text
a `mode:'same-origin'` fetch to a cross-origin URL refuses at the
API level — a client-side error, not a CORS gate.
```

## 8. The redirect-cors error

```text
a redirect during a CORS fetch whose final response lacks a proper
ACAO — the read fails on the final response's CORS, not the
redirect's.
```

## 9. The network-error-vs-cors-error split

```text
a NETWORK error (a failed connection, a timeout) → the request never
reached the server — a connectivity issue, not a CORS gate.
a CORS error → the response arrived; the browser blocked the READ —
the CORS gate held.
```

## 10. The error-to-gate table

```text
error / signal                          gate that held
no ACAO on response                     not CORS-open
ACAO:* + credentials                    the `*`+cred rule
ACAC absent + credentials               the credential gate
ACAH doesn't list the header            the preflight-header gate
ACAM doesn't list the method            the preflight-method gate
fetch 200 but public data               the credential didn't ride
a fixed ACAO                            the strict allowlist
a CORS 'blocked' on the read            the actual-response ACAO
a network error                         connectivity — not CORS
```

## 11. The error-ledger — recording which gate held

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-error: <error-message> → gate=<which> → <next-action>"
```
