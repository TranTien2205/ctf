# Anti-patterns — what NOT to do

## "Spray a big wordlist to find the oracle"

The oracle needs exactly 3 requests (good/bad/repeated-bad). A 10k-name
spray proves nothing the 3-request probe does not, trips the lock, and
abuses a shared target. Spray is the brute-force RUN; the oracle is the
MEASUREMENT. Different budgets.

## "Trust the rendered page"

The browser hides the differential — whitespace, comments, hidden
inputs, `data-*`, inline booleans. Diff raw bytes + the `-sv` envelope.

## "One anomalous response = the oracle"

A single `500`/`302`/different-body is a crash, a CSRF failure, or
per-request noise. Re-send the exact request; no-repeat means no channel.

## "Uniform text = no oracle"

The text channel is one of four. Timing, side-artifacts, and the OTHER
forms still leak. Uniform text closes the text channel, not the class.

## "Probe only /login"

The most-hardened form. check-username/register/reset/api leak first.
Coverage is per-form; a uniform login is not "the app is clean".

## "I didn't see a 429, so no throttle"

A bounded burst (8-15) is the measurement. "Didn't notice" across a few
probes is not absence — record the count, not the impression.

## "Burn a victim's account to prove the lock"

Lock your OWN known-good to measure the threshold. A victim's locked
account is an abuse and destroys the account's availability.

## "Keep re-probing a closed channel"

A channel measured uniform across `bad1==bad2`+good is closed — do not
send a 10th variant. Record the negative; the next channel or form is
the move.

## "Route everything through enum"

A uniform-auth target with a JWT/session bug is `web-auth-session` —
this class needs a differential OR a throttle finding; a clean auth
path is the neighbor class.

## "Claim catalogue as experience"

No local solve — the shapes are standard knowledge. Record what is
measured in `../field-notes.md`; never "this worked before here".
