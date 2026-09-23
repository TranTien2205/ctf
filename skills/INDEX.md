# Skill Index — the only routing table

This file, `skills/registry.json` and `knowledge/bug-classes.json` are the single
source of truth for which skill to open. `SKILL_GUIDE.md`, `ctf.py` and every
SKILL.md defer to them. `test/regression.py` fails if a path here does not exist,
if a skill on disk is missing from the registry, or if a bug class has no skill.

Ask the tools instead of reading these tables by eye:

```bash
python3 tools/classify.py     "<observation>"   # or --source <path>  -> bug class
python3 tools/skill_select.py "<observation>"   # or --source <path>  -> which skill
python3 tools/chain_match.py  "<observation>"   # or --source <path>  -> solved chains
```

`classify.py` names the bug class and its first probe. `skill_select.py` returns
exactly one router and at most one depth skill. `chain_match.py` says whether this
shape has already been solved here.

## Why the discipline exists

The depth corpus is roughly 622,000 tokens across 190 files. Opening
`skills/ctf-web/` alone is about 110,000. A router is 100–1,300 tokens and a
bug-class skill 500–1,200. Reading a corpus before a probe has produced a signal
costs a large share of the context window and anchors the next hypothesis on
whatever that file happened to describe.

## Load order (hard rule)

```
1 entry     ctf-playbook            classify + time-box          (always, once)
2 router    <category>-triage       signal -> class -> probe      (exactly one)
3 probe     run the cheapest discriminating probe                 (before any depth)
4 class     one bug-class skill     only after its signal fired
5 reference one named file          never a whole directory
```

Open counts: entry 1, router 1, depth 1, reference at most 2. To change category,
re-run `tools/skill_select.py`; never open a second router to browse.

## Evidence levels

Every bug-class skill declares one, and it changes how much weight its content
carries:

| Level | Meaning |
|---|---|
| `verified` | a chain card in `knowledge/chains/` proves this class was solved here |
| `catalogue` | a real, standard class that nothing here has solved yet — a starting point, not local experience |

A catalogue skill is never presented as experience. Promotion happens through the
loop in `LEARNING_LOOP.md`, never by editing the label.


## Category routers

| Observed evidence | Router | Tokens | Next |
|---|---|---|---|
| LLM endpoint, model file, IoT firmware or protocol | `skills/ai-iot-triage/SKILL.md` | ~0.9k | `ctf-ai-ml`, `mcp-agent-security`, `web-deserialization` … |
| ciphertext, modulus, nonce, hash | `skills/crypto-triage/SKILL.md` | ~0.7k | `ctf-crypto` |
| jail, encoding chain, game or VM, programming task | `skills/ctf-misc/SKILL.md` | ~2.1k | — |
| PCAP, disk, memory, media, logs | `skills/forensics-triage/SKILL.md` | ~0.6k | `ctf-forensics`, `ctf-malware` |
| name, handle, photo, domain in public sources | `skills/osint-triage/SKILL.md` | ~0.9k | `ctf-osint` |
| ELF/PE plus input, crash, checksec | `skills/pwn-binary-triage/SKILL.md` | ~0.8k | `pwn-rop`, `ctf-pwn` |
| binary, bytecode or firmware to understand | `skills/rev-triage/SKILL.md` | ~0.9k | `ctf-reverse`, `ctf-malware` |
| HTTP target, web framework, web source | `skills/web-triage/SKILL.md` | ~1.7k | `file-read-primitives`, `web-auth-session`, `web-cache-poisoning` … |

`ctf-misc` is both router and depth for its category, and it is the last
resort: try a named category first.

## Web bug classes

Open one only after a probe or a source read produced its signal.

| Class | Evidence | Closed when (falsifier) | Skill |
|---|---|---|---|
| SQL injection | verified | identical validated response for the true and the false form | `skills/web-sqli/SKILL.md` |
| NoSQL / operator injection | verified | the value is coerced to a string | `skills/web-nosqli/SKILL.md` |
| OS command injection | catalogue | the value is passed as a single argv element | `skills/web-command-injection/SKILL.md` |
| Server-side template injection | verified | the marker is reflected literally | `skills/web-ssti/SKILL.md` |
| XML external entity | catalogue | the parser is configured with entity resolution disabled | `skills/web-xxe/SKILL.md` |
| Server-side request forgery | verified | the fetch target is fixed in source and the request never influences it | `skills/web-ssrf/SKILL.md` |
| Request smuggling / CRLF injection | verified | the value is percent-encoded or validated | `skills/web-request-smuggling/SKILL.md` |
| Parser differential / proxy trust | verified | both forms are rejected | `skills/web-parser-differential/SKILL.md` |
| Cross-site scripting | verified | nothing renders the injected markup | `skills/web-xss/SKILL.md` |
| Cross-site request forgery | verified | the endpoint requires a token the attacker page cannot read or a content | `skills/web-csrf/SKILL.md` |
| CORS misconfiguration | catalogue | the allowed origin is a fixed allowlist | `skills/web-cors/SKILL.md` |
| Open redirect | catalogue | the destination is validated against an allowlist or forced to a relativ | `skills/web-open-redirect/SKILL.md` |
| Cache poisoning / deception | verified | the header is part of the cache key | `skills/web-cache-poisoning/SKILL.md` |
| Prototype / class pollution | verified | the merge rejects reserved keys | `skills/web-prototype-pollution/SKILL.md` |
| Unsafe deserialization | verified | the blob is signed with a key that is not leaked and not reachable | `skills/web-deserialization/SKILL.md` |
| Race condition / TOCTOU | verified | the read and the write happen inside one transaction or behind one lock | `skills/web-race-condition/SKILL.md` |
| Business logic / mass assignment | catalogue | the handler reads an explicit allowlist of fields and ignores everything | `skills/web-logic-flaw/SKILL.md` |
| Authentication and session | verified | the signature is verified with a key that is neither leaked nor guessabl | `skills/web-auth-session/SKILL.md` |
| OAuth / SSO flow | verified | the state parameter is bound to the session and the redirect target is a | `skills/web-oauth-sso/SKILL.md` |
| Broken object-level authorization | catalogue | the handler scopes the lookup by the authenticated owner | `skills/web-idor/SKILL.md` |
| Arbitrary file read / source disclosure | verified | the path is resolved and confined to a fixed directory | `skills/file-read-primitives/SKILL.md` |
| Unrestricted file upload | verified | the stored file is renamed | `skills/web-file-upload/SKILL.md` |
| GraphQL abuse | catalogue | introspection is off and errors reveal no field names | `skills/web-graphql/SKILL.md` |
| Smart contract / web3 | catalogue | the solved condition depends on state no external caller can change | `skills/web-web3/SKILL.md` |

Full signal lists, first probes and blast-radius notes are in
`knowledge/bug-classes.json`. Do not copy them here — the classifier reads
that file and this table would drift.

## Supporting depth skills

| Skill | Layer | Tokens | Opened when |
|---|---|---|---|
| `skills/ctf-ai-ml/SKILL.md` | depth | ~1.7k | the AI/IoT sub-type is decided |
| `skills/ctf-crypto/SKILL.md` | depth | ~2.7k | the primitive parameters are collected |
| `skills/ctf-forensics/SKILL.md` | depth | ~2.3k | the artifact type is identified |
| `skills/ctf-malware/SKILL.md` | depth | ~2.0k | obfuscated script, PE/.NET sample, or captured C2 traffic |
| `skills/ctf-osint/SKILL.md` | depth | ~2.3k | one unique pivot is extracted |
| `skills/ctf-pwn/SKILL.md` | depth | ~4.7k | the crash is reproduced and a named technique is needed |
| `skills/ctf-reverse/SKILL.md` | depth | ~3.1k | the runtime or packer is named |
| `skills/ctf-web/SKILL.md` | depth | ~2.7k | a narrower web class lacked the variant; open one named file |
| `skills/mcp-agent-security/SKILL.md` | depth | ~1.1k | the target is an LLM, an agent, or a tool server |
| `skills/pwn-rop/SKILL.md` | depth | ~0.9k | instruction-pointer control is proven and NX forces code reuse |
| `skills/web-chromedriver/SKILL.md` | depth | ~1.0k | an admin bot exists and a client-side payload needs debugging |
| `skills/web-info-disclosure/SKILL.md` | depth | ~0.7k | an exposed file, debug route, or verbose error is observed |
| `skills/web-source-map/SKILL.md` | depth | ~0.7k | the front-end bundle is the only available source |
| `skills/web-websocket/SKILL.md` | depth | ~0.8k | a ws:// channel or realtime feature carries the flag path |
| `skills/web-xs-leaks/SKILL.md` | depth | ~0.7k | an HttpOnly cookie blocks XSS and a bot visits attacker pages |
| `skills/ctf-writeup/SKILL.md` | reference | ~1.2k | a flag is verified and the chain must be recorded |
| `skills/security-skill-evaluation/SKILL.md` | reference | ~1.0k | a skill is being added, promoted, or removed |

## Skills that are not routed to automatically

`ctf-writeup` is opened after a flag is verified, to record the chain.
`security-skill-evaluation` is opened when judging whether a skill earns its
place. `ctf-malware` is reached from `rev-triage` or `forensics-triage`.
`ctf-playbook` is the entry point and is never a depth target.

## Chain reuse comes before depth

```bash
python3 tools/chain_match.py "<observation>"
python3 tools/chain_match.py --source ./challenge-src
```

A matching chain supplies a candidate and its cheapest confirming probe. It is
never proof. Scoring, preconditions and the mismatch rule are in
`HYPOTHESIS_PROTOCOL.md`.

## Adding a bug class

1. Add the class to `build/make_bug_classes.py` with signals, first probe and
   falsifier. Start it at `catalogue` unless a chain card already proves it.
2. `python3 build/make_bug_classes.py` then `python3 build/make_class_skills.py`
   to generate the skill and its `field-notes.md`.
3. `python3 build/make_registry.py` and `python3 build/make_index.py`.
4. `bash test/run_all.sh`. A class without a skill, or a skill missing from the
   registry, fails the gate.

## Adding any other skill

Directory with `SKILL.md`, an entry in `build/make_registry.py` under `PORTED`
(or hand-written in the registry), then regenerate and run the gate.
