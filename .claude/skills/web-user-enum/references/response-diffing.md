# Response diffing — the masked raw-byte comparison, worked

## Why the rendered page lies

The browser renders the VISIBLE error. The leak is usually in the
non-rendered bytes — a `data-` attribute, a CSS class, a hidden input,
a comment, a JSON sub-field, a `Location` param. `diff` on the RAW
response finds it; the rendered page hides it.

## The three-arm capture

```bash
cj=/tmp/cj; rm -f $cj
tok() { curl -sc $cj "$FORM" | grep -oE 'name="(csrf|_token|authenticity_token)[^"]*" value="[^"]*"'|head -1|cut -d'"' -f4; }
curl -sb $cj -i -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)" "$FORM" > g
curl -sb $cj -i -X POST -d "user=$FAKE&pass=x&csrf=$(tok)"  "$FORM" > b
curl -sb $cj -i -X POST -d "user=$FAKE2&pass=x&csrf=$(tok)" "$FORM" > b2
```

`-i` keeps the headers IN the capture — the `Location`/`Set-Cookie`/
`X-` envelope is part of the diff, not just the body.

## The mask — strip the per-request noise

```bash
mask() {
  sed -E \
    -e 's/(csrf|nonce|token|_token|authenticity_token|request[_-]?id|_ts|timestamp|date)[^<"& ]*//gi' \
    -e 's/value="[^"]*"//g' \
    -e 's/[a-zA-Z0-9+/=_-]{24,}//g' \
    -e 's/[0-9]{10,}//g'
}
```

- CSRF/nonce/token/request-id/timestamp — per-request, differ every call
- `value="..."` — a fresh token embedded in a field
- long opaque strings — session ids, hashes, uuids
- long digit runs — timestamps, ids

What survives the mask is the ORACLE CANDIDATE — a stable, username-
dependent byte difference.

## The diff

```bash
diff <(mask<g) <(mask<b)     # KNOWN vs FAKE — the oracle candidate
diff <(mask<b) <(mask<b2)    # FAKE vs FAKE2 — must be EMPTY
```

- `g vs b` differs AND `b vs b2` is empty → the delta tracks the
  username-class → a real oracle
- `b vs b2` also differs → the delta is request-noise, not the username —
  a false positive; widen the mask or discard
- `g vs b` empty → the body channel is uniform

## The grep hunts — targeted residuals

```bash
# the error word / reason
grep -oiE '(error|invalid|incorrect|wrong|no such|not.found|exist|locked|disabled|pending)[^<"]*' g b
# the code / class / data- / hidden / comment
grep -oE '(error_?code|err|reason)[=": ]*[a-zA-Z0-9_-]*' g b
grep -oE 'data-[a-z-]*="[^"]*"' g b
grep -oE '<input[^>]*type="?hidden[^>]*>' g b
grep -oE '<!--[^-]*-->' g b
grep -oE 'class="[^"]*(err|error|invalid|user|exist)[^"]*"' g b
```

## The JSON diff — the structural read

```bash
curl -s -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$KNOWN\",\"password\":\"x\"}" "$API" | python3 -m json.tool > jg
curl -s -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$FAKE\",\"password\":\"x\"}"  "$API" | python3 -m json.tool > jb
diff jg jb
# {"error_code":1001} vs 1002 ; {"reason":"user"} vs "pass" ; {"exists":bool}
```

A JSON sub-field — `error_code`, `reason`, `attempts_remaining`,
`emails`, `user_exists`, a typed `errors[].code` — is the oracle the UI
never renders.

## The header diff — the envelope

```bash
diff <(sed -n '1,/^$/p' g | grep -iv 'date\|content-length\|etag') \
     <(sed -n '1,/^$/p' b | grep -iv 'date\|content-length\|etag')
# Location param, Set-Cookie, X-Auth-Reason, X-RateLimit-*, Retry-After
```

## The length heuristic — a weak hint only

`Content-Length` or `%{{size_download}` differing is a HINT to hunt, not
a verdict — equal-length responses can carry different bytes and
different-length ones can be noise. Confirm with the masked byte-diff.

## The diff verdict

`oracle: <form>:body` needs the masked `g vs b` diff to be a STABLE,
username-class delta — verified by `b vs b2` being empty and a re-run
repeating it. A single unmasked `diff` is a candidate, never a verdict.
