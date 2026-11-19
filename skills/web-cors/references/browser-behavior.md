# Browser behavior — how each engine enforces the CORS gates

The CORS rules are browser-enforced — Chrome, Firefox, and Safari
differ on edge cases.

---

## 1. The universal rules — all engines

```text
- `*` + credentials → rejected, everywhere.
- a foreign Origin not in the ACAO → the read blocked, everywhere.
- a custom header needs a preflight, everywhere.
- SameSite=Lax cookies don't attach to a cross-site fetch, everywhere.
```

## 2. Chrome — the strict default

```text
- SameSite=Lax-by-default — an unmarked cookie is Lax → doesn't
  attach to the cross-site fetch.
- 'Schemeful SameSite' — http→https is a site-change.
- strict null-origin — a data: URL's Origin is 'null', no override.
- PNA — private-network fetches may need a separate preflight.
```

## 3. Firefox — the slightly looser edge

```text
- SameSite=Lax-by-default too (modern versions).
- some file:///`null` origin edge cases differ.
- a `network.cookie.sameSite.laxByDefault.disabled` flag exists in
  some builds — a looser SameSite.
```

## 4. Safari — the ITP layer

```text
- Intelligent Tracking Prevention — a cross-site fetch's cookie
  may be stripped as 'tracking' even when SameSite=None — an extra
  gate specific to WebKit.
- strict on opaque origins.
```

## 5. The `null` origin per engine

```text
a sandboxed iframe → Origin 'null' — all engines.
a data: URL → Origin 'null' — all engines.
a file: URL → Origin 'null' (modern) or 'file://' (older) — varies.
```

## 6. The preflight per engine

```text
all engines preflight non-simple requests identically — the ACAM/
ACAH check is universal. the cache lifetime (Max-Age) is honored
up to an engine cap (Chrome caps ~2h).
```

## 7. The PNA layer — Chrome's private-network gate

```text
a fetch from a public origin to a private/loopback address needs a
'private network access' preflight — a separate permission beyond
CORS. relevant when the target is internal and the page is public.
```

## 8. The redirect-cors interplay

```text
a redirect (30x) during a CORS fetch — the final response's ACAO is
checked, not the redirect's. a redirect to a different origin is a
new CORS question.
```

## 9. The `mode` per engine

```text
mode:'cors' — the default cross-origin — universal.
mode:'no-cors' — an opaque write — universal.
mode:'navigate' — not a fetch mode.
```

## 10. The credential-mode per engine

```text
credentials:'include' — sends the cookie cross-site — universal;
the SameSite gate decides whether it actually attaches.
```

## 11. The test-context note — your browser vs the bot's

```text
your browser's behavior ≠ the bot's — a headless chromium vs a
real Chrome, a different SameSite default, a different cookie jar.
test against the BOT's actual context, not yours.
```

## 12. The per-engine matrix — the edge cases that matter

```text
edge                    Chrome    Firefox    Safari
* + credentials         reject    reject     reject
null-origin data:       null      null       null
SameSite=Lax cookie     no-attach no-attach  no-attach (+ITP)
preflight cache         ~2h cap   ~24h cap   ~per-session
PNA preflight           yes       partial    no
file: origin            null      null       file://
```
