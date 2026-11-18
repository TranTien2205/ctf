# Same-origin vectors — the CSRF that isn't cross-site

When every cross-origin gate holds, the remaining vector is a
request that's technically same-origin — a stored page, a subdomain
sibling, a redirect that lands on the target. The "same-site CSRF"
that bypasses the cross-site defenses.

---

## 1. The stored-page vector — the canonical same-origin CSRF

```text
a page stored on the target's own origin — a stored-XSS context, a
rendered profile/bio/comment, an uploaded HTML page — submits a form
SAME-ORIGIN. every cross-site defense (SameSite, Origin, Referer)
is satisfied trivially — it's the app's own origin.
```

```html
<!-- stored in a bio field that renders HTML -->
<form action="/transfer" method=POST>
<input type=hidden name=to value=attacker>
<input type=hidden name=amount value=999>
<input type=submit value="View more">
</form>
<!-- the victim viewing the profile clicks → same-origin write under
     their session -->
```

## 2. The subdomain vector — a sibling origin

```text
a page on *.target.com — a sibling subdomain — is 'same-site' not
'cross-site':
- SameSite=Lax considers subdomains same-site → the cookie attaches
- a Referer-host check *.target.com passes
- a wildcard CSRF_TRUSTED_ORIGINS/CORS covers it
the carrier: a subdomain-XSS, a subdomain-takeover, a shared-hosting
subdomain, or a sibling app the challenge ships.
```

```html
<!-- hosted on sub.target.com — same-site, not cross-site -->
<form action="https://target.com/x" method=POST><input name=a value=1></form>
```

## 3. The redirect-chain vector — a nav that lands on the target

```text
a request that starts same-site and redirects — or a nav whose
Sec-Fetch-Site becomes 'none':
- attacker.com → target.com/redirect?u=/write — the nav's context
  may become none or same-site through the redirect
```

## 4. The service-worker / cache vector

```text
a stored ServiceWorker on the target intercepts the next visit's
requests — a persistent same-origin CSRF middleware. needs sw-
installation (a separate primitive).
```

## 5. The "the same-origin page's own JS" — the XSS boundary

```text
a stored page that runs JS IS XSS — it can read the token, the DOM,
the cookies, and make authenticated requests trivially. a same-
origin CSRF without JS (HTML-only stored) is the interesting case:
the form submits same-origin, but the token must come from
somewhere — the real form's token the stored page can embed if it
can read the DOM (then it's XSS anyway) — or the write must be
token-free.
```

The HTML-only stored-CSRF needs a click (no auto-submit without JS)
OR a token-free write — it's the clickjacking-adjacent shape.

## 6. The same-site-sibling — a trusted-subdomain check bypass

```text
the server's Origin/Referer check: host.endsWith('.target.com') —
a subdomain passes. the carrier:
- a subdomain-XSS on any *.target.com
- a subdomain-takeover (a dangling CNAME)
- a shared-hosting subdomain the challenge grants
- a sibling app on the same parent domain
```

## 7. The "the write is same-site but cross-origin" — scheme/port

```text
'same-site' ≠ 'same-origin':
- https://target.com and http://target.com — same-site, different
  origin — a form from http→https is same-site (Lax attaches) but
  cross-origin (CORS still applies for reads)
- target.com:80 vs target.com:443 — same-site, different origin
- a subdomain — same-site, different origin
```

For CSRF (which doesn't read), 'same-site' is the bar — a subdomain
or a different-scheme page attaches the Lax cookie even though it's
technically a different origin.

## 8. The stored-page's token problem — the remaining gate

```text
a stored-CSRF page still faces the token check:
- if the write needs a session-bound token → the stored page's
  form must carry it — if the stored page can run JS, it reads the
  token (then it's XSS); if HTML-only, the token must be embeddable —
  usually it can't be read → the token gate still holds
- the stored-CSRF works on token-free writes, or writes whose token
  is not session-bound
```

## 9. The falsifier

```text
no stored-content context, no subdomain carrier, no same-site page
— every vector is genuinely cross-site and every cross-site gate
holds. the class is closed.
```

## 10. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "same-origin: stored-page/subdomain submits same-site -> bypasses gates"
```
