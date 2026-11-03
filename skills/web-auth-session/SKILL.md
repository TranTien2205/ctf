---
name: web-auth-session
description: Prove authentication bypass with a forged credential, its invalid control and privileged content. Use when a token, a cookie or a header decides whether a request is authenticated, or when a login looks skippable — alg=none versus signature stripping, key confusion, kid traversal, claim swapping, expiry and session fixation.
classes: auth-bypass
---

# Authentication and session handling

Proof requirement: **a forged or absent credential accepted on a privileged
resource, with an invalid one rejected.** Three checks — a forged token accepted,
a deliberately invalid one rejected, privileged content returned — and testers
routinely arrive with the first.

## Why acceptance alone is worth nothing

`alg=none` coming back 200 feels like the finding. It is not one until you know
what a *broken* credential returns: an endpoint that never required
authentication answers 200 to every token, including one made of noise. Reported
as a signature bypass, it is the wrong vulnerability with the wrong fix — and the
right one, "this resource needs no credential at all", is already in your hand.

`proof.token_probe` takes both controls itself: the `garbage` transform, appended
to your list whether you ask for it or not, and a request with no credential at
all. Pass `privileged_marker=<a string only an entitled caller sees>` too —
without it the third check cannot pass and the grade stops at `supported`. It
reads acceptance as *the same status as your real token, and under 400*, so a
stale token makes every forgery look rejected. And it records the forgeries and
the two controls but not the baseline, so your own expired token still working
unchanged is a record you write.

## Read the token before you change it

Decode the two base64url segments first: no request, no budget, and it decides
every later step.

| what you read | what it tells you |
|---|---|
| `alg` | which transforms apply at all: `HS*`, `RS*`/`ES*`, or already `none` |
| `kid`, `jku`, `x5u` | the key is fetched by name or by URL — attacker-influenced inputs |
| `sub`, `role`, `scope`, `tenant` | which claim the authorization decision probably reads |
| `exp`, `iat`, `nbf` | whether expiry is expressed at all, and over what window |
| the third segment | 43 characters is HS256, 342 is RS256, empty is already `none` |

An opaque session cookie decodes to nothing, which is information: every JWT
transform reports `does not apply to this token`. Run the tool anyway with
`location=cookie:<name>` for the two controls, and look for the forgery elsewhere.

## The transforms, and what accepting each one means

```
proof.token_probe url="http://t/api/me" token="<yours>" privileged_marker="admin"
  transforms=["alg-none","strip-signature","claim-swap"] claims={"role":"admin"}
```

| transform | what it changes | accepted means |
|---|---|---|
| `alg-none` | `alg` set to `none`, signature dropped | the library honours an attacker's choice of algorithm |
| `strip-signature` | signature emptied, `alg` untouched | verification is never called |
| `claim-swap` | claims replaced, signature kept | the signature is not checked — the HMAC cannot still match |
| `expiry-extend` | `exp` plus a year, signature kept | the same bug, on a token that expresses expiry |
| `kid-traversal` | `kid` points at `/dev/null`, signature kept | the key is loaded by name and an empty file fails open |
| `garbage` | a token this issuer never minted | **nothing.** This one must be rejected |

`alg-none` and `strip-signature` look alike and are not: the first is a verifier
reading `alg` out of the token it verifies, the second a verifier never invoked.
Pinning the algorithm list fixes one and not the other, so the finding says which.

## What you mint and record by hand

Key confusion is `RS256` re-signed as `HS256` with the public key as the HMAC
secret: the server verifies with bytes it published — a certificate, the bundle,
`/.well-known/jwks.json`. No transform signs for you: mint it, send it, record it:

```
ledger.add_evidence kind=probe vuln_class=auth-bypass hypothesis_id=hy-...
  record={"token_accepted":true,"privileged_marker":"admin",
          "payload":"RS256 token re-signed HS256 with the published modulus",
          "response":{"status":200,"body_span":"<the privileged content>"}}
```

Then the same `proof.token_probe` call with `transforms=["garbage"]` on this
hypothesis, and `proof.verify vuln_class=auth-bypass hypothesis=hy-...` grades
the set on equal terms. It will not take the acceptance without the rejection.

Session fixation is the same arrangement in two phases: an identifier you chose
before authentication, still valid after it. Two records carrying the *same*
value — pre-login as `kind=control` with `token_accepted=false`, post-login as
`kind=probe` with `token_accepted=true` and the marker. A rotated cookie ends it.
The pre-login record must be a refused request to that same privileged resource:
the matrix reads any `token_accepted=false` as the control, so add `garbage` too.

## "The signature is not checked" versus "the claim is not authorised"

- **Signature not checked.** A transform that keeps the old signature and changes
  the payload is accepted. Fix: verify, with a pinned algorithm and key.
- **Claim not authorised.** The token is validly signed — the server minted it —
  but a claim you influenced at registration or profile update is what the
  authorization decision reads. Nothing is forged, the trust boundary is wrong,
  and the fix is to resolve entitlements server-side. When what changed is
  *whose* data comes back, the class is `idor`: `skills/web-authz/SKILL.md`.

## What does not count

- **A 200 on a forged token with no control.** The class is the asymmetry.
- **A missing `exp`, an `alg` of `none`, a short key.** Token inspection is a
  configuration observation; nothing is bypassed until a request was accepted.
- **An unauthenticated endpoint.** Real, and a different finding — the no-token
  control distinguishes it, and the tool says so in its `next`.
- **A secret cracked offline.** Weak-key is its own finding; the proof is still
  a request accepted, with its controls.
