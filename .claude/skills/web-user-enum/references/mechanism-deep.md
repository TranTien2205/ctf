# Mechanism (deep) — the enumeration asymmetry, in full

## The code shapes that leak

### Shape 1: the honest error

```python
user = User.get(username)
if not user:
    return error("No account named " + username)
if not check(password, user.hash):
    return error("Wrong password")
```

The text is the oracle — one arm names the account, the other names the
password. This is the naive shape, rare in modern apps but common in
CTF because it is the teaching example.

### Shape 2: the "uniform" error that is not uniform

```python
if not user or not check(password, user.hash):
    return error("Invalid username or password")
```

The text is identical — but `check()` runs only on the `user` arm (the
`or` short-circuits). The **timing** differs; the body may differ by a
hidden field, a `data-` attribute, a trailing newline, or a different
error-template path. Diff the raw bytes, not the rendered page.

### Shape 3: the early-return timing oracle

```python
if not user:
    return render("login.html", msg="Invalid")   # ~1ms, no hash
# only reached for real users:
if not bcrypt.verify(password, user.hash):       # ~100ms
    return render("login.html", msg="Invalid")
```

Both arms render the SAME template with the SAME message — the only
difference is `bcrypt.verify` ran on one arm. The timing is the whole
oracle. This is the shape a competent developer writes, and it still
leaks.

### Shape 4: the timing-equalized shape that leaks elsewhere

```python
if not user:
    bcrypt.hash(password)          # burn the same time
    return invalid()
if not bcrypt.verify(password, user.hash):
    return invalid()
```

The developer burned a dummy hash to equalize timing — but the equalize
path may differ in a *side* channel: a different cache write, a session
cookie set on one arm, a log line, a `Set-Cookie` on success-path setup.
When timing is equalized, hunt the artifact channels.

### Shape 5: the registration/reset leak

The login may be uniform, but:
- **registration** rejects a taken username (`"email already registered"`)
- **reset** reveals the account (`"if that account exists…"` vs a real
  send, or an account-exists error)

The auth-adjacent forms leak what the login does not — always probe
register/reset/username-check alongside login.

## The timing math

`bcrypt(cost=12)` ~ 250ms. `argon2` ~ 100-500ms. `scrypt` ~ 50-200ms.
`pbkdf2(600k)` ~ 100-300ms. `sha256(password)` ~ <1ms — a fast-hash app
gives a weak timing oracle (sub-10ms), swamped by network jitter. The
oracle strength is the hash cost + the short-circuit gap; measure the
median delta, not a single shot.

## The measurement that makes it a signal

```
good,bad,good,bad,good,bad,good,bad   (alternate to cancel drift)
median(good) - median(bad) = delta
delta / stdev(pooled) -> significance
```

A repeatable delta > ~3x jitter is a lead; a delta that survives a
re-shuffled second run is a finding. Timing under a load balancer needs
session affinity — the requests must hit the same worker.
