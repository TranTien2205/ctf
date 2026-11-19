# Spray patterns and list strategy — bounded, measured, recorded

## The two distinct loops — do not conflate

| Loop | Purpose | Budget owner |
|---|---|---|
| **enum** — `?u=<name>` once per candidate | measure `exists` | this class |
| **spray** — `login(user, pw)` per (name × pw) | guess credentials | `web-auth-session` |

The enum's loop measures the oracle; the spray guesses passwords. A
confirmed account list is the enum's OUTPUT; the spray is the
neighbor's INPUT. Do not run a password loop inside `web-user-enum`'s
budget — that is `web-auth-session`'s, and it is exactly what the
throttle stops.

## The enum-list — bounded and ranked

Through a confirmed oracle, run the candidate list ONCE per name:

```bash
for u in admin administrator root test demo user guest flag service \
         backup deploy system support operator monitoring superuser \
         sa ci jenkins gitlab sonar nexus vault consul grafana; do
  printf '%-14s ' "$u"; curl -s "$BASE/api/username-available?u=$u"
done
```

`{"available":false}`/`200`/`{id}`/`null`→`exists` — each `false`/`200`
is a verified name; each `true`/`404` is a recorded negative.

## The ranking — by chain-value, not list-size

- `flag`/`flaguser`/the-challenge-name — the flag holder, highest value
- `admin`/`administrator`/`root`/`superuser` — the privileged path
- `service`/`backup`/`deploy`/`ci`/`jenkins`/`gitlab`/`monitoring` —
  service accounts, often default-cred
- `test`/`demo`/`user`/`guest` — the low-privilege foothold
- a discovered name from the bundle/source/content — the real account

## The app-leaked list — higher value than a wordlist

`username-sources.md`/`username-sources-deep.md` — the bundle's
`currentUser`/`author`/`created_by` fixture, a source `INSERT INTO
users`, a `seed`, a content `Posted by`, a `mailto:` — these name REAL
accounts and outrank a generic wordlist. Mine them before the seeded
set.

## The wordlist — bounded, scoped, authorized

On an authorized target with a confirmed oracle and NO throttle (or a
bypassed one), a bounded wordlist slice:

- `SecLists/Usernames/top-usernames-shortlist.txt` — the short slice
- `xato-net-10-million-usernames` — a SLICE, never the whole
- the service-specific set (ci/jenkins/gitlab/vault/...)

Never a mass wordlist on a shared/victim target — that is the abuse a
throttle exists to stop. The oracle is proven with 3 requests; the
list is bounded by the throttle measurement and the challenge scope.

## The spray — `web-auth-session`'s loop, briefly

Once the enum hands off a verified name list, the credential attack:

```bash
# ONE common password per confirmed account — stays under a per-account lock
for u in admin service backup; do
  curl -o /dev/null -w "$u %{http_code}\n" -X POST -d "user=$u&pass=Password1" "$BASE/login"
done
# a session on one -> web-auth-session owns the post-login
```

One password per account, under the measured per-account lock — the
password-spraying pattern. A `200`/`302`/session = a valid credential →
`web-auth-session`.

## The bounded-burst rule

The throttle MEASUREMENT is a ~15-request burst to see whether a `429`/
`423`/delay appears — measurement, not attack. A real brute-force
(many requests) is out of scope for a read-first recon skill and is
what the throttle finding reports. Record `absent`/`at-N`/`bypassed`;
do not run the unbounded loop inside the enum's budget.
