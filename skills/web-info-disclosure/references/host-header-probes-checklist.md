# Host and forwarded-header probing — checklist

The app's trust in Host/X-Forwarded-Host splits internal vs external views — some artifacts only serve to the internal name.

## Checklist

- [ ] Re-request key artifacts with Host: localhost, Host: 127.0.0.1, Host: internal.
- [ ] Try X-Forwarded-Host / X-Forwarded-Server / X-Host on 403s.
- [ ] A different response under a different Host = a vhost finding.
- [ ] Captured vhost names feed further Host probing.

## Abort conditions

- Don't invent hostnames — use names leaked by certs, comments, headers.
- This boundary is shared with web-host-header — deeper attacks live there.
- A 403→200 flip under Host: localhost is a real misconfig.

## Falsifier

Falsifier — every Host variant returns the same content: single vhost, nothing hidden behind routing.
