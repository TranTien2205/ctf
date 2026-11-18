# Evasion and WAF — when a filter inspects the delivery

A WAF/CDN/app-filter that inspects requests may block the CSRF
delivery itself. The evasion corpus — and what a filter can't
actually stop.

---

## 1. What a filter CAN'T stop — the browser's own request

```text
a CSRF is the VICTIM's browser sending a legitimate-looking request
— the WAF sees a well-formed, credentialed request from a real user
agent. there's no 'attacker' signature — the malicious part is
WHERE the request originated (the page), which the server can't see.
```

A WAF filters REQUESTS, not requesters. A CSRF request is identical
to a legitimate one — that's the confused-deputy essence.

## 2. The filter-shapes that DO apply — the request's content

```text
a WAF may inspect the BODY for malicious patterns (a stored-XSS
payload, a SQLi string, a template-injection marker):
- the CSRF carries a payload the WAF blocks → encode/obfuscate the
  payload, or split it across the write's fields
- a payload the filter can't distinguish (a clean field value) →
  it passes — a CSRF writing a normal-looking value isn't filtered
```

## 3. The Origin/Referer-filter — a WAF-side CSRF check

```text
some WAFs/CDNs add a CSRF layer — a request with a foreign/absent
Origin gets blocked at the edge BEFORE the app. the bypass:
- the Origin can't be forged by JS — but a data:/no-referrer page
  may send Origin: null which a 'present'-requiring WAF may also
  block
- a same-site page (subdomain, stored) sends a same-site Origin —
  the WAF's cross-site check passes
```

## 4. The rate-limit — the bot-cycle budget

```text
a per-IP rate-limit on the write endpoint — each failed CSRF delivery
costs a cycle and the bot's IP may be limited. batch the probes:
- multi-form chains in one page
- a marker-per-attempt to distinguish results
- poll the oracle, don't re-deliver
```

## 5. The CSP on YOUR page — the delivery-side block

```text
a CSP on the page HOSTING the CSRF (your host, or a stored context)
that blocks inline scripts — the auto-submit never runs:
- your own host → you control the CSP — allow inline or use a
  non-script auto-submit (a meta-refresh, an onload attr)
- a stored context → the target's CSP may block your injected JS —
  a pure-HTML form + a click, or an event-handler the CSP allows
```

## 6. The `Cross-Origin-Opener-Policy`/`COEP`/`CORB` — page isolation

```text
COOP/COEP/CORB on the TARGET's responses — isolation headers that
mostly affect embedding the target, not CSRF-ing it. a form POST
isn't a resource-load — these don't block the write.
```

## 7. The "the WAF sees the bot's request differently" case

```text
a WAF that whitelists the bot's IP/UA — the bot's request passes
where a foreign one is blocked. a CSRF via the bot inherits the
bot's trusted position — the WAF's IP-allow applies.
```

## 8. The payload-shape evasion — making the write look clean

```text
- a stored-XSS-via-CSRF: encode the payload to evade a body-scan —
  <svg onload=>, unicode, case-mix, attribute-order
- a SQLi-via-CSRF: the field carries the injection — encode it in
  the field's value
- a 'clean' field the write accepts — the least-filtered shape
```

## 9. The filter→carrier decision

| Filter | The evasion |
|---|---|
| body-pattern scan | encode/obfuscate the payload, or use a clean field |
| Origin/Referer required | a same-site/subdomain page |
| rate-limit | batch probes; poll the oracle |
| CSP on the page | a non-script auto-submit (meta-refresh/onload) |
| IP/UA allow for the bot | deliver through the bot |

## 10. The falsifier

```text
a WAF that enforces a same-site Origin exactly + a required token
+ a content-type whitelist — the delivery can't satisfy all gates
AND evade the filter. the class is closed; a stored page or a
different class.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "waf: <filter-shape> -> <the evasion carrier>"
```
