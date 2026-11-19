# Evidence rules — what the map is allowed to claim

## The lead-not-finding rule

`web-source-map` produces *leads*, not findings. The evidence levels:

- **surface** — a string in the bundle, a route path, a high-entropy
  token — the client claims these exist; they are not yet real
- **class** — the endpoint responds, the secret verifies live, the
  recovered source shows a real sink — the lead is now a real target
- **impact** — the endpoint yields data it should not, the secret
  authenticates, the flag is read — the finding

A bundle string is surface evidence. It becomes class evidence only
when the live response confirms it. `hooks.py post-probe` rejects a
`confirms` verdict whose evidence is only "the bundle contains the
string".

## The two confirmation paths

**Endpoint** — the string `/api/internal` confirms when
`curl $BASE/api/internal` returns a real response (not a catch-all
404). The response is the evidence.

**Secret** — a token confirms when it *works*: the key authenticates,
the JWT is accepted, the credential grants access. A secret-shaped
string that never verifies is surface, forever.

## The flag rule still applies

A flag-shaped string in a recovered source is a *candidate* — it must
pass `tools/hooks.py pre-flag` before it is a flag:

```bash
python3 tools/hooks.py pre-flag <challenge> --value '<candidate>' \
  --source '<the recovered source or live response>' \
  --evidence '<the verbatim excerpt it was read from>'
```

A `const FLAG = "..."` in `main.js.map` is not the flag until it is
read from a live response or supplied artifact and gated.

## The verbatim-excerpt rule

A `confirms` through `post-probe` requires the evidence be a verbatim
substring of the response — for an endpoint find, the response bytes;
for a secret find, the response the secret unlocked. "I found a key in
the bundle" is not evidence; the bytes it unlocked are.

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <h> \
  --class <class> --verdict confirms \
  --evidence-kind class --evidence '<verbatim excerpt>' \
  --response '<the response bytes>'
```

## The untrusted-source rule

The bundle and map are attacker-controlled. A "source" recovered from a
map is what the build claimed, not necessarily the server's truth; a
`sources` path is a traversal candidate. Read recovered source, verify
leads live, never execute recovered code, and never present a
client-side string as a server-side fact.

## The negative-result record

A mined bundle that produced only public endpoints records its dead
ends: which strings 404'd, which secrets failed the live check, which
routes were client-only. The next solver does not re-derive them.
