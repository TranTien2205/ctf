# Sensitive endpoints — the read targets that carry the flag

A CORS read is only useful on an endpoint returning session data.
The endpoint inventory and how to find the right target.

---

## 1. The endpoint classes

```text
/api/me, /api/user, /api/profile    — the session's own data
/api/flag, /flag, /admin            — the flag endpoint
/api/token, /api/csrf-token         — a capability the write needs
/api/account, /api/balance          — account data
/api/secret, /api/key, /api/config  — a leaked secret
/api/messages, /api/data            — session-scoped data
```

## 2. The inventory grep — finding the read targets

```bash
# the endpoints that return session/flag data
grep -rnoE '(api|me|user|profile|flag|secret|data|private|admin|account|balance|token|config|session|auth|info)' <src> | \
  grep -iE 'route|@|app\.|def |get|json|res\.|return|response' | head -30

# the front-end's cross-origin calls — the app's own API surface
grep -rnoE "fetch\(|axios|XMLHttpRequest|api\.|/api/" <src>/static/*.js <src>/templates/*.html 2>/dev/null | head -20
```

## 3. The sensitivity test — does the endpoint carry the flag

```bash
# the endpoint's response — is it session-scoped?
curl -s -b "$CJ" "$BASE/api/me"
#   {"name":"x","flag":"FLAG{...}"} — session data — the target
curl -s -b "$CJ" "$BASE/api/public"
#   public data — not the read target
```

## 4. The credentialed-vs-public split

```text
an endpoint returning the SAME data unauthenticated as
authenticated is a public API — a `*` read of it is fine, not the
vuln. the vuln is an endpoint whose data CHANGES with the session —
a flag cookie, a logged-in profile.
```

## 5. The flag-in-response check

```bash
# does the authenticated response carry the flag?
curl -s -b "$CJ" "$BASE/api/me" | grep -iE 'flag|FLAG|secret|key|token'
# the flag's exact field — the exfil must carry it
```

## 6. The capability-endpoint — a read that leaks a write token

```text
/api/csrf-token, /api/token — a read whose value unlocks a write —
the CORS-read→CSRF-write chain's target. the read leaks the
capability, not the flag directly.
```

## 7. The read-vs-write-endpoint — a CORS read target

```text
a GET endpoint returning data — the CORS read. a POST endpoint
that takes a write — not a CORS read (a CSRF write, a different
class). CORS reads; CSRF writes.
```

## 8. The endpoint-shape grep — a JSON-API vs HTML

```bash
# a JSON API — the fetch reads .json()
curl -s -b "$CJ" "$BASE/api/me" | head -c 100   # {"..."}
# an HTML page — the fetch reads .text() and scrapes
curl -s -b "$CJ" "$BASE/admin" | grep -i 'flag'
```

## 9. The multi-endpoint chain — a read that feeds a read

```text
/api/token returns a key; /api/flag needs ?key=<key> — a two-step
read. the exploit page chains the fetches.
```

## 10. The unauthenticated-endpoint — the `*`-only case

```text
an endpoint that returns the flag WITHOUT a session — a public `*`
read is the trivial case; the CORS question doesn't arise. a `*`
endpoint with the flag is 'the flag is public', not a CORS vuln.
```

## 11. The endpoint-inventory table

```text
/api/me        — session data — the canonical target
/api/flag      — the flag — the direct target
/api/token     — a capability — the chain target
/api/admin     — admin data — privileged read
/admin         — an HTML page — scrape the flag
/api/config    — a config — may carry a key
/api/user/<id> — a foreign user's data — an IDOR+CORS blend
```

## 12. The selection rule

```text
read the endpoint that carries the flag or a capability — not just
'any endpoint that reflects ACAO'. a reflected ACAO on a public
endpoint is noise; on /api/me it's the vuln.
```
