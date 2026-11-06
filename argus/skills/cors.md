# CORS misconfiguration

**When:** an API serves authenticated/cross-origin data. `probe_cors` sends
a foreign Origin and reads `Access-Control-Allow-Origin`/`Allow-Credentials`.

## Verdicts and what they mean

| ACAO | ACAC | Verdict |
|---|---|---|
| reflects your evil origin | true | exploitable - any site reads the victim's data |
| `*` | absent/false | wildcard - public data only, usually low |
| `*` | true | browsers block `*`+credentials - misconfig but limited; note it |
| null | true | `Origin: null` (sandboxed iframe) is exploitable |
| subdomain/trusted-list echo | true | exploitable only via XSS on an allowed origin |

## What to test after the naive case

- `Origin: null` - sandboxed iframes, file://, redirects produce it
- Suffix tricks: `https://victim.com.evil.com`, `https://evilvictim.com`
- Prefix/typo tricks: `https://victimcom.evil`, `https://victim_com` (bad regex)
- Scheme downgrade: `http://victim.com` when only https is intended
- Preflight (`OPTIONS` with `Access-Control-Request-Method`) vs simple-request
  policy - a mismatched pair is its own finding

## Proof standard

The finding needs an authenticated response readable cross-origin: make the
request WITH the victim's credentials (the session you were given) and show
ACAO reflecting the foreign origin on THAT response. An unauthenticated
endpoint reflecting Origin is expected behavior for public APIs - check
whether the data is actually sensitive before rating it.

## Falsifier

ACAO absent, static allowlist, or echo only on public unauthenticated data.

## Severity guide

Credential-bearing reflection on sensitive data: high. `null`/`subdomain`
trust exploitable: high-medium. Wildcard on sensitive-but-public-ish data:
low. Reflected on public data: info.
