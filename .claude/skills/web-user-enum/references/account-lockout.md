# Account lockout — the control that is also the oracle

## The lockout mechanism

```python
# the canonical shape — the counter lives on the user row
def login(user, pw):
    u = User.find(user)
    if u is None:
        return "invalid"          # no row -> no counter -> no lock
    if u.failed >= LOCK:           # a real row carries the counter
        return "locked"
    if u.check(pw): ...
    else:
        u.failed += 1              # only a real row increments
        return "invalid"
```

The `u.failed` counter can ONLY exist on a real row — a fake name has
nothing to increment and nothing to lock. The `423 "locked"` therefore
fires only for a real account — the lockout IS an existence oracle.

## Measuring the threshold — on YOUR account only

```bash
# YOUR OWN registered account — never a victim's
for i in $(seq 15); do
  curl -o /dev/null -w "$i %{http_code} " -X POST -d "user=$OWN&pass=wrong" "$BASE/login"
done
# -> 401 401 401 401 401 423 ... -> locks at attempt 6
```

Record `locks at N`. Never run this on a discovered/target account —
locking `admin` out is a denial-of-service on the challenge, not a
measurement.

## The lock-as-oracle

```bash
# YOUR OWN known-good vs a fake — the lock only fires on real
for u in "$OWN" "$FAKE"; do
  for i in $(seq 8); do
    printf '%s %s ' "$u" "$i"; curl -o /dev/null -w '%{http_code}\n' -X POST -d "user=$u&pass=wrong" "$BASE/login"
  done
done
# OWN -> 401..423 at N ; FAKE -> 401..401 forever => the exists-oracle
```

A `423` on a real name vs a perpetual `401` on a fake = the lock oracle,
fully confirmed by the three arms.

## The lockout differential — a subtler read

A `locked` real account returns a DIFFERENT message than a real
UNLOCKED account AND than a fake — three states, three responses:

- `admin` (real, locked): `"account is locked"`
- `admin` (real, unlocked): `"wrong password"`
- `zzz` (fake): `"invalid credentials"` or `"no such user"`

A state-message oracle — a richer signal than the binary exists/not.

## The lockout as the throttle finding

A missing lockout (no `423` in a 15-burst) = `throttle: absent-on-
lockout` — a credential-spray can run unbounded. A present lockout =
`throttle: per-account-at-N` — bounds the SPRAY per account but the
`423` still leaks `exists`.

## The unlock/oracle boundary

`POST /unlock`/`/reactivate` — `"account unlocked"` vs `"no locked
account"` is itself an existence + state oracle — `per-endpoint-
catalogue.md` carries its protocol.

## The lockout-safety rule

- only ever lock an account YOU registered (the guaranteed known-good)
- a `423` on a discovered name is recorded, never re-triggered
- the lock-as-oracle needs the lock to fire — on YOUR account, once
- a locked account is a finding (`throttle: at-N`), not a dead end
