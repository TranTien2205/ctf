# Troubleshoot (deep) — the stubborn-measurement playbook

## "the diff is unreadable — everything differs"

Strip aggressively — `sed -E 's/[a-zA-Z0-9+/=]{16,}//g'` removes most
tokens/nonces, `s/value="[^"]*"//g` blanks hidden inputs, `s/[0-9]{10,}//g`
strips timestamps/ids. If the diff is still all-noise, the form may
return a unique response per-request — use the status/timing channel.

## "every timing sample is wildly different"

Extreme jitter — a cold-cache first-request, a GC pause, a busy server.
Drop the first sample (warm-up), increase N, use median-of-medians
across 3 runs, or pin the connection. If jitter still swallows the
delta, the timing oracle is unmeasurable — record `sub-jitter` and use
a content channel.

## "the response is a redirect to a captcha interstitial"

The app interposes a CAPTCHA/challenge — the CAPTCHA's presence is a
signal (the app distinguishes attempts) but blocks the content oracle.
A CAPTCHA that only appears after N attempts is itself a measured
throttle; the content oracle may still fire within the first N.

## "my requests get a WAF/edge block"

A signature on the username field or a rate-of-requests block — slow
the probe, vary the header/UA, or use a different surface (the API may
be less WAF'd than the form). A WAF block is a defense, not a channel —
do not confuse a `403 WAF` with a `403 auth`.

## "the account I need is locked and I can't reset it"

Do not unlock a victim's account. Record `locks at N` + the confirmed
existence; the enum is already proven. The chain moves to `web-auth-session`
without needing the unlocked account.

## "enum_probe says uniform but curl differs"

The tool holds every field constant; a manual request adds a cookie,
a token, a header. Match the tool's exact request (same method, body,
headers); the tool's controlled-arm read is the reliable one. If they
still disagree, the manual request carries a confound — find it.

## "the throttle resets too fast to bound"

A per-second/per-minute window is not a loop-blocker — measure the
window (`N per T`), record it, and note a slow spray under the window
still passes. The finding is the WINDOW, not "no throttle".

## "I can't tell a format-404 from an oracle"

A `404` on `admin@x.c` when the app expects bare `admin` is a FORMAT
error, not an oracle. Probe the format first (`admin` vs `admin@x.c`);
the oracle only counts when the format is right on both arms.
