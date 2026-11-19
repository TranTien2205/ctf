# Per-mechanism — each sub-mechanism's protocol

| Mechanism | What it measures | Protocol | File |
|---|---|---|---|
| existence oracle | `f(user)` differs by `exists` | 3-request differential | `mechanism.md`,`channels.md` |
| text oracle | the error body | masked raw diff | `channel-body.md` |
| status oracle | code+`Location` | `-w` code+redirect | `channel-status.md` |
| timing oracle | the hash-work gap | N>=8 median delta | `timing-oracle.md` |
| side oracle | the envelope/send | `-sv` diff + send | `channel-side.md` |
| direct exists | a check endpoint | `GET /check?u=` | `form-surface.md` |
| register-taken | the signup check | `POST /register` | `register-reset-enum.md` |
| reset-send | the send side-effect | `POST /reset` + timing/field | `register-reset-enum.md` |
| lockout | the lock-on-real-row | N attempts → `423` | `channel-side.md` |
| throttle | the loop bound | bounded burst → `429`/`423`/delay | `throttling.md` |
| throttle-bypass | the counter reset | XFF/session/endpoint/method | `rate-limit-bypass.md` |

## The mechanism-order rule

Cheapest-leak first: direct-exists > register-taken > text/status >
side > timing > reset-send > lockout > throttle. Try the one-shot
oracles before paying for a timing baseline or a lock count.

## The mechanism-coverage rule

Every sub-mechanism is a separate measurement — a uniform direct-exists
does not close a timing oracle on `/login`, and a `/login` lock does not
close a `/reset` send. Coverage is per-mechanism-per-form; the class is
closed only when every mechanism is measured on every form.
