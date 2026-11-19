# Mechanism (deep-2) — the remaining model detail

## The resolution-order model — the param's journey to the Location

```text
the request arrives -> the framework parses the URL -> the param is
extracted (decoded? raw?) -> the filter checks it (at WHICH stage?) ->
the redirect is built (verbatim? decoded? joined?) -> the Location is
emitted -> the client's browser resolves it (WHATWG) -> the navigation
```

Every stage is attackable — the corpus maps the arms to the stage they
cross.

## The stage-boundary model — the decode-stage map

```text
stage 0: the raw param    ?next=https%3a%2f%2fevil.com   (URL-encoded)
stage 1: the 1st decode   https://evil.com                (the framework decodes)
stage 2: the filter check on stage-1                       (the check reads the decoded)
stage 3: the emit         Location: https://evil.com       (the verbatim pass)
stage 4: the browser      resolves https://evil.com
```

The DECODE-ORDER gap: a check at stage-0 reads the ENCODED form; a check
at stage-1 reads the decoded. The double-encoded arm `%252f` survives a
stage-1 check (`%252f` -> `%2f`) then resolves at stage-4 (`%2f` -> `/`).

## The trust-model — the issuer's authority

```text
the Location: header is the server's AUTHORITY to redirect — the client
trusts it because it trusts the server. an unchecked param makes the
server ISSUE the attacker's destination — the trust is borrowed.
```

## The mechanism-vs-sibling boundary

```text
open-redirect:   the server issues a DESTINATION — the client navigates
SSRF:            the server FETCHES a destination — the server fetches
XSS:             the param reaches a code-sink — the client executes
header-injection: the param reaches a header — the bytes split
```

The boundary is the CARRIER — a `Location:` is open-redirect; a fetched
response is SSRF; a code-sink is XSS; a header-split is injection.

## The mechanism's invariants — the class's constants

```text
- the oracle is a verbatim Location: carrying the canary — always
- the falsifier is a uniform Location: <safe> — always
- the laundered-trust is the value — always
- the parser-differential is the bypass mechanism — always
- the verbatim evidence is the proof-standard — always
```

## The mechanism-record

`mechanism-deep2: the-stage-map + the-trust-model + the-sibling-boundary`
