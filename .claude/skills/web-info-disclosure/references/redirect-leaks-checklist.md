# Redirect and Location-header disclosure — checklist

302s leak internal URLs; redirect chains reveal routing structure and sometimes unauthenticated intermediate content.

## Checklist

- [ ] curl -s -D- without -L — read the raw redirect, not the follow.
- [ ] Location headers name internal routes that aren't linked.
- [ ] A redirect's own body sometimes carries the content despite the 302.
- [ ] Chained redirects map the auth/routing structure.

## Abort conditions

- --no-follow on probes keeps the 302 oracle — the redirect IS the signal.
- Location to an internal host is a vhost find.
- A redirect that leaks a token in the Location query = session disclosure.

## Falsifier

Falsifier — redirects go straight to public pages: nothing hidden.
