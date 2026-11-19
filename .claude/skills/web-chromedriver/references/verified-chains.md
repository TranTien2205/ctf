# Verified chains — the locally-proven shapes

## The honest status

`web-chromedriver` is a **verified** skill — its local-bot-debugging
and channel-check discipline is anchored by two solved challenges.
What follows names the verified patterns, not invented proof.

## Verified: the local-bot-debugging pattern

**Anchor**: `solved/apexsurvive.md`

- a stored-XSS -> template-overwrite chain
- payload developed against a local headless browser
- confirmed stages fired at the live bot once, worked

**What is verified**: reproducing the challenge's admin bot locally
turns a blind channel into a debug loop — the method, not a specific
payload.

## Verified: the channel-check lesson

**Anchor**: `solved/tornadoservice.md`

- the payload's exfil used a tunnel with a headless-blocking
  interstitial
- attempts were lost to the dead channel
- the fix: verify reachability from inside the driver first

**What is verified**: the tunnel/interstitial failure mode is real and
costly; the pre-check is the fix.

## The distinction this skill must keep

These anchors verify the *method* — local reproduction and channel
checking. They do not verify a specific exposed-endpoint file read or
a specific payload. Keep the evidence language honest:

- **verified method**: local-bot debugging, channel pre-check
- **standard knowledge**: the WebDriver endpoint's file/loopback read,
  the primitive set
- **not locally verified**: a specific challenge's exposed driver

## How to cite them

- the reproduction discipline -> `apexsurvive`
- the channel check -> `tornadoservice`
- the endpoint-as-capability -> standard WebDriver knowledge, not a
  local solve

## The card's place

`knowledge/chains/` holds the solved-card library — the anchors above
live there as the chain cards these lessons came from. Read them for
the full chain context; this file is the summary the skill's honest
status requires.
