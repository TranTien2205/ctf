# Evidence catalogue — what each finding needs verbatim

## An oracle finding — the delta, verbatim

```
form:     POST /login
channel:  body/code
KNOWN:    {"error_code":1001}
FAKE:     {"error_code":1002}
FAKE2:    {"error_code":1002}   (the second bad arm — not a one-off)
arms:     KNOWN vs FAKE differs; FAKE vs FAKE2 identical
verdict:  oracle on /login:body/code
```

The verbatim pair + the third arm. Never "it looked different" — the
raw bytes.

## A timing finding — the distribution, not one number

```
form:     POST /api/login
channel:  timing
samples:  N=12 interleaved
good_med: 247ms   bad_med: 9ms   jitter: 5ms
delta:    238ms = 47x jitter
verdict:  oracle on /api/login:timing (the verify-short-circuit)
```

A single `curl -w` is noise — the N, the medians, the jitter, the ratio.

## A throttle finding — the count or the reset

```
form:     POST /login
result:   429 at attempt 9 (8 free attempts)
bypass:   X-Forwarded-For:<rand> resets the 429 -> 200/401
verdict:  per-IP throttle at 8, bypassed via XFF
```

```
form:     POST /login
result:   no 429/423/delay in 15 requests
verdict:  throttle absent — unbounded credential loop
```

## A name finding — the oracle excerpt per name

```
oracle:   GET /api/username-available?u=
verified: admin  -> {"available":false}
          service -> {"available":false}
          flag    -> {"available":false}
          root    -> {"available":true}   (a negative — record it)
```

Every name carries its oracle excerpt; a `true`/negative is a recorded
non-name, not an omission.

## A negative — the measured cell

```
form:     POST /login
channels: body/status/side — measured uniform; timing — measured uniform
verdict:  /login is uniform on all channels — a closed form, not the class
```

A negative is a measured cell, verbatim — never "looked the same".

## The record grammar

```
enum: <form>: <channel>: <verbatim oracle>
name: <name> confirmed via <form>:<channel>
throttle: <absent|at-N|bypassed-by-<key>>
negative: <form>:<channel> uniform
route: <name> -> <neighbor-class>
```

## The evidence rule

A flag counts only from a live response through `hooks.py pre-flag`.
An oracle is a candidate until the three arms + the channel's protocol
verify it. A message the UI shows is not the raw diff. A single or
unmasked response is never a verdict.
