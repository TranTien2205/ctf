# Redirect and Location-header disclosure

302s leak internal URLs; redirect chains reveal routing structure and sometimes unauthenticated intermediate content.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Location: to an internal URL | internal route named | probe it |
| redirect chain through hidden stages | routing structure | read each hop |
| redirect body with content | body vs Location | --no-follow to read |

## Steps

1. curl -s -D- without -L — read the raw redirect, not the follow.
2. Location headers name internal routes that aren't linked.
3. A redirect's own body sometimes carries the content despite the 302.
4. Chained redirects map the auth/routing structure.

## Falsifier

Falsifier — redirects go straight to public pages: nothing hidden.

## Traps

- --no-follow on probes keeps the 302 oracle — the redirect IS the signal.
- Location to an internal host is a vhost find.
- A redirect that leaks a token in the Location query = session disclosure.

## Commands

```bash
curl -s -D- -o /dev/null '$BASE/admin'
```

## Cross-references

`response-anatomy.md` · `header-disclosure.md`
