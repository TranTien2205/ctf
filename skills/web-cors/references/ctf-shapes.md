# CTF shapes — how the CORS challenge is actually laid out

The recurring CTF CORS setups — each a complete challenge shape.

---

## 1. The reflected-API shape — the canonical CTF CORS

```text
an API (often a separate api.sub.domain or /api/* path) with a
reflected ACAO+ACAC, a bot that visits your page, and a flag in
/api/me or /api/flag. the whole challenge is the read+exfil.
```

```bash
curl -i -b "$CJ" "$BASE/api/flag" -H 'Origin: https://evil.com'
#   ACAO: evil.com + ACAC:true → the trivial CTF win
```

## 2. The `null`-origin shape — the data: URL challenge

```text
a strict-looking CORS that allows 'null' — the bot opens a data:
URL you hand it; the fetch originates 'null' → reads the flag.
```

## 3. The subdomain shape — a trusted `*.target.com`

```text
the CORS trusts *.target.com — a subdomain you control (a
CTF-supplied sub, a subdomain XSS, or a takeover) reads the flag.
```

## 4. The token-read → write shape — the CORS+CSRF chain

```text
a CORS-open /api/csrf-token leaks the token → your page reads it →
fires a CSRF-write → the write triggers the flag. the read is the
key to the write.
```

## 5. The JSONP-legacy shape — a script-tag read

```text
the endpoint is JSONP (a ?callback= param) — a <script src> read
with no CORS check — the tag's cookies ride (SameSite-gated).
```

## 6. The websocket-hijack shape — a ws channel

```text
a ws endpoint with cookie-auth and no Origin check — a CSWSH
read+write — the flag flows over the socket.
```

## 7. The postMessage-broadcast shape — a page that leaks

```text
a target page postMessages the flag/data to '*' — your iframe
receives it — a postMessage-hijack, not a fetch read.
```

## 8. The cache-poison shape — a reflected ACAO without Vary

```text
a reflected ACAO without Vary: Origin — a shared cache serves the
attacker-origin response to every visitor — a stored-leak.
```

## 9. The internal-API shape — a loopback/pna target

```text
an internal API (127.0.0.1) with a reflected CORS — a browser-side
fetch reaches it via the bot's own network position — the 'internal'
assumption isn't a defense.
```

## 10. The same-origin-vs-cors shape — a stored page wins

```text
a stored XSS on the target reads /api/flag same-origin — the CORS
question never arises. the CTF's CORS is the fallback when no XSS
exists.
```

## 11. The multi-step shape — a read chain

```text
/api/token → /api/flag?key=<t> → the flag — a two-step read the
exploit page chains.
```

## 12. The airgapped-bot shape — no external fetch

```text
the bot can't reach attacker.com — the exploit is a data: URL or a
stored page; the exfil is a write-back to the target or a
page-side readback.
```

## 13. The shape-to-route table

```text
reflected API + a bot          → the canonical read+exfil
a null-allowed CORS            → a data: URL page
a subdomain-trust              → a controlled-sub page
a token endpoint               → the read→write chain
a JSONP endpoint               → the script-tag read
a ws endpoint                  → the CSWSH read
a postMessage page             → the postMessage-hijack
a stored-XSS surface           → the same-origin read (skip CORS)
an internal API                → the bot-network read
```

## 14. The CTF-CORS ledger — naming the shape

```bash
python3 tools/state.py <c> --hypothesis \
  "ctf-cors: <shape> -> read /api/<ep> -> exfil -> FLAG{...}"
```
