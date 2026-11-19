# Anti-enumeration defenses — and which channels survive them

## The uniform-message defense

`"invalid credentials"` / `"if that account exists, we emailed it"` —
the intentional equalization. It closes ONE channel (the body text).
The survivors:

- the residual — a `code`/`class`/`data-`/hidden/comment the text-writer
  forgot (`channel-body.md`, `response-diffing.md`)
- the `Location` param — `?error=`/`?e=` differing (`channel-status.md`)
- the timing — `verify()` still runs only for real (`timing-oracle.md`)
- the envelope — a `Set-Cookie`/`X-`/`attempts` field (`channel-side.md`)
- the send — the email queues only for real (`channel-side.md`)
- the lock — `423` on a real row (`account-lockout.md`)
- the OTHER forms — register/check/graphql leak (`form-surface-deep.md`)

## The dummy-hash equalization

On the miss, the app hashes a constant — equalizes the MEAN timing.
The survivors:

- the variance — a fixed dummy has a constant cost → LOWER stdev than
  the per-user real-hash stdev (`timing-statistics.md`)
- the OTHER channels — content/envelope/send/lock remain
- a dummy-hash bug — a randomized dummy re-introduces a mean gap; a
  `stdev` read detects the fixed-vs-per-user difference

## The rate-limit defense

`429`/`423` at N — bounds the spray, does NOT close the oracle:
- the `423`-on-real still leaks `exists` (`account-lockout.md`)
- a counter-key reset (XFF/session/endpoint/method) is a BYPASS —
  a finding, not a closure (`rate-limit-bypass-deep.md`)
- a window (`1/sec`) bounds but a paced sweep still runs

## The CAPTCHA defense

A challenge after N — bounds automation; the existence-oracle still
fires per-request before the CAPTCHA, and a per-form oracle on a
non-CAPTCHA'd endpoint (graphql/api) bypasses it (`evasion-deep.md`).

## The IP-ban defense

A temp block after a burst — bounds the source; a proxy/header-keyed
counter is bypassable; the existence-oracle still fires pre-ban.

## The "log-and-monitor" defense

Detection, not prevention — the oracle still fires; it just gets
logged. Not a closure, but a reason to keep the sweep bounded and
the payloads ordinary.

## The secondary-form blind spot — the structural hole

A hardened `/login` almost always coexists with a leaky:
- `check-username`/`available` — designed to reveal
- `/register` — must tell a user the name is taken
- `/reset`/`forgot` — the send-side
- `/api/users/{id}` — a resource oracle
- `/graphql` `userByEmail`/`checkUser` — a resolver oracle

The defense that equalizes `/login` rarely touches these — coverage,
not the headline, is the whole pass.

## The genuinely-closed case — what it looks like

Every form, every channel: uniform masked body, uniform status+`Location`,
uniform `-sv` envelope, equalized timing medians AND variances, no send,
no lock, no secondary-form oracle, no resolver — a real all-uniform
negative across the coverage matrix. Recorded cell-by-cell, it is a
closed class — rare, and a legitimate honest negative.
