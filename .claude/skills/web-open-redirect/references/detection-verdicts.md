# Detection verdicts — the verdict vocabulary for the redirect surface

## The candidate verdict

```text
a verbatim Location: <the-canary> — the oracle fired:
  Location: https://attacker.invalid/landing  <- the absolute canary
  Location: //evil.com                        <- the scheme-relative canary
  Location: https://target.com.evil.com       <- the subdomain-gap canary
  Location: https://evil.com/target.com       <- the substring-gap canary
  Location: https:evil.com                    <- the scheme-no-// canary
the post-probe: --verdict confirms --evidence-kind class
               --evidence 'Location: <the-verbatim>'
               --response '<the raw 302>'
```

## The negative verdict — the strong-negative

```text
a verbatim Location: <safe> on a REAL redirect param:
  Location: /dashboard         <- forced-relative
  Location: https://target.com <- allowlisted
the post-probe: --verdict negative
               --evidence 'Location: / on arm X'
               --response '<the raw>'
```

## The weak-negative verdict — the wrong-param

```text
no Location / a 200 render / a 400 on a GUESSED param:
  ?next=evil.com -> 200 render   <- 'next' isn't a redirect param here
the post-probe: --verdict negative --evidence 'no Location on ?next'
               — record as a weak-negative, NOT a class verdict
```

## The falsifier verdict — the class-closing

```text
Location: <safe> on EVERY canary + bypass arm:
  the arms-tried list + each verbatim safe Location
the post-probe: --verdict falsifies
               --evidence 'Location: / on all arms: <the-list>'
               --response '<the verbatim safe Locations>'
```

## The client-side-twin verdict

```text
a meta-refresh/JS carrying the canary:
  content="0;url=https://evil.com"     <- the meta-twin candidate
  location.href="https://evil.com"      <- the JS-twin candidate
the post-probe: --verdict confirms --evidence-kind class
               --evidence 'content="0;url=https://evil.com"'
               --response '<the HTML/meta>'
```

## The impact verdict — the chain's evidence

```text
the laundered-trust fires:
  the OAuth code on the canary's access log: 'GET /?code=<code>'
  the fetched internal content in the response
  the bot's visit logged: 'GET / ... User-Agent: <bot>'
the post-probe: --verdict confirms --evidence-kind impact
               --evidence '<the verbatim downstream evidence>'
```

## The verdict-decision matrix

| The observation | The verdict | The evidence-kind |
|---|---|---|
| `Location: <canary>` verbatim | confirms | class |
| `Location: <safe>` on the canary | negative | class |
| `Location: <safe>` on all arms | falsifies | class |
| no `Location` on a guessed param | negative (weak) | — |
| meta/JS carries the canary | confirms | class |
| meta/JS escaped | negative | — |
| the chain's downstream fires | confirms | impact |
| `Location: <relative>` (same-origin) | negative | — |

## The verdict-record

`verdict: <the-verdict>: <the-evidence-kind>: <the-verbatim-evidence>`
