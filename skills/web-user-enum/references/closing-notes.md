# Closing notes — what a complete pass proves

## The done-state

A `web-user-enum` pass is complete when:

1. **every account-touching endpoint is inventoried** — login/register/
   reset/check/unlock/mfa/invite/api/graphql/users, every alias
2. **every (form × channel) cell is measured** — the masked body, the
   status+`Location`, the `-sv` envelope, the N>=8 median timing, the
   send-side, the lock — each marked `oracle`/`uniform`/`unmeasured`
3. **the oracle is confirmed** — a repeated, channel-identified delta
   that tracks the username-class across a second bad name and a re-run
4. **the throttle is measured** — absent / threshold / bypassed, with
   the count or the reset verbatim
5. **the verified names are recorded** — each with its oracle excerpt
6. **the negatives are recorded** — each closed cell with its falsifier

## What a complete pass proves

- the auth surface's existence-oracle is fully enumerated — which forms
  leak and on which channel
- the guessing loop's bound is measured — absent, at-N, or bypassed
- the verified accounts are named — the chain's targets
- the per-cell coverage is recorded — the next attempt does not re-probe

## What a complete pass does NOT prove

- that an unmeasured channel is closed (a `gap` is not a negative)
- that a uniform-login app is clean (register/reset/check may still
  leak)
- that a throttle is un-bypassable (a counter-key not yet tested —
  session/endpoint/method — may reset)
- that a confirmed account's credential is weak (the credential attack
  is `web-auth-session`'s, not this class's)

## The honest close

Report: `N forms, M oracles (<form>:<channel>), K confirmed names,
throttle=<absent|at-N|bypassed>`. A measured all-uniform is a clean
negative, not a failure. Never claim a differential from a single or
unmasked response, and never present the catalogue as a local solve.
