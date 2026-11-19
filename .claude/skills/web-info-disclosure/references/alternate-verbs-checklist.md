# 403 bypasses — verbs, headers, path tricks — checklist

A 403 on a real artifact is 'forbidden', not 'absent': alternate verbs, Host tricks, and path forms reopen it.

## Checklist

- [ ] On every 403 in the bounded list: try HEAD, OPTIONS, POST.
- [ ] Try trusted headers: X-Forwarded-For, X-Real-IP, X-Original-URL, X-Rewrite-URL.
- [ ] Try path variants: //path, /./path, /path/, /path%2f.
- [ ] A flip to 200/redirect is a finding AND a route in.

## Abort conditions

- X-Original-URL/X-Rewrite-URL let a proxy route you around the ACL.
- Semicolon and %2e tricks work on Java/Apache stacks.
- A 403→302 to login means auth-gated, not forbidden.

## Falsifier

Falsifier — every verb/header/path variant returns the same 403: the artifact is genuinely forbidden to this surface.
