# Negative results — what a dead end looks like, recorded

## The dead-end shapes

### All forms uniform

```json
{"form":"/login","body":"uniform(masked)","status":"200/200",
 "location":"identical","timing":"good_med=9ms bad_med=8ms jitter=3ms",
 "side":"identical","verdict":"no oracle on /login"}
```

Recorded per-form, not "the app doesn't enumerate" — the register or
reset may still leak.

### A throttle present

```json
{"form":"/login","limit":"423 Locked at 6 per-account","verdict":
 "throttle present — the enum loop is bounded at 6"}
```

The lock IS the control — record the threshold as a negative for
unbounded enum and a positive for a lockout oracle (the lock only fires
on a real row — still an enum signal).

### A one-shot anomaly that did not repeat

```json
{"form":"/reset","anomaly":"'server error' once on bad user","re_send":
 "identical to good","verdict":"a crash, not a differential"}
```

The anomaly was a crash/CSRF/noise, not an oracle — record it as a
closed lead.

### Timing lost to jitter

```json
{"form":"/api/login","delta":"good_med=11ms bad_med=9ms jitter=8ms",
 "verdict":"sub-jitter delta — weak-hash app, no usable timing oracle"}
```

The delta is real but unmeasurable — record as a closed timing channel.

## The falsifier-that-fired record

Every dead lead carries WHICH falsifier fired:

- `uniform: all channels identical across bad1==bad2`
- `no-repeat: anomaly absent on re-send`
- `sub-jitter: delta within noise floor`
- `throttle: 423 at 6 — loop bounded`
- `masked: per-request noise swallowed the diff — remeasure`

## What a clean negative is

A form measured uniform on all four channels (masked body, identical
status+Location, sub-jitter timing across N≥8, identical envelope) is a
PROVEN dead end — the next solver does not re-probe it. A form "not yet
measured" is not a negative; it is a gap.

## The chain the negative still feeds

A "no oracle on /login" is dead for enum but still feeds:
- `register`/`reset` — probed next, may still leak
- `web-auth-session` — a uniform login is itself a (weak) hardening signal
- `knowledge/attempts/` — the kill map records it so the next attempt
  does not re-walk it
