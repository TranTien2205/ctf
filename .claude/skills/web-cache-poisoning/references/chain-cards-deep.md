# Chain cards deep — the verified card's mechanics, exhaustively

The one verified card's every step, grounded.

---

## The HTB Encodecept card — the full mechanics

### The surface — the chain's setup

```text
a Rails app behind an nginx proxy_cache — an authenticated
/settings.html page — a markdown template system (redcarpet) — a
report feature — a charset reflection — a marshal RCE. the chain:
an authenticated page cached + served anonymously + a charset XSS +
a marshal RCE.
```

### The card's signals — the classification vocabulary

```text
'nginx', 'proxy_cache', 'x-cache-status', 'rails', 'contract_frontend',
'settings', 'bio', 'markdown', 'redcarpet', 'report',
'contract_manager', 'contract_templates', 'marshal', 'django',
'owner__password__startswith' — the classifier's vocabulary for this
shape.
```

### The first probe — the card's own

```bash
# the card's first_confirming_probe — the authenticated-page deception
# an authenticated GET stores the privileged page
curl "https://target/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # MISS — stores
# an anonymous GET — the stored copy serves it
curl "https://target/settings.html?cb=<unique>"                       # anonymous — HIT + the page?
```

```text
the card's probe: 'authenticated GET /settings.html?cb=1 twice, then
anonymous GET /settings.html?cb=1'.
expected: 'anonymous request returns 200 with X-Cache-Status HIT and
the body of the authenticated page'.
falsifier: 'anonymous request is a 302 to /login'.
```

### The mechanism — the key-mismatch

```text
the cache keys on the URL, not the auth state — an authenticated GET
stores the privileged page under the shared URL — an anonymous GET
for the same key gets the stored privileged copy — the auth state
wasn't in the key.
```

### The blast radius — the card's trap note

```text
'cache poisoning affects all players until expiry; the verified chain
also combined charset XSS and marshal RCE, so created templates must
be removed and disposable cachebusters used.'
```

### The chain — the deception + the injection + the RCE

```text
step 1 — the authenticated page cached under a shared URL — the
  stored copy serves the privileged content to the anonymous
step 2 — a charset reflection — an injected charset XSS stored in
  the cached page — the privileged bot's XSS writes files inside the
  container
step 3 — a marshal RCE — the chain reaches the flag
```

### The deception's confirm — the wrong-context serve

```text
the anonymous request returns the privileged page (a 200 with the
authenticated content, not a 302 to login) AND a cache HIT — the
stored copy served the privileged content to a different context.
```

### The injection's confirm — the stored payload

```text
an unkeyed reflected charset carries a payload — the stored copy
carries the injected XSS — every requester's page has it — a stored-
XSS-like delivery through the cache.
```

### The falsifier — when the card doesn't apply

```text
the anonymous request 302s to /login — the cache didn't serve the
privileged page — the auth state WAS in the key or the page isn't
cached — the card doesn't apply.
```

### The evidence — what the card required

```text
a stored response — a cache HIT on the second identical request —
the suspected input omitted from the cache key — the reflected value
reaching a victim response. a marker reflected only in the immediate
MISS response is not cache poisoning.
```

### The per-step probe map — how to run the card

```text
step 1 — run the card's first_confirming_probe — the authenticated-
         served-anonymously deception
step 2 — if the deception confirms — run the charset XSS injection
step 3 — the bot's XSS writes files — the marshal RCE — the flag
```

### The per-step falsifier — when to move

```text
step 1 — a 302 to login → the auth state WAS keyed → a different class
step 2 — a keyed charset → a per-input entry → a different class
step 3 — no marshal surface → a different chain
```

### The card's use — run the card's probe first

```text
a chain card match → run the card's first_confirming_probe first —
the card carries the traps that cost time the first time — the probe
is the cheapest confirm — a confirmed card is a solved challenge.
```
