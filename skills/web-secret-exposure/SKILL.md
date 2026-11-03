---
name: web-secret-exposure
description: Turn a credential shape found in a bundle, a backup or an error page into a finding. Use when a key, a token, a private key or a connection string appears in a response — where keys actually are, the record the matrix can grade, and how to show a key is live against its own issuer without touching a customer's data.
classes: secret-exposure
---

# Exposed credentials

Proof requirement: **the credential observed in a response and shown to be live
against its own issuer.** Three checks — observed in a response, shown to be
live, stored redacted — and the middle one is the step everyone skips. A shape in
a bundle is a string that matched an expression; until something answers to it
the severity is a guess, and the verifier says so: "not validated, so severity is
a hypothesis".

## Where credentials actually are, in rough order of how often they pay

- **the JavaScript bundle**, and the `.js.map` beside it, which carries the
  original sources including the config file the key was read from
- **`.env`, `.env.local`, `.env.bak`**, served because the web root is the repo
- **`.git/`** — `config` for a credentialed remote, then `logs/HEAD` and the
  objects for the commit that took the key out of HEAD
- **backups and swap files**: `.bak`, `.old`, `.orig`, `.save`, `~`, `.swp`
- **an error page** rendering the environment, the settings object or a
  connection string into a stack trace
- **`/proc/self/environ`** once a file read is proven: the key at runtime
- **committed CI configuration**: workflow files, a Jenkinsfile, a deploy script

The sweep is two tools: `recon.js_mine` reports credential shapes in a page's
scripts by kind, script and offset, and `fuzz.content` with
`extensions=".env,.bak,.old,.swp"` finds the paths nothing links to.

## The record the matrix can grade

`recon.js_mine` reports what it saw to you, but the record it writes carries
`extracted.secret_kinds` — a list, for the index — while the verifier reads
`extracted.secret_kind`, singular. That follows its own `next`: a shape in a
bundle is not a finding, so the gradeable record is one you write, for one key:

```
ledger.add_evidence kind=probe vuln_class=secret-exposure hypothesis_id=hy-...
  record={"target":"https://t/static/app.4f1c.js",
          "extracted":{"secret_kind":"github-pat","secret_value":"ghp_12…REDACTED",
                       "location":"app.4f1c.js offset 81422","validated":true,
                       "issuer_response":"200 login=build-bot, x-oauth-scopes: repo"}}
```

**The value is the one thing that must not be in there.** The check reads
`extracted.secret_value` and passes only when it is absent, contains `REDACTED`,
or is eight characters or fewer. The write-path redaction in `argus/util.py` will
not save you: it is a named list of shapes — AWS, GitHub, Google, Slack, two
model-API prefixes, a JWT — applied to `stdout_span`, `stderr_span`,
`callback_payload` and `response.body_span` only. A Stripe `sk_live_` key, a
private-key body or a password in a connection string is on neither list, and
`extracted` is not redacted at all — its first three fields are even copied into
the evidence index, the digest every model reads. The kind, the file and the
offset reproduce the finding; the value only copies the client's incident in.

## Validation is an operator action, deliberately

No tool here will call an issuer for you, and that is not squeamishness. The
broker's scope is a default-deny allowlist over the engagement's targets and
`api.github.com` is not in it; a validation tool would have to exempt itself from
the one check that makes this system trustworthy, and would send a live customer
credential off a machine the client does not control, with no human deciding.

So you make the call, under the authorisation you already have, and record the
outcome with `ledger.add_evidence` and `extracted.validated=true`. **The issuer
only**: only the service that minted the key can answer whether it still
authenticates, and a key that unlocks a third party's API is that third party's
resource, not your scope. **No customer data**: use the call that returns the
key's own identity, never the one that returns records. Expect the issuer to log
it, which is fine and worth saying before you make it.

| kind | the call that answers "is it live" | what you learn |
|---|---|---|
| `aws-access-key` | `aws sts get-caller-identity` | the account and principal ARN, and nothing else |
| `github-pat` | `GET https://api.github.com/user` | the login, plus `x-oauth-scopes`, which *is* the impact sentence |
| `slack-token` | `POST https://slack.com/api/auth.test` | the workspace and the identity it belongs to |
| `stripe-key` | `GET https://api.stripe.com/v1/account` | the account it belongs to; `/v1/charges` is customer data, so no |
| `google-api-key` | the one API the bundle itself calls with it | per-API: `REQUEST_DENIED` means live but not enabled there, a different sentence |
| `jwt` | the application's own authenticated endpoint | decode `exp` first — an expired token is not a credential |
| `private-key` | no call at all | compare its public half with the key the host presents; a match is live and nothing was authenticated |
| `basic-auth-url` | usually nothing you may do | logging in to the client's database is a human's decision; record `validated=false` with that reason |

That last row is not a failure: "validation needs authorisation to connect to the
database host" is a two-minute task for whoever holds it. A guess is not.

## The rotated key in an old bundle

The most common false positive in the class, and the reason the second check
exists. A key is taken out of the code and the old asset is still served — a CDN
path with the previous content hash, a cached bundle, a commit object, a release
artifact. The expression matches, the string is real, the credential was revoked
months ago, and nothing about the string says which. The issuer does, in one call:
a 401 closes it — record that, falsify it, report the shape present and the key dead.

## What does not count

- **A regular-expression match**, including this system's own.
- **A high-entropy string.** Entropy is not provenance: build identifiers,
  integrity hashes and minified names all look like keys.
- **A publishable key.** A Maps browser key, a Stripe `pk_live_`, a Sentry DSN
  and a Firebase config are *meant* to be in the bundle; the finding there, if
  any, is a missing referrer restriction, with its own evidence.
- **A key in a response you authenticated for.** A caller reading their own token
  back is a design. Check what an anonymous request sees.
- **An internal hostname, a stack trace, a version banner.** Not a credential.
- **A validated key with its value in the ledger.** The check fails, and it
  should: the proof must not become the second copy of the breach.
