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
        "tags: [web, %s, ctf, bug-class]" % entry["id"].replace("web-", ""),
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
