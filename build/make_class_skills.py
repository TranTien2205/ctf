#!/usr/bin/env python3
"""Generate one router card per bug class from knowledge/bug-classes.json.

Header, signals, probe and falsifier come from the taxonomy, so a skill can
never drift from the classifier that routes to it. The body below is the
technique content, written per class.

Verified classes cite the chain card that proves them. Catalogue classes say
plainly that nothing here has solved one, so a reader never mistakes standard
knowledge for local experience.

This generator OVERWRITES SKILL.md, and several of these files have been extended
by hand since they were generated -- an "Operational probe" section, a worked
example, a measured trap. A plain re-run silently deleted 169 such lines across
eight skills before this guard existed, and only `git diff` caught it. So a file
whose body no longer matches any generated body is left alone and REPORTED; pass
--force to overwrite it deliberately, after copying the hand-written part into
the BODIES entry or into field-notes.md where it will survive.
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY = os.path.join(ROOT, "knowledge", "bug-classes.json")

BODIES = {
    "web-nosqli": """## Recognise

The query takes an object, not a string. The tell is a JSON body whose value can
be replaced by a document: `{"id": "abc"}` becomes `{"id": {"$ne": null}}` and
the handler passes it straight to the driver. Mongo ids are 24 hex characters and
documents carry a version key, so both show up in responses.

## Confirm safely

Send the filter pinned to an object **you created**, with every write field
omitted. A read-safe update returns the matched documents unchanged, which proves
the filter is attacker-shaped without touching anyone else's data.

Only after that, test operators one at a time.

## The operators that matter

| Operator | What it buys |
|---|---|
| `$ne`, `$gt`, `$regex` | a boolean oracle over a field you cannot read |
| `$where` | JavaScript evaluation inside the query, when the server allows it |
| `$rename` | moves a value to a new path — including a dotted path the validator does not check |

`$rename` is the bridge to prototype pollution: schema validation usually guards
assignment paths, not rename targets. See `../web-prototype-pollution/SKILL.md`.

## Traps

- A broad filter combined with write fields rewrites every document in the
  collection. On a shared instance that destroys other players' work and can cost
  the instance. Pin the filter to your own object id, every time.
- An operator that works in the shell may be blocked by the ODM's strict mode;
  the error text usually names which.

## Operational probe

```bash
curl -i -b "$JAR" -H 'Content-Type: application/json'   -d '{"noteId": {"$ne": null}}' "$BASE/api/notes"
```

Pin the operator payload to an object you created, then read the returned set:
`$ne: null` on an id you do not own proves the operator is evaluated only if
documents you did not create come back. Record the verbatim matched-count or
the returned ids. An identical response to the baseline is a negative — the
value never reached a query operator.
""",
    "web-command-injection": """## Recognise

First prove the **sink and shell boundary**. In source, distinguish
`execFile`/argument-array execution from `shell=True`, `system`, `popen`, or a
string passed to a shell. In black-box evidence, look for command output or a
shell-specific error, not merely a slow response.

## Confirm

1. Establish one timing baseline with a harmless input.
2. Use one benign separator and a deterministic, non-destructive identity
   command available in the challenge's stated environment.
3. Compare the response body, status, and timing with the baseline.
4. If output is not returned, use a bounded timing channel and record repeated
   baseline/variant measurements. One slow request is inconclusive.

Expected confirmation is an attributable output marker or a repeatable timing
delta caused by the command. A parser error, timeout, or generic 500 is not
confirmation.

## Source decision tree

| Sink | Meaning |
|---|---|
| argument array / `execFile` without shell | command injection is falsified at this layer |
| shell-enabled subprocess or concatenated command string | continue with a read-only probe |
| template expression evaluates | route to `web-ssti`, not shell injection |
| user input only reaches a filename/API argument | inspect traversal or logic instead |

Use one named reference after the sink is confirmed:
`../ctf-web/server-side-exec.md` or `../ctf-web/server-side-2.md`.

## Traps

- Do not use destructive commands, filesystem writes, reverse shells, or broad
  network callbacks for the first probe.
- Character filtering is not the same as shell isolation; conversely, a single
  argv element is not a bypass challenge. Read the call boundary first.
- Output-free injection plus a blocked outbound channel remains inconclusive
  unless the timing delta is repeatable and attributable.

## Operational probe

```bash
curl -i -b "$JAR" -X POST "$BASE/ping" -d 'host=127.0.0.1;id'
curl -i -b "$JAR" -X POST "$BASE/ping" -d 'host=$(sleep%205)'
```

Record the verbatim output block for an injected `id`, or the measured delay
for blind sinkholes — compare against a 5x serial baseline, not a single
sample. Confirmation is command output (uid=... in the response) or a
repeatable timing delta the baseline cannot explain. A 500 or a quoted
literal is a rejected hypothesis.

""",
    "web-xxe": """## Recognise

Anything that parses XML on the server: a direct XML endpoint, a SOAP service, an
office document upload, or an SVG. The parser matters more than the endpoint —
older configurations resolve external entities by default.

## Confirm

1. Send a baseline document and record status, body length, and timing.
2. Send one harmless internal entity that points to a path the challenge
   definitely supplies. Keep the entity read-only.
3. If the response is not an echo channel, use an out-of-band URL only when the
   challenge explicitly provides a callback you control.

Expected confirmation is entity expansion in the response or an attributable
callback. A generic XML parse error does not prove entity resolution.

## Where it usually hides

Document formats are ZIP containers with XML inside: replacing one part of a
`.docx` or `.xlsx` puts your entity in front of a parser that the upload handler
never intended to expose. SVG uploads reach an image pipeline that is often an
XML parser first.

## Traps

- A blocked external DTD does not mean entities are off; parameter entities and
  local file entities may still resolve.
- Error-based extraction leaks the file through the parser's own error message
  when the response body does not echo anything.
- An uploaded document may be parsed by more than one library; identify the
  parser used by the relevant route before choosing a format-specific reference.
""",
    "web-request-smuggling": """## Recognise

Two parsers disagree about where one request ends and the next begins. In CTF web
that most often appears as **CRLF injection into a server-side fetch**: a request
value is interpolated into a URL or a header without encoding, and the control
characters survive into the outbound request.

## Confirm

One folded control character inside the interpolated value. Compare the upstream
error against an ordinary hostname. If the parser accepts the folded form, the
value is not encoded and a second request can be appended.

## Building the smuggled request

Once a control character survives, the outbound stream is yours to shape:

1. Terminate the original request line and its headers.
2. Append a complete second request, with a content length that counts the body
   bytes **exactly**.
3. Append a trailing fragment so the smuggled request is terminated and the
   connection does not hang waiting for more.

The backend is now issuing the request, which is what defeats a loopback-only
route: the caller's address is the backend's own.

## Traps

- An off-by-one content length silently drops the body or hangs the connection.
  Count the bytes, do not estimate them.
- Without the trailing fragment the smuggled request is never completed.
- A smuggled request executes as a trusted client. On a shared instance it
  changes state for everyone — know what it will do before sending it.
""",
    "web-parser-differential": """## Recognise

A proxy, gateway or WAF sits in front of the application and the two disagree
about the same bytes. The application trusts something the proxy is expected to
set — most often a client-address header — and has a fallback for when it is
missing.

## Confirm

Send the same restricted request twice: once normally, once with the proxy's own
header named in the `Connection` header. A proxy that honours hop-by-hop
semantics strips its own header before forwarding, and the application's
missing-header fallback decides the request is local.

## The general question

Always ask: **what does the trust check read, and who is supposed to set it?**
The same shape appears with path normalisation, method casing, duplicate headers,
and content-length versus transfer-encoding. If the proxy and the backend
normalise differently, the rule the proxy enforces is not the rule the backend
applies.

## Traps

- Header spoofing alone usually fails when the check reads the socket peer rather
  than a header. Read which one it is before spending the budget.
- A rule that matches an unanchored pattern, or compares with containment rather
  than equality, is bypassable without any protocol trick at all.

## Operational probe

```bash
printf 'POST /search HTTP/1.1

Host: %s

Content-Length: 4

Transfer-Encoding: chunked



5c

GPOST / HTTP/1.1



0



' "$HOST" | nc "$HOST" 443
```

Send the ambiguous request once and record **both** raw status lines — the
front-end's answer to the first request and what a second queued request
proves about where the bytes were split. Confirmation requires a response that
belongs to a request the front-end never saw (smuggled content reached the
back-end as a new request). A single error or a dropped connection is not a
differential.
""",
    "web-csrf": """## Recognise

A state-changing endpoint that accepts a request the browser will send with
credentials attached, and does not require a value the attacker page cannot read.
In CTF this is nearly always paired with a bot that visits a URL you submit.

## Confirm

Host a page that issues the request cross-origin and have the viewer load it.
Confirmation is the state change, observed from your own account or from the
endpoint's response afterwards.

## Reaching a JSON endpoint from a form

A form cannot set an arbitrary content type, but `text/plain` is allowed. The
body is `name` + `=` + `value`, so putting the opening of the JSON document in
the field name and closing it in the value produces a valid JSON body with no
encoding applied. Endpoints that parse the body by content sniff, or that accept
`text/plain`, are reachable this way.

## Traps

- Fire one route at a time. Two payloads at once — a form and a framed script,
  say — make success unattributable, and bot cycles are limited.
- Bot sessions are often re-created per visit, so a stolen credential dies fast.
  Verify it immediately.
- Check the cookie's same-site attribute before assuming the browser will attach
  it to a cross-origin request.
""",
    "web-cors": """## Recognise

The response carries an access-control origin header. The question is whether the
value is a fixed allowlist or an echo of whatever the request asked for, and
whether credentials are permitted alongside it.

## Confirm

1. Capture an authenticated baseline response without `Origin`.
2. Repeat the same request with a unique foreign `Origin`.
3. Inspect both the actual response and the preflight response, if the browser
   would preflight.

Confirmation requires the foreign origin to be reflected or accepted **and**
credentials to be allowed in a browser-usable response. A wildcard alone, or an
origin header on a public unauthenticated endpoint, is not enough.

## What to check beyond the wildcard

- A null origin, which sandboxed frames and some redirects produce.
- A prefix or suffix match rather than an exact one, which a lookalike hostname
  satisfies.
- A subdomain allowlist combined with any injection on a subdomain.

## Traps

- A wildcard origin cannot be combined with credentials by the browser, so a bare
  wildcard on a public endpoint is usually not exploitable.
- The preflight response and the actual response can differ; read both.
- Header presence is not browser exploitability: check whether the requested
  method/headers and credentials policy line up.
""",
    "web-open-redirect": """## Recognise

A parameter that names where to go next: a post-login destination, a callback, a
continue URL. The response is a redirect and the parameter is inside its
`Location` header.

## Confirm

Send one external destination and inspect the exact `Location` header without
following it. Repeat once with an encoded or parser-boundary form only if the
first result is inconclusive. Confirmation requires the server to emit a
redirect to the attacker-controlled destination.

## Why it matters in a chain

Alone it is low value. It becomes the chain when it feeds something that trusts
the destination: an OAuth redirect target, a server-side fetch, or a bot that
will visit whatever it is handed. See `../web-oauth-sso/` and `../web-ssrf/`.

## Traps

- A validator that only checks a prefix is satisfied by a hostname that starts
  with the allowed value. One that only blocks `//` is satisfied by backslashes
  or encoded forms, depending on which parser resolves the URL.
- A redirect that is immediately followed by a safe allowlist or a fixed
  relative path is not open; record the exact header before escalating.
""",
    "web-cache-poisoning": """## Recognise

A cache sits in front of the application — the response carries a cache status,
an age, or a vary header. The question is which parts of the request are in the
cache key and which are not.

## Confirm

1. Record a clean baseline from a fresh session and note cache headers, age, and
   the apparent cache key.
2. Send one harmless unique marker through a suspected unkeyed header, query
   parameter, or path normalisation boundary.
3. Request the same URL cleanly from a separate session.

Confirmation requires the marker to persist into the clean response and a cache
indicator or repeatable response comparison showing that the stored response was
reused. A marker reflected only in the immediate response is not poisoning.

## What to look for

- A header the application reflects but the cache does not key on.
- A path that normalises differently in cache and application, so a static-looking
  URL is served the dynamic response.
- A parameter the cache ignores but the application honours.

## Traps

- This is the one web class where a successful probe **affects every other
  player** until the entry expires. Use a marker that is harmless, keep the time
  to live in mind, and never poison an entry the whole challenge depends on.
- A response that varies per user is usually not cached at all; confirm the
  response is cacheable before spending the budget.
- Use a disposable path or an entry with a short, known lifetime; poisoning a
  shared flag or login page is an avoidable outage.

## Operational probe

```bash
curl -i -H 'X-Forwarded-Host: canary.invalid' "$BASE/"      # write the poisoned entry
curl -i "$BASE/"                                            # victim view, no probe header
```

Record the cache status header on both requests AND whether the canary value
is reflected in the victim response. Confirmation requires all three: the
probe request stored (HIT on the second identical request), the keyed input
left out of the cache key, and the reflected value reaching a response the
victim actually receives. A reflected header on a MISS is not a poisoning.
""",
    "web-prototype-pollution": """## Recognise

Two shapes, same mechanism: JavaScript **prototype** pollution and Python **class**
pollution. Somewhere a routine copies attacker-shaped keys onto an object without
filtering reserved ones — a deep merge, a recursive assignment, a rename, a config
loader.

The payoff is a property that some later code reads **with a fallback**. A check
that reads an optional property and treats absence as trusted is the target.

## Confirm

Pollute one harmless property, then read it back through a path that should not
have it. Do not jump straight at the gate you actually want.

## Reaching the write

| Route | Shape |
|---|---|
| Deep merge of request JSON | `__proto__` as a key in the merged object |
| Rename operator in a document store | a dotted target path under `__proto__` |
| Recursive attribute set in Python | `__class__.__init__.__globals__` to a module-level object |

A rename is the route when direct assignment is blocked: validators usually guard
assignment paths, not rename targets.

## Materialisation

Writing the pollution is not the same as applying it. A document store may only
run the prototype setter when the document is **loaded and cloned**, so the
sequence is write, then read the object back, then test the gate.

## Traps

- Pollution is global to the process. Every later request inherits it until
  restart, so on a shared instance you have changed the app for everyone. Pollute
  the narrowest property that reaches your goal.
- The values you pollute with must already exist somewhere when the write is a
  rename: create them first.
""",
    "web-race-condition": """## Recognise

Check and act are separated. A balance is read then debited, a token is issued
then re-read, a limit is counted then incremented — and nothing holds a lock
across the gap.

In source the tell is two awaits, or a read and a write, on the same record
across different functions.

## Confirm

**Two interleaved requests, not a flood.** The goal is to land the second commit
inside the window; a flood succeeds without telling you which request did it, and
a result you cannot attribute is not evidence.

Send A and B so their windows overlap, then read the state and decide which one
won.

## What makes the window wide

- The read and the write live in different functions, so extra work happens
  between them.
- An external call — email, webhook, render — sits inside the window.
- The isolation level permits the interleaving. A single transaction at a strict
  level closes the window entirely; check before spending the budget.

## Traps

- Racing a shared resource corrupts it for other players. Race an object you own.
- Parallel requests over one connection may serialise; use enough connections
  that the requests genuinely overlap.
- If the first attempt does not land, re-roll rather than escalating the rate.

## Operational probe

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem"   --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...'   --concurrency 20 --count 20 --baseline-count 5 --challenge <name>
```

Record the serial baseline FIRST: a signature that also appears serially is
not a race. Then the concurrent run — `max_in_flight`, the count of
identical-success responses, and the exact status/body split versus baseline.
Confirmation is an effect that cannot occur serially: two redeems of one
single-use code, a balance decremented past zero, a second accepted vote.
""",
    "web-logic-flaw": """## Recognise

Nothing is technically broken — the application does exactly what it was told, and
what it was told is wrong. Extra fields accepted into a model, a workflow step
that can be skipped, a coupon that can be applied twice, a role that can be set at
registration.

## Confirm

1. Record the account's own state before the request.
2. Add exactly one field the normal form does not send, or omit exactly one
   workflow step.
3. Read the state back through the account's normal view.

Confirmation requires an attributable before/after change caused by that one
field or skipped step. A success response without a state change is
inconclusive.

## Where to look first

- The model's field list versus the form's field list. The gap is the candidate.
- Any step that trusts a value the previous step produced without re-checking it.
- Anything that assumes an order the API does not enforce.

## Traps

- Logic flaws are easy to claim and hard to prove. State exactly which field or
  which skipped step produced the change, and show the before and after.
- An allowlist of assignable fields closes mass assignment completely; read the
  handler before spending the budget.
- Keep the first test on an account or object you created. Do not change roles,
  balances, or another player's records until the field boundary is proven.

## Operational probe

```bash
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-1'
curl -i -b "$JAR" "$BASE/cart"
```

Record the state before and after the malformed step, verbatim from the
response: price, quantity, role, or step position. Confirmation is a state the
application's own rules forbid — a negative total charged, a skipped step the
server accepted, an object modified beyond the caller's authority. An error
page or a silently-corrected value is a rejected hypothesis, not a near miss.
""",
    "web-oauth-sso": """## Recognise

An authorisation flow across two parties: an identity provider and the
application, joined by redirects, a code and a state parameter. Multiple session
cookies usually appear — one per party.

## Confirm

**Walk the whole flow once and record everything before changing anything**: every
redirect, every parameter, every cookie set and by whom. Most findings in this
class are visible in that transcript, and a change made before the transcript
exists is unattributable.

## What goes wrong

| Where | Shape |
|---|---|
| State parameter | not bound to the session, so a flow can be started by one party and finished by another |
| Redirect target | validated loosely, so the code is delivered somewhere it should not be |
| Account linking | identity matched on an address the attacker can also register |
| Two cookies | the application and the provider each set one, and swapping them at the right moment crosses the identities |

The last one is why the transcript matters: the exploit lives in the ordering of
cookie writes, not in any single request.

## Traps

- A registration step inside the flow can be raced; see `../web-race-condition/`.
- Changing a redirect target usually invalidates the code. Test the validation
  first with a harmless variation.

## Operational probe

```bash
curl -i -b "$JAR" -L "$BASE/oauth/callback?code=AAAA&state=BBBB"
```

Replay the callback with a `state` the provider never issued for this session,
then with the code swapped for another user's (if a second account exists).
Record the verbatim status line and any session issued. Confirmation: a
session or token issued against a mismatched state or a foreign code. A 400
naming the mismatch closes the path — record it as the falsifier.
""",
    "web-graphql": """## Recognise

A single endpoint that takes a query document. Introspection, type names, or a
query and mutation shape in the body.

## Confirm

1. Identify the endpoint and send one bounded introspection query.
2. If introspection is disabled, send one deliberately unknown field and record
   whether the error discloses a type or field suggestion.
3. Use only the names observed in the schema or error before testing an
   object-level read or mutation.

Confirmation is a schema/error oracle, not a finding by itself. The exploit
class is confirmed only when a read or mutation crosses an authorization or
validation boundary and the result is observed.

## What the schema buys

The schema is the attack surface list: every field, every mutation, every
relationship. The findings are usually the ordinary ones — an object read without
an ownership check, a mutation that should be admin-only — reached through a
single endpoint instead of many routes. Cross-check with `../web-idor/`.

## Traps

- Depth and alias limits exist; a query that is too large is rejected for size,
  not authorisation. Do not read that as a defence.
- Batched queries can bypass per-request rate limits, which matters when the
  finding needs many attempts.
- A rejected introspection query is not a secure GraphQL implementation; it only
  closes that discovery channel. Do not invent field names after a silent error.
""",
    "web-web3": """## Recognise

A Solidity source file, an RPC endpoint, and a setup contract. The challenge
usually ships a `Setup` contract with a solved condition.

## Confirm

1. Read the setup contract and solved condition first. Record the exact state
   predicate and the instance addresses.
2. Call read-only view functions and record the starting state.
3. Identify one state transition reachable by the supplied caller and predict
   its post-state before sending it.

Confirmation is the on-chain solved predicate changing after the attributable
transaction. A reverted transaction, a local simulation, or a guessed flag is
not confirmation.

## Where the routes usually are

Delegated calls that execute foreign code in this contract's storage; access
checks that read the transaction origin rather than the immediate caller;
arithmetic or accounting that can be driven to a state the author did not expect;
and any function that is reachable before initialisation.

## Traps

- The RPC endpoint and the private key are supplied per instance; nothing here is
  reusable across instances.
- Reading the deployed bytecode is often faster than reasoning about the source
  when the two might differ.
- Never assume a private key, RPC URL, or contract address from another
  challenge; use only values supplied for this instance.
""",
    "crypto-rsa": """## Recognise

The handout gives numbers, not a service: one or more moduli `n`, a public
exponent `e`, and one or more ciphertexts. Write the parameter sheet before
choosing anything — modulus bit length, `e`, how many moduli, how many
messages, and whether any value repeats across them.

## The discriminator table

Answer in order; the first yes picks the attack id for `tools/crypto_attack.py`.

| Observation | Attack id |
|---|---|
| several moduli from the same generator, none factorable alone | `batch-gcd` |
| the same message encrypted to several recipients under small `e` | `hastad` |
| one modulus reused with two exponents | `common-modulus` |
| primes `p`, `q` generated close together (`next_prime` after `p`) | `fermat` |
| `d` small, `e` full-size | `wiener`, then `boneh-durfee` below its bound |
| part of a factor or of the message known | `coppersmith-high-bits` / `coppersmith-core` |
| `e` = 3 and the message short enough that `m**e < n` | `eth-root` / `small-e-root` |
| `p - 1` smooth | `pollard-pm1` |

If only a private operation is missing — you hold `d`, `phi`, or the factors —
`factor-from-d` or `rsa-decrypt` finishes directly.

## Confirm

A recovered plaintext or factor is confirmed when it passes a check the handout
verifies by itself: `pow(m, e, n)` reproduces the ciphertext, or the product of
the recovered factors reproduces `n` exactly. A plausible-looking plaintext that
fails that check is a candidate, not a recovery.

## Traps

- Bounds are the attack. `boneh-durfee` fails silently above its `d` bound and
  `coppersmith` above its known-bits window; check the applicability line each
  attack prints before waiting on the lattice.
- A shared-prime batch needs at least two moduli; a single `n` never reaches
  `batch-gcd`.
- `e = 3` alone means nothing — the shortcut applies only when `m**e < n`, so
  padded messages route back to `hastad` or `coppersmith`.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # every attack id and its applicability
python3 tools/crypto_attack.py <attack-id> --help
```

Feed the parameter sheet, not guesses: a wrong bit length routes to the wrong
lattice bound.
""",
    "crypto-prng": """## Recognise

The generator is the target, not the cipher. Source names it (`LCG`, `LFSR`,
`mt19937`, `random.getrandbits`) or the shape does: outputs that look uniform
but repeat the generator across tickets, nonces or keys.

## Confirm

Record consecutive outputs — the attack tables index on them. Then name the
matching attack id from `tools/crypto_attack.py list`:

| Generator and what you hold | Attack id |
|---|---|
| LCG with modulus `m`, multiplier `a`, increment `c` | `lcg-recover` |
| LCG with modulus unknown but outputs untruncated | `lcg-unknown-modulus` |
| LCG leaking only high bits | `lcg-truncated` |
| LFSR keystream bits | `berlekamp-massey`, then `lfsr-predict` |
| LFSR where the taps are unknown | `lfsr-recover` |
| MT19937 with 624 consecutive 32-bit outputs | `mt19937-clone` |

Confirmation is a predicted held-back output reproduced exactly — never a
statistical argument. If the next value cannot be produced bit-for-bit, the
generator is not recovered.

## Traps

- Outputs must be **consecutive and raw**. A `mod`, a hex encoding, or a float
  division between the state and your observation changes the required count or
  breaks the clone entirely.
- MT19937 needs the full 624-word state window; 623 outputs leave you one word
  short, not one output short.
- A time-seeded generator is a seed search, not a state recovery — bound the
  seed window from the challenge's stated epoch before brute-forcing.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # id, family, applicability
python3 tools/crypto_attack.py <attack-id> --help
```

Count outputs before running anything: the applicability line on each attack
says exactly how many it needs.
""",
    "crypto-ecc-dlog": """## Recognise

The handout carries curve parameters, ECDSA signature pairs `(r, s)`, or a
discrete-log statement (`y = g**x mod p`). Name the group first — curve name,
order, generator — because the discriminator below reads differently on each.

## The discriminator

| Observation | Route |
|---|---|
| the same `r` across two signatures | `ecdsa-nonce-reuse` — closed form, no lattice |
| a nonce that is biased, short, or partially known across several signatures | `hnp` / `hnp-ecdsa` — a lattice problem |
| a group order that factors smoothly | `pohlig-hellman` |
| a small order or bounded exponent | `bsgs` — out of reach above ~2**44 |

The reused-nonce case is the most common CTF shape and the cheapest to check:
two signatures, same `r`, gives `k` in one division and the private key in one
more.

## Confirm

Re-derive the public point from the recovered scalar and compare it with the
supplied public key. A scalar that does not reproduce the public key is not the
key, whatever the algebra looked like.

## Traps

- Nonce **reuse** means identical `r`, not similar nonces. Similarity is the
  biased case and needs the lattice route with several signatures — one
  signature never feeds `hnp-ecdsa`.
- `pohlig-hellman` runs per-factor of the order; check smoothness first with
  `smoothness` before committing.
- On Weierstrass curves, validate that supplied points lie on the curve —
  invalid-curve attacks exist only when the server skips that check.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # ecdsa / dlog / lattice families
python3 tools/crypto_attack.py smoothness --help
```
""",
    "crypto-symmetric-oracle": """## Recognise

You control plaintext and read ciphertext (or the reverse through a service):
an ECB/CBC/CTR token, a MAC tag, a decrypt endpoint. The first question is
always which oracle you actually hold — encrypt, decrypt, padding-check, or
verify.

## Confirm

Detect ECB in **one** request: submit 32+ identical bytes and look for
identical ciphertext blocks. Then separate the oracle answers — an
invalid-padding response that differs from an invalid-MAC response is the whole
padding-oracle precondition.

| Oracle or reuse | Route |
|---|---|
| ECB with attacker-controlled plaintext | block cut-and-paste / chosen-plaintext dictionary |
| CBC with a distinguishable padding error | padding oracle decryption |
| a reused IV or nonce under CTR/stream | keystream reuse, `crib-drag` |
| `MD5`/`SHA1` used as `hash(secret || message)` | `length-extension` |
| two messages under one keystream | XOR them; the keystream cancels |

## Traps

- Authenticated modes close the class: GCM, or any HMAC checked **before**
  decryption, rejects a tampered ciphertext identically and no oracle exists.
- ECB needs a controlled block boundary — a fixed server prefix shifts your
  alignment by its length mod 16.
- A generic 500 is not a padding oracle. Only a response that distinguishes
  padding-bad from MAC-bad carries the signal.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # xor / hash / helper families
python3 tools/crypto_attack.py crib-drag --help
python3 tools/crypto_attack.py length-extension --help
```
""",
    "misc-interpreter-escape": """## Recognise

Input is evaluated: a pyjail, a restricted `eval`/`exec`, a filtered shell, or
a REPL that names a blocked word in its error. The error message is the first
map of the filter — read it before writing anything.

## Confirm

Map the filter **before** the escape. Send single characters and short tokens
until you know whether the check is a string blacklist, a parsed-AST rule, or a
sandbox below the interpreter. Each layer has a different escape shape:

| Filter layer | Escape shape |
|---|---|
| string blacklist on names | `getattr`, `getattr(obj, "attr"[::-1])`, `chr()` joins |
| blocked brackets or quotes | f-strings, format specs, `().__class__` chains, `subclasses()` walk |
| AST node rejection | only the grammar the checker forgot: decorators, `with`, exception args |
| shell keyword block | `$IFS`, globs, `${var:offset:1}`, command substitution |

Confirmation is code execution you observe: `id`, a read of the flag path, or
output the jail claims to forbid.

## Traps

- An AST check rejects **node types**, not strings — a blacklisted word can
  still be reachable through `__builtins__`, `getattr`, or an object that
  carries it as an attribute.
- `__subclasses__` walks are index-fragile: enumerate them at run time instead
  of hard-coding an index from a different build.
- A jail that echoes errors is free recon — quote the rejection in your notes;
  it names the exact layer.

## Operational probe

```text
1+1                     # does it evaluate at all?
"".__class__            # attribute access alive?
().__class__.__mro__    # how far does the chain climb?
globals()               # namespace readable?
```
""",
    "misc-encoding-carrier": """## Recognise

A blob with no obvious attack surface: identify the carrier **before** decoding.
Alphabet, distinct-character count, and length modulus separate base64 from
base32 from base85 from hex from base58 at a glance; the index of coincidence
separates an encoding from a classical cipher.

## Confirm

Run the standard decoders first — a blob that decodes cleanly under one of them
was an encoding, not a cipher, and the class closes. Only when every standard
carrier fails, compute IC: near the natural-language range it is a substitution
problem (`../ctf-crypto/classic-ciphers.md`); far below it suggests
polyalphabetic or layered.

| Carrier | Tell |
|---|---|
| hex | even length, alphabet `[0-9a-f]` |
| base64 | alphabet size 64, `=` padding, length ≡ 0 mod 4 |
| base32 | `[A-Z2-7]`, `=` padding in groups of 8 |
| base85 / z85 | no padding, wider symbol set |
| rot-N / Caesar | IC of natural text, shifted letter frequencies |

## Traps

- Decode **twice**: `base64(hex(...))` and friends are the standard trick.
- `+`/`/` versus `-`/`_` distinguishes standard base64 from URL-safe; wrong
  alphabet fails silently.
- An odd-length "hex" string is usually base64 *of* hex, or a nibble-aligned
  custom table — check distinct-character count, not vibes.

## Operational probe

```bash
python3 -c "import base64,binascii; d=open('blob.txt','rb').read().strip(); \
[print(n, getattr(base64,n)(d)[:60]) for n in ('b64decode','b32decode','b85decode','a85decode') \
 if __import__('contextlib').suppress(Exception) or False]"
strings blob.txt | grep -i "flag{"
```
""",
    "osint-media-metadata": """## Recognise

A media or document file is the handout and the question asks for a fact about
it — where, when, on what device, or what was inside before it was shared.

## Confirm

Read **all** of the metadata, not one guessed tag: `exiftool` prints every
group, and the answer is often in an odd corner (`ThumbnailImage`,
`HistoryParameters`, a software string). Then the container itself — `binwalk`
and `strings` find appended archives and embedded payloads that metadata never
shows.

| Evidence surface | What it answers |
|---|---|
| EXIF / XMP groups | device, time, GPS, authoring software |
| embedded thumbnail | what the image showed before a crop or blur edit |
| appended data after the format's end marker | hidden archive or second file |
| document revision/author fields | identity and edit history |

Confirmation is the fact read verbatim from the file — a guess about what a GPS
coordinate names is a hypothesis until a map source confirms it.

## Traps

- Platforms strip metadata on upload; a clean file is evidence the question is
  in the visible frame, not that you missed a flag.
- The embedded thumbnail survives edits the main image does not — compare it.
- `steghide`, `zsteg` and `outguess` cover the common carriers but are not
  installed everywhere; `binwalk -e` and `strings` are the baseline that always
  runs.

## Operational probe

```bash
exiftool -a -u -g1 <file>
binwalk -e <file>
strings -n 6 <file> | grep -iE "flag|gps|key"
```
""",
    "osint-identity-pivot": """## Recognise

The pivot is a handle, an email, a name, or a key fingerprint, and the question
asks for a different attribute of the same identity — another account, a real
name, a location, a domain.

## Confirm

Extract the **single most unique** pivot and normalise it: compute a key
fingerprint rather than eyeballing a key, derive the email pattern rather than
guessing one address. Then an ordered plan — at most six sources, each chosen
for what it can uniquely add — worked one source at a time.

| Pivot | First pivots it buys |
|---|---|
| a rare handle | other platforms where the same handle exists |
| an email | the local-part as a handle; the domain's own records |
| a name + org | professional records, conference talks, commits |
| a PGP or SSH key | keyserver uid packets, `authorized_keys` strings in repos |

Confirmation is two attributes that corroborate each other — a handle match
alone is a lead, not an identity.

## Traps

- A pivot too generic to separate from unrelated people is a measurement about
  the pivot: extract a rarer one instead of forcing the search.
- Avatars and bios get reused — a reverse image match is often a stronger pivot
  than the handle itself.
- Record every negative result with the query that produced it, so no source is
  queried twice and a later claim can cite the dead end.

## Operational probe

Work the plan, not the search bar: one query per source, verbatim results into
notes, and public sources only —
`../osint-triage/references/legal-considerations.md` bounds what is in scope.
""",
    "osint-infra-records": """## Recognise

A domain, host, or certificate is supplied and the answer lives in records —
DNS, registration, certificates, or passive aggregators.

## Confirm

Query `TXT` first — that is where a flag is actually planted — then sweep the
record types that carry data, then `whois` and the certificate subject and its
SAN list.

| Record or source | What it can carry |
|---|---|
| `TXT` / `SPF` / `DKIM` | planted strings, verification tokens, mail policy |
| `NS`, `SOA`, `CAA` | the operators behind the zone |
| `whois` | registrar, dates, contact pattern |
| certificate transparency (`crt.sh`) | every SAN ever issued — internal names included |
| `SRV`, `MX` | service discovery, mail host names |

## Traps

- A wildcard record inflates subdomain enumeration — confirm a found name with
  a real query before counting it.
- Record answers change; note the TTL and the resolver used.
- `dig`/`host` may be absent — `nslookup -type=TXT` is the fallback that exists
  nearly everywhere.

## Operational probe

```bash
dig TXT <domain> +short        # or: nslookup -type=TXT <domain>
dig ANY <domain> +short
whois <domain>
curl -s "https://crt.sh/?q=%25.<domain>&output=json"
```
""",
    "pwn-stack-overflow": """## Recognise

A native binary takes input and something reads past the buffer: `gets`, an
unbounded `scanf %s`, `strcpy`, a `read` with a length the caller trusts. The
prize is the saved return address; the first deliverable is the exact offset to
it.

## Confirm

`tools/pwn_triage.py` **first** — it reports every protection with the evidence
that decided it, and the protection sheet decides the whole chain. Then measure
the offset with a cyclic/de Bruijn pattern and prove control: the saved return
address holds your four marker bytes.

| Protection | What it changes |
|---|---|
| canary | a smashing write trips `__stack_chk_fail` before the return |
| PIE | no absolute gadget or data address until a leak lands |
| NX | the payload is code reuse — `../pwn-code-reuse/` — not shellcode |
| full RELRO | closes GOT as a write target |

## Traps

- A **static** binary can carry the `__stack_chk_fail` symbol without the check
  being enabled — read the protections report, not the string table.
- The length field may be attacker-influenced but bounded elsewhere; a read
  capped below the saved-state distance is not this class.
- Send the cyclic pattern once and record the fault address; guessing offsets
  burns the probe budget.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal
r2 -A ./chal && afl
# cyclic(offset-pattern) -> crash -> read faulted RIP, recover exact offset
```
""",
    "pwn-format-string": """## Recognise

User input lands where a format string belongs: `printf(buf)`, `fprintf(f, buf)`,
`snprintf(dst, n, buf)` with no format argument of its own. The cheapest
confirmation in pwn lives here.

## Confirm

Send a short run of `%p` and read the leaked words back — a `%p` that returns a
stack pointer confirms the primitive in one probe. Then locate your own buffer:
`AAAA.%N$p` scanning `N` until `0x41414141` returns, which fixes the argument
offset every `%n` write depends on.

| Primitive | What it buys |
|---|---|
| `%p` / `%x` reads | stack, libc and binary addresses — the leak |
| `%s` at a planted pointer | arbitrary read |
| `%n` / `%hn` / `%hhn` | arbitrary write — GOT entry, return address, `__malloc_hook` on old glibc |

## Traps

- The format argument being a **literal** closes the class — `printf("%s", buf)`
  interprets nothing.
- Full RELRO closes the GOT route; the remaining targets are the saved return
  and allocator hooks.
- On x86-64 the first several variadic arguments live in registers — the stack
  offset you measured for `%p` is not argument index zero.
- A blind format string returns no output; it needs a crash oracle and is a
  different budget, not a harder version of this class.

## Operational probe

```text
%p.%p.%p.%p            # leaked words?
AAAA.%N$p              # N where 0x41414141 returns = buffer offset
```
""",
    "pwn-heap-corruption": """## Recognise

The bug lives between allocated objects: use-after-free, double-free, an
overflow that reaches chunk metadata, or an index that reads/writes past an
allocation. The first question is never the bug — it is the allocator version.

## Confirm

Answer the glibc version first (`libc.so.6` shipped, `strings` version line, or
the challenge's stated base image): tcache behaviour, double-free detection and
fd mangling differ sharply across versions, and a technique written for 2.27
dies silently on 2.36.

| Version feature | Consequence |
|---|---|
| tcache bins (2.26+) | freed chunks go to per-thread bins first |
| tcache count check (2.29+) | naive double-free is detected |
| safe-linking (2.32+) | fd pointers are mangled — a leak is required to aim them |
| unsorted-bin leak | first free of a larger chunk leaks libc pointers |

Then map the allocation layout — which chunks you allocate, free, and in what
order — and drive the corruption to overlapping chunks or a poisoned `fd`.

## Traps

- A pointer cleared on free and bounds-checked indexes close the class — no
  freed object is reachable.
- `gdb` is absent here: `r2 -d ./chal` with `dmh` commands is the runtime heap
  view.
- Heap feng shui is order-sensitive; script the alloc/free sequence rather than
  clicking through it interactively.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal
r2 -d ./chal          # dmh, dmhf for the heap walk
```
""",
    "pwn-code-reuse": """## Recognise

This class presupposes control of the instruction pointer — a confirmed stack
or format-string overwrite — with NX on, so the payload is borrowed code, not
injected code.

## Confirm

Read the protection sheet `tools/pwn_triage.py` already produced: PIE or ASLR
decides whether a leak is needed at all, RELRO decides whether GOT is a
reachable write, and its gadget report names what the binary can express.

| Shape | Route |
|---|---|
| dynamic binary, libc supplied or leakable | ret2libc — `system`, `execve` gadgets |
| static binary | syscall gadgets or `int 0x80` |
| no `pop rdi` but `__libc_csu_init` present | ret2csu — the universal call primitive |
| write what/where needed | GOT entry, `.data`, or a `read` into a writable page |

Confirmation is the target action observed — a shell prompt, a read of the flag
path — never a clean exit after the chain.

## Traps

- On x86-64 a `ret` gadget before the final call fixes stack alignment; a chain
  that crashes inside `system` on `movaps` is an alignment bug, not a bad chain.
- The remote libc must match — leak a resolved symbol and identify the version
  (`tools/gadget_lookup.py`, libc database) before hard-coding offsets.
- `ROPgadget`/`ropper` are absent here; `r2 /R` and the `pwn_triage.py` gadget
  report are the local answer.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal      # protections + gadgets in one report
r2 -c "/R pop rdi" ./chal
```
""",
    "rev-native-check": """## Recognise

A native binary reads input and prints a verdict. The work is locating **the
deciding check** — the one comparison the flag actually passes through — and
replicating it, not describing the whole binary.

## Confirm

Locate the input read, follow the value to the comparison, and quote the
disassembly that carries it. Then replicate the check in Python and verify: a
replicated check that produces the accepted input is the solve; a described
check is not a measured one.

| Pattern | Where it usually sits |
|---|---|
| literal `strcmp`/`memcmp` | the answer is one `strings` away or one xref from the read |
| per-character transform then compare | replicate the transform in Python |
| table-driven check | dump the table, invert the mapping |
| anti-debug or packer wrapper | `../rev-triage/references/packer-analysis.md` first — the check is underneath |

## Traps

- A comparison against a value computed at run time from something you cannot
  supply means replication cannot produce the input — that is the class
  falsifier, not a harder instance.
- `radare2` is the dynamic story here: `r2 -d` debugs, `r2 -A` analyses, `pdf @
  main` disassembles. There is no `gdb`.
- Read the xrefs **to** the success/failure strings — they walk you backwards
  to the check faster than `afl` walks you forwards.

## Operational probe

```bash
r2 -A ./chal
r2 -c "afl; iz" ./chal          # functions, then strings — find the verdict text
```
""",
    "rev-managed-code": """## Recognise

The binary is managed: a PE with a non-zero CLR data directory, a `0xCAFEBABE`
class file, a dex, or a Python-packed executable. Decompilers exist for every
one of these — the job is matching the tool to the runtime.

## Confirm

Prove the runtime from the header **bytes**, quote them, then decompile with
what exists:

| Artifact | Tool family |
|---|---|
| PE + CLR directory | dnSpy / ILSpy / `ilspycmd` — and the binary often still carries unobfuscated metadata |
| `.class` / `.jar` | cfr / procyon / `javap -c` as the always-available floor |
| `.dex` / `.apk` | jadx |
| PyInstaller / py2exe bundle | extract the `.pyc`, then `../rev-bytecode-vm/` |

Confirmation is the deciding check read in decompiled form and replicated —
recompute the accepted input, do not narrate the algorithm.

## Traps

- A managed-looking binary can be a thin native stub: if the CLR directory is
  empty or the jar is only a launcher, the work belongs to `../rev-native-check/`.
- Obfuscators rename everything — follow data flow to the check, not
  identifier names.
- Single-file .NET bundles need the embedded assemblies extracted before the
  decompiler sees real code.

## Operational probe

```bash
file ./chal
rabin2 -I ./chal | grep -i clr     # CLR data directory non-zero?
strings ./chal | grep -iE "dotnet|mscoree|java|kotlin"
```
""",
    "rev-bytecode-vm": """## Recognise

The logic lives in bytecode: a `.pyc`, a `.class`, a serialised code object, or
a custom VM with its own dispatch loop. The bytecode is the program — disassemble
it, then replicate the check.

## Confirm

For `.pyc`, read the header magic and name the Python version **before** running
any decompiler — the marshal format is version-locked and a wrong-version load
crashes or silently misreads. The stdlib `dis` module on the unmarshalled code
object is the floor that always works.

| Bytecode | Route |
|---|---|
| `.pyc` matching your interpreter | `marshal.loads` past the header, then `dis.dis` |
| `.pyc` for another version | a version-matched decompiler, or read the magic and fetch that interpreter |
| custom VM | recover the opcode table from the dispatch loop, then trace |

Confirmation is the accepted input produced from the disassembly — a table you
recovered but never inverted is recon, not a solve.

## Traps

- A dispatch loop driven by a table generated **at run time** makes static table
  recovery incomplete — trace the program instead of reading the table.
- `uncompyle6`/`decompyle3` cover old Python versions only; `dis` covers the one
  installed, and the magic word says which that should be.
- `.pyc` headers are 12 or 16 bytes depending on version — skip the wrong count
  and `marshal.loads` fails before the code object even parses.

## Operational probe

```bash
python3 -c "import importlib.util,struct; d=open('x.pyc','rb').read(); \
print(d[:4].hex(), 'header', 16 if importlib.util.MAGIC_NUMBER!=d[:4] else 'check')"
python3 - <<'PY'
import dis, marshal
d = open('x.pyc','rb').read()
dis.dis(marshal.loads(d[16:]))
PY
```
""",
}


def frontmatter(entry):
    verified = entry["evidence_level"] == "verified"
    if verified:
        line = ("Verified here by %d chain card(s)." % len(entry["verified_by"]))
    else:
        line = "Catalogue class: nothing in this toolkit has solved one yet."
    confusables = ", ".join(entry.get("confusable_with", [])) or "none listed"
    description = ("Action-oriented depth skill for %s. Use after the router or "
                   "tools/classify.py names this class; start with the first probe "
                   "and record the expected signal. Do not use it as proof of a finding. "
                   "Confusable classes: %s." % (entry["name"], confusables))
    return "\n".join([
        "---",
        "name: %s" % entry["id"],
        "description: >",
        "  " + description,
        "  %s" % line,
        "tags: [%s, %s, ctf, bug-class]" % (entry["category"],
                                            entry["id"].split("-", 1)[-1]),
        "environment: [ctf, lab, authorized-testing]",
        "budget:",
        "  stuck_threshold: 3",
        "  on_stuck: pivot",
        "  stop_conditions:",
        "    - \"same probe point: 3 attempts with no new signal\"",
        "    - \"the class falsifier is observed\"",
        "evidence_level: %s" % entry["evidence_level"],
        "---",
        "",
    ])


def header(entry):
    lines = ["# %s" % entry["name"], ""]
    if entry["evidence_level"] == "verified":
        lines += ["**Verified here.** Chains that prove this class:", ""]
        lines += ["- `knowledge/chains/%s.json`" % cid for cid in entry["verified_by"]]
        lines += ["", "Run `python3 tools/chain_match.py` before this skill: a matching",
                  "chain gives you the exact confirming probe that already worked.", ""]
    else:
        lines += ["**Catalogue class.** This toolkit has never solved one. What follows is",
                  "standard published knowledge, not local experience — treat it as a starting",
                  "point and record what actually happens in `field-notes.md`.", ""]
    lines += ["## First probe", "", entry["first_probe"], "",
              "**Falsifier** — the observation that closes this class: " + entry["falsifier"], ""]
    if entry.get("blast_radius"):
        lines += ["**Blast radius** — read before any write on a shared instance: "
                  + entry["blast_radius"], ""]
    return "\n".join(lines)


def footer(entry):
    lines = ["", "## Routing", ""]
    if entry.get("confusable_with"):
        lines += ["Shares signals with: " + ", ".join(
            "`../%s/`" % c.replace("web-", "web-") for c in entry["confusable_with"])
            + ". Check those before committing to this one.", ""]
    if entry.get("depth_refs"):
        lines += ["Depth, one named file at a time:", ""]
        lines += ["- `%s`" % ref for ref in entry["depth_refs"]]
        lines += [""]
    lines += ["Signals that route here are in `knowledge/bug-classes.json`; classify with",
              "`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.",
              "",
              "## Field notes", "",
              "`field-notes.md` in this directory grows every time a challenge of this class",
              "is solved. Entries marked `proposed` are awaiting review; entries marked",
              "`confirmed` have been checked. See `../../LEARNING_LOOP.md`.", ""]
    return "\n".join(lines)


FIELD_NOTES_HEADER = """# Field notes — {name}

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---
"""


def hand_edited(skill_path, entry):
    """True when the file on disk carries prose this generator did not write.

    The header and footer are regenerated from the taxonomy every run, so they
    legitimately differ whenever a class is promoted. The BODY is the part a
    human extends, so that is the part compared: if every line of the stored
    body is still present in the file, the file is generator-shaped and safe to
    rewrite. A line that is not in the stored body is a hand edit.
    """
    if not os.path.isfile(skill_path):
        return []
    with open(skill_path, encoding="utf-8") as handle:
        text = handle.read()
    generated = set(frontmatter(entry).splitlines())
    generated |= set(BODIES[entry["id"]].splitlines())
    generated |= set(footer(entry).splitlines())
    # The header is taxonomy-derived and changes on promotion; accept any form
    # of it by accepting every line the current taxonomy would produce plus the
    # catalogue wording it may still be carrying.
    generated |= set(header(entry).splitlines())
    generated |= {
        "**Catalogue class.** This toolkit has never solved one. What follows is",
        "standard published knowledge, not local experience \u2014 treat it as a starting",
        "point and record what actually happens in `field-notes.md`.",
    }
    return [line for line in text.splitlines()
            if line.strip() and line not in generated]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="overwrite a SKILL.md that carries hand-written lines")
    args = parser.parse_args()

    with open(TAXONOMY, encoding="utf-8") as handle:
        taxonomy = json.load(handle)
    created, updated_notes, skipped = [], [], []
    for entry in taxonomy["classes"]:
        directory = os.path.join(ROOT, "skills", entry["skill_dir"])
        skill_path = os.path.join(directory, "SKILL.md")
        if entry["id"] in BODIES:
            extra = [] if args.force else hand_edited(skill_path, entry)
            if extra:
                skipped.append({"skill": entry["skill_dir"],
                                "hand_written_lines": len(extra),
                                "first": extra[0][:90]})
                continue
            os.makedirs(directory, exist_ok=True)
            with open(skill_path, "w", encoding="utf-8") as handle:
                handle.write(frontmatter(entry) + header(entry)
                             + BODIES[entry["id"]] + footer(entry))
            created.append(entry["skill_dir"])
        notes = os.path.join(directory, "field-notes.md")
        if os.path.isdir(directory) and not os.path.exists(notes):
            with open(notes, "w", encoding="utf-8") as handle:
                handle.write(FIELD_NOTES_HEADER.format(name=entry["name"]))
            updated_notes.append(entry["skill_dir"])
    result = {"skills_written": len(created), "field_notes_created": len(updated_notes),
              "skills": created}
    if skipped:
        result["skipped_hand_edited"] = skipped
        result["note"] = ("these files carry lines this generator did not write and were "
                          "LEFT ALONE. Move the hand-written part into the BODIES entry or "
                          "into field-notes.md, then re-run with --force.")
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
