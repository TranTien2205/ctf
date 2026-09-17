# Skill Index — the only routing table

This file and `skills/registry.json` are the single source of truth for which
skill to open. `SKILL_GUIDE.md`, `ctf.py`, and every SKILL.md defer to it.
`test/regression.py` fails if a path here does not exist, if a skill on disk is
missing from the registry, or if the registry and `ctf.py` disagree.

Ask `tools/skill_select.py` instead of reading this table by eye:

```bash
python3 ~/ctf/tools/skill_select.py "Express mongoose /update noteId flag 403"
python3 ~/ctf/tools/skill_select.py --source ./challenge-src
```

It returns exactly one router, at most one depth candidate, and the reason.

## Why the discipline exists

The depth corpus is about 622,000 tokens across 190 files. Opening `ctf-web/`
alone is roughly 110,000 tokens. A router is 100–1,200 tokens. Reading a depth
skill before a probe has produced a signal costs a large share of the context
window and biases the next hypothesis toward whatever the file happened to
describe. That is the failure this index prevents.

## Load order (hard rule)

```
1 entry     ctf-playbook            classify + time-box        (always, once)
2 router    <category>-triage       signal -> class -> probe    (exactly one)
3 probe     run the cheapest discriminating probe               (before any depth)
4 depth     one depth SKILL.md      only if the router lacked the technique
5 reference one named file          never a whole directory
```

Open counts: entry 1, router 1, depth 1, reference at most 2. To change
category, re-run `tools/skill_select.py`; do not open a second router to browse.

## Category routers

| Observed evidence | Router | Tokens | Next |
|---|---|---|---|
| HTTP target, web framework, web source | `skills/web-triage/SKILL.md` | ~1.0k | one `web-*` depth |
| ELF/PE + input, crash, checksec | `skills/pwn-binary-triage/SKILL.md` | ~0.1k | `pwn-rop`, `ctf-pwn` |
| Binary/bytecode/firmware to understand | `skills/rev-triage/SKILL.md` | ~0.7k | `ctf-reverse`, `ctf-malware` |
| Ciphertext, modulus, nonce, hash | `skills/crypto-triage/SKILL.md` | ~0.4k | `ctf-crypto` |
| PCAP, disk, memory, media, logs | `skills/forensics-triage/SKILL.md` | ~0.4k | `ctf-forensics` |
| Name, handle, photo, domain in public sources | `skills/osint-triage/SKILL.md` | ~0.7k | `ctf-osint` |
| LLM endpoint, model file, IoT firmware/protocol | `skills/ai-iot-triage/SKILL.md` | ~0.6k | `ctf-ai-ml`, `web-deserialization` |
| Jail, encoding chain, game/VM, programming | `skills/ctf-misc/SKILL.md` | ~5.8k | one misc reference |

`ctf-misc` is both router and depth for its category, and it is the last resort:
try a named category first.

## Web depth selection

Open one of these only after a probe produced the signal in the middle column.

| Class | Signal that unlocks it | Depth skill |
|---|---|---|
| SQL injection | SQL error, boolean delta, or timing delta | `skills/web-sqli/SKILL.md` |
| SSRF | server fetches a request-controlled URL, or a bot visits one | `skills/web-ssrf/SKILL.md` |
| SSTI | arithmetic marker evaluated, template error string | `skills/web-ssti/SKILL.md` |
| XSS | marker reaches an HTML/JS/DOM context with a viewer | `skills/web-xss/SKILL.md` |
| IDOR | second identity reads or writes the first identity's object | `skills/web-idor/SKILL.md` |
| File upload | stored file is later served, parsed, or executed | `skills/web-file-upload/SKILL.md` |
| Auth/session | token, JWT, signed cookie, or role gate decides flag access | `skills/web-auth-session/SKILL.md` |
| Deserialization | serialized blob crosses a trust boundary | `skills/web-deserialization/SKILL.md` |
| File read | read primitive proven, source/config/flag path unknown | `skills/file-read-primitives/SKILL.md` |
| Anything not covered | the depth skill lacked the variant | one named file in `skills/ctf-web/` |

## Skills that are not routed to automatically

`ctf-writeup` is opened after a flag is verified, to record the chain.
`ctf-malware` is opened from `rev-triage` or `forensics-triage`, never directly.
`ctf-playbook` is the entry point and is never a depth target.

## Chain reuse comes before depth

Before opening any depth skill, ask whether a chain already solved here matches:

```bash
python3 ~/ctf/tools/chain_match.py "<observation>"
python3 ~/ctf/tools/chain_match.py --source ./challenge-src
```

A matching chain supplies a candidate and its cheapest confirming probe. It is
never proof. Scoring, preconditions, and the mismatch rule are in
`HYPOTHESIS_PROTOCOL.md`.

## Adding or renaming a skill

1. Add or move the directory with its `SKILL.md`.
2. Add the entry to `skills/registry.json` with `use_when` and `do_not_use_when`.
3. Add the row to this file.
4. Run `bash ~/ctf/test/run_all.sh`. A skill missing from the registry, or a
   registry path missing from disk, fails the gate.
