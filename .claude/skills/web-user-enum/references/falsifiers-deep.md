# Falsifiers (deep) — the closure logic, in full

## The full class falsifier

The class is closed ONLY when every account-touching form, on every
channel, is measured uniform:

```
for each form in {login, register, reset, forgot-user, check-user,
                  unlock, mfa, invite, api/*, graphql, users-resource}:
  for each channel in {body, status+location, timing, side-artifact}:
    assert uniform(form, channel)
```

A single uniform form does not close the class — the register may leak
where the login does not.

## The per-channel deep falsifier

### body — the masked-uniform test

`bad1`==`bad2` after masking per-request noise, AND `good`==`bad` after
the same mask → the body channel is closed. A diff that survives the
mask is a residual; a diff that is ONLY noise is closed.

### status+redirect — the identical-envelope test

Identical status code AND identical `Location` (or both absent) across
`good`/`bad1`/`bad2` → closed. A `?e=`/`?error=`/`?reason=`/`?msg=`
parameter that differs is a residual.

### timing — the sub-jitter test

median delta within ~1x jitter across N≥8, interleaved, session-pinned —
AND it does not grow on a second bad name → closed. A delta within noise
is a measured closure, not "maybe".

### side-artifact — the identical-envelope test

Identical `Set-Cookie` set, identical custom headers, identical JSON
sub-fields, and no asymmetric send/lock → closed.

## The "unmeasured, not closed" falsifier

- a diff masked by noise is UNMEASURED, not uniform — remeasure after
  masking
- a sub-N timing read is UNMEASURED — N≥8 required
- a single-arm send check is UNMEASURED — both arms needed
- a probe on only `/login` is PARTIAL — the other forms are unmeasured

Never record a closure from an unmeasured or partial read.

## The throttle falsifier

- absent is falsified by ANY `429`/`423`/captcha/delay within the burst
- "bypassed" is falsified if the spoofed request still `429`s — the
  reset did not work
- "no throttle" is falsified if the burst is <8 requests — unmeasured

## The stop rule

A channel is stopped when measured-uniform; a form when all channels
are uniform; the class when all forms are uniform. Never re-probe a
measured-closed channel — the next channel, form, or class is the move.
