# Negative results — what to record when the redirect isn't there

## The negative taxonomy

```text
weak-negative   <- a guess produced a null/no-Location response;
                   the param name was wrong — NOT a class verdict
strong-negative <- a verbatim `Location: <safe>` on the canary; the
                   param IS a redirect but validated — a class verdict
uniform         <- `Location: <safe>` on EVERY bypass arm — the filter
                   holds — the class falsifier
```

## The weak-negatives — the wrong-param guesses

```text
?next=https://evil.com   -> 200, no Location          -> next isn't the param
?url=https://evil.com    -> 400 Bad Request            -> url rejected outright
?redir=...               -> a Location:/dashboard (fixed) -> not this param
?return=...              -> 200 page render            -> not a redirect param
```

A `200 render`/`400`/no-`Location` on a guessed param is a weak-negative —
the param name was wrong; move to the next name, don't conclude.

## The strong-negatives — the measured validation

```text
?next=https://evil.com        -> Location: /       <- forced-relative
?next=//evil.com              -> Location: /       <- the // rejected
?next=https://target.com.evil.com -> Location: https://target.com/ <- allowlisted
?next=evil.com\@target.com    -> Location: /       <- normalized
```

A verbatim safe `Location:` on a REAL redirect param is a strong-negative —
the param is a redirect but the validation holds for that arm.

## The uniform falsifier — the arms all fail the same way

```text
?next=https://evil.com           -> Location: /
?next=//evil.com                 -> Location: /
?next=/\evil.com                 -> Location: /
?next=%5c%5cevil.com             -> Location: /
?next=https://target.com@evil.com -> Location: /
?next=evil.com/target.com        -> Location: /
?next=https:%2f%2fevil.com       -> Location: /
?next=javascript:alert(1)        -> Location: /
```

Every arm → the SAME safe `Location: /` — the uniform falsifier — the
validation holds across all parser boundaries. This is the class-closing
observation.

## The different-failure-modes ledger

| The arm | The Location | The meaning |
|---|---|---|
| `https://evil.com` | `Location: /` | external blocked |
| `//evil.com` | `Location: /` | scheme-relative blocked |
| `/\evil.com` | `Location: /` | backslash normalized |
| `javascript:...` | `400` | the scheme rejected |
| `evil.com\@target.com` | `Location: /` | the `@` normalized |
| `https://target.com.evil.com` | `Location: https://target.com.evil.com` | **the suffix arm PASSED** — a subdomain allowlist gap |

One arm passing while others fail is the MECHANISM fingerprint — the
fingerprint names the filter shape.

## The client-side negatives

```text
?url=https://evil.com  -> <meta content="0;url=https://evil.com">
                          -> a META redirect carrying the canary — a
                             client-side-twin CANDIDATE, not a negative
?url=https://evil.com  -> window.location="/safe"
                          -> a JS sanitized — a negative for the JS carrier
?url=https://evil.com  -> <a href="/x?url=...">  <- reflected, not a redirect
```

## The chain-negative — the redirect confirms but doesn't launder

```text
Location: https://evil.com   <- the open-redirect CONFIRMS
BUT: the OAuth redirect_uri is strict -> the OAuth chain is a chain-negative
     the fetcher doesn't follow -> the SSRF chain is a chain-negative
     the bot doesn't run JS for a meta -> the bot chain is a chain-negative
```

The class-confirmed-but-chain-dead is a chain-negative — record the class
confirm AND the chain's failure separately.

## The negative-record

```bash
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <id> --class web-open-redirect \
  --verdict negative \
  --evidence 'Location: / on https://evil.com and //evil.com' \
  --response '<the verbatim safe Location>'
```

## The kill-map entry — when the class is fully closed

```json
{
  "challenge": "<name>", "class": "web-open-redirect",
  "verdict": "closed",
  "arms_tried": ["https://evil.com", "//evil.com", "/\\evil.com",
                 "%5c%5cevil.com", "userinfo", "subdomain", "javascript:"],
  "uniform_response": "Location: / on all arms",
  "falsifier": "the destination is validated against an allowlist or forced to a relative path",
  "reopen_precondition": "a redirect param on a different endpoint / a stored-redirect / a Referer-derived surface not yet swept"
}
```
