# Body channel — the text differential, in full

## What to diff

The raw response body, byte for byte. Rendered-page comparison misses
the leak — browsers normalize whitespace, strip comments, hide hidden
inputs and `data-*` attributes, and execute the JS that might carry the
boolean.

```bash
curl -s -X POST -d 'user=KNOWN&pass=x' "$BASE/login" -o g.html
curl -s -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" -o b.html

# 1. exact byte diff
cmp -l g.html b.html | head

# 2. length delta — a 1-byte difference is a signal
wc -c g.html b.html

# 3. whitespace-insensitive — collapse runs of space
diff <(tr -s ' \t\n' ' ' < g.html) <(tr -s ' \t\n' ' ' < b.html)

# 4. extract just the message block
grep -oE '<(div|span|p|li|small)[^>]*(error|alert|msg|invalid|fail|denied)[^>]*>[^<]*' g.html
grep -oE '<(div|span|p|li|small)[^>]*(error|alert|msg|invalid|fail|denied)[^>]*>[^<]*' b.html
```

## The text shapes that leak

- `"No account named admin"` vs `"Wrong password"` — direct
- `"User not found"` vs `"Incorrect password"` — direct
- `"Invalid username"` vs `"Invalid username or password"` — a subtle
  word difference
- `"Invalid username or password."` — a trailing period present on one
  arm only
- `error_code=1001` vs `error_code=1002` — a numeric code
- `<div class="err-USERNF">` vs `err-BADPASS` — a CSS class
- `data-err="user"` vs `data-err="pass"` — a data attribute
- `<!-- user lookup failed -->` — a comment
- `<input type=hidden name=reason value=no-such-user>` — a hidden field
- `{"error":"user_not_found"}` vs `{"error":"bad_credentials"}` — JSON

## The false-positive filter — what differs but is NOT an oracle

- a CSRF token / nonce that changes every request — differs on BOTH arms;
  the pair is unpaired unless the token is held or re-fetched per-request
- a timestamp, a request-id, a CSRF-hidden-input that varies per-request
- a rotating banner/ad/CSRF — normalize these OUT before diffing; diff
  the same-bad-username twice first to find the per-request noise, then
  mask it

## The normalize-then-diff protocol

```bash
# 1. find the per-request noise — same bad user twice
curl -s -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" -o b1
curl -s -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" -o b2
diff b1 b2          # these lines vary per-request -> mask them

# 2. mask the noise, then diff good vs bad
diff <(sed 's/csrf[^<"]*//g;s/nonce[^<"]*//g' g.html) \
     <(sed 's/csrf[^<"]*//g;s/nonce[^<"]*//g' b.html)
```

The difference that survives the noise-mask is the oracle.
