# Verified chains — the cache-poisoning case, end to end

The one verified card's mechanics, grounded.

---

## The HTB Encodecept card — the charset-XSS cache-deception marshal-RCE

### The setup — the chain's surface

```text
a Rails app behind an nginx proxy_cache — an authenticated
/settings.html page — a markdown template system — a report feature —
a charset reflection — a marshal RCE. the chain: an authenticated
page cached + served anonymously + a charset XSS + a marshal RCE.
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

### The mechanism — the cache's key-mismatch

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
1. an authenticated page cached under a shared URL — the stored copy
   serves the privileged content to the anonymous
2. a charset reflection — an injected charset XSS stored in the
   cached page — the privileged bot's XSS writes files inside the
   container
3. a marshal RCE — the chain reaches the flag
```

### The card's signals — the classification vocabulary

```text
'nginx', 'proxy_cache', 'x-cache-status', 'rails', 'contract_frontend',
'settings', 'bio', 'markdown', 'redcarpet', 'report',
'contract_manager', 'contract_templates', 'marshal', 'django',
'owner__password__startswith' — the classifier's vocabulary for this
shape.
```

### The per-step mechanics — how the deception works

```text
step 1 — the authenticated page
  an authenticated GET /settings.html stores the privileged page
  under the URL — the cache doesn't distinguish 'your copy' from
  'the anonymous copy'
step 2 — the anonymous request
  an anonymous GET /settings.html hits the same key — the stored
  copy serves the privileged page — a 200 with the content, not a
  302 to login
step 3 — the charset XSS
  an unkeyed reflected charset — an injected charset XSS stored in
  the cached page — the privileged bot's XSS writes files
step 4 — the marshal RCE
  the chain reaches the flag through the marshal RCE
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
