# Detection index — the host-header detection surface, indexed

The index — a header the app reads, a check the header gates, a sink that pays.

| Check | Header(s) | First probe | Sink | Proof |
|---|---|---|---|---|
| canonical-URL | `Host` | `Host: canary.example` on `/robots.txt` | generated links / redirects | canary in `Location`/`Set-Cookie`/body link |
| reset-link | `X-Forwarded-Host`, `X-Host`, `X-Forwarded-Server`, `X-HTTP-Host-Override`, `Forwarded` | `X-Forwarded-Host: canary.example` on `/reset` | reset email link | canary in the reset URL (tester's own account) |
| Location | `Host`, `X-Forwarded-Host` | `Host: canary.example` on `/redirect` | `Location` | canary in `Location` |
| Set-Cookie | `Host`, `X-Forwarded-Host` | `Host: canary.example` on `/login` | `Set-Cookie: domain=` | canary in cookie domain |
| cache-key | `Host`, `X-Forwarded-Host` | `Host: canary.example` on `/page` | shared cache | canary served to a clean request |
| rewrite ACL | `X-Original-URL`, `X-Rewrite-URL`, `X-Forwarded-Path`, `X-Forwarded-Prefix`, `X-Original-Path`, `X-Real-Path` | `X-Original-URL: /admin` on `/` | gated route | 200 with the admin body |
| forwarded | `Forwarded: host=` | `Forwarded: host=canary.example` on `/page` | generated links | canary in body |
| duplicated Host | `Host` × 2 | two `Host` headers, both orders | parser differential | different result by order |
| malformed Host | `Host` | `Host: evil.example:80`, `evil.example.`, empty | parser edge | routing/parse delta |
| absolute-URI | request line | `--request-target 'http://evil.example/'` | request-line differential | different backend than `Host` |
| multi-header | host + a trust flag | `Host:` + `X-Internal: true` | privileged route | 200 on a gated route |
| multi-proxy | `X-Forwarded-*` chain | `X-Forwarded-Host:` through the chain | per-layer normalization | origin sees a different host |
