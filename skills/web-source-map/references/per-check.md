# Per-check — one row per mined lead to verify

## Endpoint leads

| Mined string | Verify | If live |
|---|---|---|
| `/api/admin` | `curl $BASE/api/admin` | → `web-idor`/`web-logic-flaw` |
| `/internal/export` | `curl $BASE/internal/export` | → `file-read`/`web-logic-flaw` |
| `/graphql` | `curl -XPOST $BASE/graphql` | → `web-graphql` |
| `/api/user/:id` | `curl $BASE/api/user/1` | → `web-idor` |
| `/upload`, `/file/:name` | `curl $BASE/file/x` | → `web-file-upload`/`file-read` |
| a `/fetch?url=`/`/proxy?` | `curl "$BASE/proxy?url=..."` | → `web-ssrf` |

## Secret leads

| Candidate | Verify | If live |
|---|---|---|
| a JWT | decode; is it a real session? | → `web-auth-session` |
| `apiKey`/`token` | `curl -H"Authorization: Bearer $K" $BASE/api/me` | → `web-auth-session` |
| `AKIA...` | an AWS key — scope probe | → cloud/SSRF note |
| `sk_live_` | a Stripe-like secret | → `web-auth-session` |
| a private key | what does it sign/decrypt | → `web-auth-session`/`file-read` |
| `pk_live_`/public | publishable — likely dead | record negative |

## Flag/config leads

| Find | Verify | If live |
|---|---|---|
| `feature.admin` | set the flag, probe the endpoint | → `web-logic-flaw` |
| `config.debug` | `?debug=1`/a header | → `web-logic-flaw` |
| an internal URL | can an SSRF reach it | → `web-ssrf` |
| `__NEXT_DATA__` config | parse for secrets | → `web-auth-session` |
| `const FLAG` | `pre-flag` gate | → flag |

## Route leads

| Route | Verify | If live |
|---|---|---|
| client route `/admin` | does `/api/admin` exist | → its class |
| lazy route in manifest | fetch the page chunk | more endpoints |
| `/:id` param route | an IDOR probe | → `web-idor` |

## The dead-lead record

Every lead that fails the live check is recorded with its source file +
verbatim string + the dead response. A dead lead is a measurement.
