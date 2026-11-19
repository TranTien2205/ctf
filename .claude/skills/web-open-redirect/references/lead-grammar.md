# Lead grammar — the observation-to-hypothesis phrasing

## The lead-shape — the observation phrasing

```text
the lead is a phrased observation: "<the-surface> suggests <the-class>
because <the-signal>" — never "there's an open-redirect" without the
verbatim Location evidence
```

## The signal-to-lead grammar

| The observation | The lead phrasing |
|---|---|
| `?next=` exists + a 302 | "the `next` param reaches a `Location:` — the open-redirect surface; check the verbatim Location for the canary" |
| `Location: <canary>` | "the `Location:` carries the canary — a CANDIDATE open-redirect; post-probe confirms" |
| `Location: <safe>` | "the `Location:` is safe — the arm is blocked; the filter fingerprint is X; try the Y arms" |
| `Location: <partial>` | "the `Location:` is a partial — a host/path-force; the substring/@/suffix arms apply" |
| no `Location:` | "no `Location:` — the param isn't a redirect carrier; the client-side twin?" |
| a meta-refresh | "a meta-refresh carries the param — the client-side twin surface" |
| a `location.*` sink | "a DOM-source `location.*` sink — the client-side redirect" |
| a Referer-carried | "the `/back` reads the Referer — a Referer-derived redirect" |
| an OAuth `redirect_uri` | "an OAuth `redirect_uri` — the allowlist surface; check for an open-redirect on the allowlisted domain" |
| a fetcher + the redirect | "a fetcher — does it follow `Location`? the SSRF-chain surface" |

## The hypothesis-shape — the phrased hypothesis

```text
hypothesis: the <endpoint>?<param>= redirect-param is unchecked — the
            server emits an attacker-controlled Location; the falsifier is
            'Location: <safe> on every arm'
```

```python
# the hypothesis-record — the ledger's hypothesis
{
  "id": "h-or-1", "class": "web-open-redirect",
  "statement": "the /login?next= param is an unchecked redirect",
  "the_probe": "curl -si '$BASE/login?next=https%3A%2F%2Fevil.com' | grep -i location",
  "the_falsifier": "Location: / on every bypass arm",
  "the_chain_route": "the post-auth phishing launder",
  "budget": 5
}
```

## The verdict-grammar — the phrased verdict

```text
the verbatim-evidence phrasing:
  "confirms — the Location: header carries 'Location: https://attacker.invalid'
   verbatim (the 302 response)"
  "negative — the Location: is 'Location: /' — a forced-relative arm-block"
  "falsifies — 'Location: /' on every arm: canary, //, \, %5c, @, subdomain,
   javascript: — the allowlist/relative-force holds"
```

## The chain-lead grammar

```text
"the open-redirect confirms AND the allowlisted redirect_uri domain is X
 — the OAuth-code launder route"
"the open-redirect confirms AND a fetcher follows Location — the SSRF route"
"the open-redirect confirms AND the sink accepts javascript: — the XSS route"
```

## The reclassification-grammar — the lead that routes elsewhere

```text
"the param is FETCHED not redirected -> web-ssrf"
"the javascript: reaches a DOM-sink -> web-xss"
"the redirect_uri is the OAuth surface -> web-oauth-sso"
"a %0d%0a splits the Location -> web-request-smuggling"
"the \@/%5c parser-gap is the mechanism -> web-parser-differential"
```

## The grammar-record

`lead: <the-observation> -> <the-hypothesis>` — each observable's hypothesis.
