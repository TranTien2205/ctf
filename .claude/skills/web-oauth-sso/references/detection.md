# Detection — mapping the OAuth surface

The OAuth attack surface is invisible until you walk the flow once. The
transcript — every redirect, parameter, cookie set, and who set it — is the
detection surface.

## The walk

```bash
# capture the full flow, unauthenticated
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee flow.txt
grep -E "Location:|Set-Cookie:|HTTP/|code=|state=|client_id=|redirect_uri=" flow.txt
```

## What to record

| Artifact | Where it appears | The bug it names |
|---|---|---|
| `state` parameter | in the `authorize` URL and the `callback` URL | not bound to session → CSRF; predictable → replay |
| `redirect_uri` | in the `authorize` URL | loose validation → code delivered to attacker |
| `code` | in the `callback` URL | not bound to client → replayed cross-client |
| `session` cookie | set by the app | the app's own session |
| `token`/`sso`/`auth` cookie | set by the IdP | the delegated identity — the swap target |
| `SAMLResponse`/`SAMLRequest` | in POST body or URL | the SAML shape — decode it |
| `access_token`/`id_token` | in fragment, URL, or response | leaked, replayed, or cross-client |
| `nonce` | in the `authorize` URL | missing → replay of the callback |
| `scope` | in the `authorize` URL | broader than requested → privilege escalation |
| `email`/`preferred_username` claim | in the userinfo or id_token | the account-linking match field |
| `email_verified` claim | in the userinfo or id_token | ignored → unverified email linking |

## The cookie inventory

Two cookies is the signal. One from the app, one from the IdP, both in the
same jar. Check each:

| Cookie attribute | The check | The gap |
|---|---|---|
| `SameSite` | `Strict` or `Lax` | missing or `None` → cross-site writes land |
| `HttpOnly` | present | missing → readable by JS, but the swap still works |
| `Secure` | present | missing → over plain HTTP |
| `Domain` | set to the app domain | set to a parent domain → shared across subdomains |
| `Path` | `/` or a restricted path | `/` → readable everywhere |

## The endpoint inventory

| Endpoint | The check |
|---|---|
| `/authorize` or `/oauth/authorize` | the IdP entry point — does it accept `redirect_uri` variations? |
| `/token` or `/oauth/token` | the code exchange — does it re-validate `redirect_uri`? |
| `/callback` or `/oauth/callback` | the app's entry point — does it validate `state`? |
| `/login` or `/sso/login` | the app's login — does it ignore credentials and use the jar? |
| `/register` or `/signup` | the account creation — is it idempotent? |
| `/link` or `/connect` | the account-linking endpoint — does it require authentication? |
| `/submit-url` or `/visit` | a bot's URL-rendering endpoint — the delivery channel |
| `/userinfo` or `/me` | the identity endpoint — what claims does it return? |

## The parameter inventory

Every parameter in the authorize URL is a testable surface:

| Parameter | The check |
|---|---|
| `client_id` | is there a second registered client with a different `client_secret`? |
| `redirect_uri` | the validation shape — exact, prefix, wildcard? |
| `response_type` | `code` vs `token` vs `id_token` — implicit flow leaks to the fragment |
| `scope` | broader than the app requested? |
| `state` | bound to session? predictable? reflected? |
| `nonce` | present? validated? |
| `code_challenge`/`code_challenge_method` | PKCE — is it enforced? |
| `prompt` | `none` → silent re-auth; `consent` → forced consent |
| `max_age` | re-authentication required |
| `login_hint` | prefilled username — enumeration or injection |
| `id_token_hint` | a previous id_token — replay surface |

## The first discriminating signal

A `state` that is *not* cryptographically bound to the session cookie. Test:
start the flow, capture the `authorize` URL, open it in a fresh jar, complete
the flow. If the session lands on the attacker's account, `state` is not
bound — the CSRF shape is live.
