# Onboarding (deep) — the complete first-session guide

## The contract — read first

```text
the class: CATALOGUE — no local solve; the corpus is published knowledge
the first probe: one external destination, follow=False, read the Location
the falsifier: Location: <safe> on EVERY canary + bypass arm
the evidence: the verbatim Location: header — nothing else confirms
```

## The 15-minute map

```text
0-3   read the contract + the first-probe
3-6   the param sweep — the vocabulary
6-9   the canary — the fingerprint
9-12  the arms — the filter-shape family
12-15 the verdict — confirm / falsifier / negative
```

## The concepts — the mental model

```text
a redirect-param is a request value that lands in a Location:/meta/JS —
the server emits a DESTINATION; unchecked, the client is sent to the
attacker's host. The value is the LAUNDERED TRUST — the redirect feeds
an OAuth/SSRF/XSS/bot/phishing chain.
```

## The vocabulary — the terms

```text
the canary        the attacker-controlled destination — https://attacker.invalid
the Location      the 3xx response header — the oracle
the carrier       the redirect mechanism — Location/meta/JS/Refresh
the fingerprint   the ONE Location on the first canary — names the filter
the arm           a bypass payload — //, /\, @, \@, subdomain, encoded, ...
the uniform       the same safe Location on every arm — the falsifier
the launder       the downstream trust the redirect feeds
```

## The first reads — the files to open in order

```text
1. quick-reference.md      the 60-second pass
2. detection.md            the signals
3. decision-table.md       the fingerprint -> the arm
4. filter-bypass-deep.md   the bypass corpus
5. evidence-rules.md       the verbatim standard
6. falsifiers.md           the class-closing
```

## The first probe — the hands-on

```bash
# the canary — the first thing you do
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid" | grep -i location
# the fingerprint — read the Location
# the arms — the filter-shape family
curl -si "$BASE/login?next=%2f%2fevil.com" | grep -i location
```

## The mental checklist

```text
- is the param a redirect?        -> the Location exists
- is the destination unchecked?   -> the canary lands in the Location
- is the filter named?            -> the fingerprint -> the arms
- is the class closed?            -> the uniform safe Location
- is the chain open?              -> the laundered-trust route
```

## The discipline — the rules that keep you honest

```text
- ONE param, ONE carrier, ONE arm at a time
- the verbatim Location is the evidence — never "it redirected"
- a safe Location on one arm is a negative, not a falsifier
- a uniform safe Location on ALL arms is the falsifier
- a confirmed canary routes to the chain — the class alone is rarely the flag
- the class is CATALOGUE — the local confirm is the verbatim Location
```

## The escalation — what to do when stuck

```text
stuck on the param?      -> the vocabulary sweep — param-inventory.md
stuck on the carrier?    -> the meta/JS/Referer/stored — client-side.md
stuck on the filter?     -> the residual arms — evasion.md
stuck on the chain?      -> the route-preconditions — chain-routes.md
the class is closed?     -> the falsifier — record + move to the next surface
```

## The record — the ledger entries

```bash
# a candidate
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid' --response '<the 302>'
# a falsifier
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict falsifies \
  --evidence 'Location: / on all arms' --response '<the safe 302s>'
```
