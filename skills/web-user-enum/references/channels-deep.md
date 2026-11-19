# Channels (deep) — the four oracle channels, complete

## Channel 1: body — the residual hunt order

When the message is uniform, hunt these in order:
1. a numeric `error_code`/`err`/`code` — `1001` vs `1002`
2. a CSS class on the error block — `err-USER` vs `err-PASS`
3. a `data-*`/`aria-*` attribute — `data-reason="user"` vs `"pass"`
4. a hidden `<input>` — `<input type=hidden name=reason value=no_user>`
5. a comment — `<!-- user lookup failed -->`
6. a trailing byte — a period, a newline, a different template path
7. a JSON sub-field — `{"error":{"type":"user"}}` vs `{"type":"pass"}`

Each is a noise-masked raw-byte diff — `channel-body.md` is the protocol.

## Channel 2: status + redirect — the param hunt

- the code: `200`/`302`/`401`/`403`/`404`/`422`/`429`/`423`
- the `Location`: same-path-different-param — `?e=`/`?error=`/`?msg=`/
  `?reason=`/`?code=`/`?status=`/`?login=`
- a `Location` to a DIFFERENT path — `/login` vs `/dashboard` vs `/error`
- the `Location` fragment — `#error=user` vs `#error=pass`

`channel-status.md` — read `Location`, never follow.

## Channel 3: timing — the work-asymmetry + variance

- the median delta: `verify()` on the real arm — 50-500ms on KDFs
- the variance: a fixed dummy-hash's lower stdev vs a per-user real hash
- the sub-jitter caveat: a fast-hash app (<10ms delta) is unmeasurable
- the affinity caveat: pin a session to one worker under a balancer

`timing-oracle.md` — N>=8 interleaved median + jitter.

## Channel 4: side-artifact — the envelope hunt

- `Set-Cookie`: `auth_attempt`, `session`, `error`, `last_user`, a flash
- headers: `X-RateLimit-*`, `Retry-After`, `X-Auth-Reason`, `X-Error-Code`
- the send: an email/OTP that queues only for a real row
- the lock: a `423`/`locked` on a real row
- the audit: a logged `"failed login for <name>"`
- the JSON field: `attempts_remaining`, `emails_sent`, `user_exists`

`channel-side.md` — the `-sv` envelope + the send + the lock.

## The channel-coverage matrix

```
         body  status+loc  timing  side
form1    ?
form2    ?
...
```

Every cell is `oracle`/`uniform`/`unmeasured`. A form is closed when
every cell is `uniform`; the class when every form is `uniform`.
