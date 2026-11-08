# Path normalization differentials

A path is parsed at least twice: by the front proxy (routing, auth rules) and by
the backend (dispatch). Every rewrite either layer performs is a candidate
mismatch. The working request pair always differs in exactly one normalization
dimension.

## The rewrite alphabet

| Variant | Frontend sees | Backend may see |
|---|---|---|
| `/./` inside the path | literal or collapsed | collapsed to `/` |
| `//` at the start or middle | literal | collapsed to `/` |
| `%2f` / `%2F` | literal (never decoded at routing) | decoded to `/` |
| `?` inside the path or Host | path vs query boundary shifts | part of the route |
| `..;/`, `/%2e/`, `.;/` | kept literal | traversal collapsed |

Send every variant with `curl --path-as-is` (or the raw-socket equivalent) —
curl collapses `/./` and `//` client-side otherwise, which hides the very
difference being measured.

## Probe pairs that worked

**Dot-segment** (LockTalk):

```text
GET /api/v1/./get_ticket   with --path-as-is
GET /api/v1/get_ticket     plain
```

Expected: the dot-segment arm reaches a different route decision than the plain
arm — an auth rule that matched `/api/v1/get_ticket` literally did not match
the un-normalized form, while the backend dispatcher still resolved it.

**Double-slash and encoded slash** (No Threshold):

```text
GET /auth/login
GET //auth/login     with --path-as-is
GET /./auth/login    with --path-as-is
GET /auth%2f/login   with --path-as-is
```

Compare response *bodies*, not only status codes — a 200 on both arms can hide
that one reached a different handler. Falsifier: all arms return byte-identical
bodies, so normalization happens once, before auth.

**Query boundary in Host** (in-office):

```text
GET office-process?,mmoffice.x.corp HTTP/1.1
Host: office-process?,mmoffice.x.corp
```

The `?` made the frontend split path from query where the backend did not, and
the request landed on a vhost the normal form never reached.

## Falsifier

All variants produce byte-identical status and body: the layers share one
normalizer and there is no differential to exploit here — close the class and
spend the budget elsewhere.

## Traps

- An ACL can match the *normalized* path while the bypass only lives on the
  raw one — always test both arms of the pair, never just the exotic form.
- A 404 on both arms means the path is wrong, not the technique; pick the
  endpoint out of source or recon first.
