# Status and redirect channel — the code and Location differential

## The status line as oracle

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'user=KNOWN&pass=x' "$BASE/login"
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login"
```

Differentials that count:

- `200` vs `302` — one arm re-renders, the other redirects
- `200` vs `401` / `403` / `404` — a distinct status class
- `302` vs `302` to different `Location`s — see below
- `400` vs `401` — a validation-path vs auth-path distinction
- `422` vs `401` — unprocessable vs unauthorized

## The Location differential

A `302` to `/dashboard` means success; but the interesting case is two
`302`s to DIFFERENT failure URLs:

```
known-bad  -> Location: /login?error=1
known-good -> Location: /login?error=2
```

The `?error=` parameter carries the reason — `error=user` vs
`error=pass`, `?e=1001` vs `?e=1002`, `?msg=notfound` vs `?msg=wrong`.
The redirect target IS the oracle; follow no redirect, read `Location`.

```bash
curl -s -D - -o /dev/null -X POST -d 'user=KNOWN&pass=x' "$BASE/login" | grep -i '^location'
curl -s -D - -o /dev/null -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" | grep -i '^location'
```

## The status-vs-content trap

A `200` on both arms is NOT a closed channel — the body may still differ
(channel-body). A `302` on both arms is not closed either — the
`Location` may differ. Close a channel only when BOTH the status code
AND the redirect target are byte-identical across the repeated-bad pair.

## The API status shapes

| Pair | Meaning |
|---|---|
| `404` vs `401` | resource-not-found vs unauthorized — a user-exists oracle |
| `200 {exists:false}` vs `200 {exists:true}` | a JSON boolean oracle |
| `401 "user not found"` vs `401 "bad credentials"` | a code+text oracle |
| `422` vs `401` | a validation-passed vs auth-failed distinction |
| `429` | the throttle fired — the other half of the class |

## Recording the channel

A status/redirect differential is a finding when: the SAME bad username
twice gives byte-identical status + Location, AND a second bad name
gives the same pair, AND the known-good differs on at least one. Record:
`status_good, status_bad, location_good, location_bad, repeats`.
