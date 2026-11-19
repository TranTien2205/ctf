# Second-order enumeration — the indirect existence leaks

## The referral/invite graph

An app where a user can invite/refer — `POST /invite {email}`:
- `"already invited"`/`"already registered"` → the email exists
- `"invite sent"` → does not exist (yet)
- a referral count/`{referrals:N}` → a real account's graph

## The contact/mention oracle

`POST /contact`/`@mention`/`share`:
- `@alice` autocompletes to a real user → `alice` exists
- a `share with <user>` autocomplete/`POST /share {to:user}` —
  `"user not found"` vs a shared confirmation
- a `POST /message {to:user}` — `"no such user"` vs accepted

## The public-content oracle

A real account's public footprint — the user-generated content:
- `/author/<name>` `/u/<name>` `/profile/<name>` `200`/`404`
- a blog `Posted by <name>` / a forum post count / a `member since`
- a `GET /users/<name>/posts` — `200`+posts for real, `404` for fake
- a `/api/users/<name>/activity`/`/repos`/`/gists` — the per-user feed

## The follower/friend oracle

`GET /users/<name>/followers` `200`/`404`; `POST /follow {user}` —
`"no such user"` vs a follow confirmation; a friend-request error —
the social-graph oracle.

## The search oracle

`GET /search?u=<name>`/`/users/search?q=` — returns the user row for a
real name, `[]`/`no results` for a fake — a search-driven exists-oracle,
and a `web-info-disclosure`/`web-idor` read of the returned fields.

## The autocomplete/typeahead oracle

`GET /autocomplete?u=<prefix>`/`/typeahead?user=` — a real user appears
in the suggestion list — a prefix-based oracle that enumerates the
whole namespace one prefix at a time.

## The last-login/last-seen oracle

`GET /users/<name>`/`/profile/<name>` carrying `last_login`/`last_seen`/
`online` — a real account has activity; a `null`/`never`/`404` marks a
fake. The field is the oracle + a `web-info-disclosure` leak.

## The registration-side second-order

A `POST /register` with a TAKEN email/username that returns a different
error than a free one — already covered (`register-reset-enum`), but the
SECOND-order variant: `"an account with this email already exists —
sign in instead"` leaks the login-form as well.

## The team/org-membership oracle

`GET /orgs/<org>/members`/`/teams/<team>/users` — a membership list;
`POST /orgs/<org>/members {user}` — `"user not found"` vs added — the
org-scope oracle.

## The comment/mention notification

`POST /comment {text: "@alice hi"}` — the `@alice` mention that sends a
notification only for a real user → the send-side second-order oracle.

## The second-order boundary

- `web-user-enum` — the indirect exists-oracle (autocomplete/search/
  content/graph/invite/mention)
- `web-info-disclosure` — the public data the oracle also leaks
- `web-idor` — the object/resource the oracle returns
- `web-auth-session` — the account the oracle confirms

The second-order oracle is often UN-throttled (a feature, not a login)
— a cheaper, quieter existence measurement than the auth path.
