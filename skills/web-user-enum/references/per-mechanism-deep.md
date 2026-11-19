# Per-mechanism (deep) — each sub-mechanism's internals

## The lookup asymmetry

`db.lookup(username)` — a `None` return vs a row. The lookup itself is
fast (~1ms); the downstream branch is the oracle:

```
user = db.get(name)
if user is None:  return invalid()        # branch A — cheap
if not verify(pw, user.hash): return invalid()  # branch B — pays verify
```

The `verify()` on branch B is the work asymmetry — the oracle reads the
branch taken.

## The hash asymmetry — the timing oracle's core

`verify(pw, hash)` for a KDF is deliberately slow — bcrypt/argon2/scrypt/
PBKDF2 burn CPU+memory to resist brute force. The `None` arm skips it.
The gap:

- bcrypt cost 10: ~60-100ms
- bcrypt cost 12: ~250ms
- argon2id: ~100-500ms
- PBKDF2 600k: ~100-300ms
- sha256/md5: <1ms — no usable gap

## The equalization defense — and its residual

```python
if not user:
    hash_dummy(pw)          # burn the same time
    return invalid()
```

The median is equalized — but the VARIANCE is not: a fixed dummy-hash
has lower stdev than a per-user variable-cost real hash. And the OTHER
channels (cookie/send/lock) still fire conditionally.

## The send asymmetry

`send_reset_email(user)` runs only on the `exists` branch — the email is
the side-effect oracle. A uniform `"if exists"` response does not
equalize the send.

## The lock asymmetry

`increment_failures(user)` / `lock(user)` writes only to a real row —
the `423 "account locked"` fires only on a real account. The lock is
itself the oracle.

## The register asymmetry

`INSERT ... ON CONFLICT` / a `unique` constraint — the duplicate-key
check returns `"taken"` for a real row, a clean insert for a fake. The
form is BUILT to reveal availability.

## The mechanism-to-channel map

- lookup → the branch → text/status
- hash → the work → timing/variance
- send → the side-effect → send channel
- lock → the write → lock channel
- register → the constraint → taken channel

Every mechanism resolves to one channel's measurement.
