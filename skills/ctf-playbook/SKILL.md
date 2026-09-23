---
name: ctf-playbook
description: >
  Entry skill for any CTF challenge. Classifies the challenge, routes to exactly
  one category router, and manages time across a timed contest. Routes; never
  solves.
tags: [ctf, general, triage, strategy, playbook]
environment: [ctf, lab]
---

# CTF Jeopardy — Entry Playbook

This skill classifies and time-boxes. It does not solve. The routing table it
defers to is `../INDEX.md` and `../registry.json`.

## Step 0 — every challenge

```bash
python3 ./ctf.py --json "<observation>"            # or a source path
python3 tools/skill_select.py "<observation>"    # or --source <path>
python3 tools/chain_match.py "<observation>"     # or --source <path>
python3 tools/state.py <id> --category <cat> --target <target>
```

1. Classify, then open exactly one router. Never open two to compare.
2. Record where the flag lives, what is given, the first hypothesis and the next
   action in the ledger.
3. Estimate difficulty and set a time-box before the first probe.
4. Check chain reuse before opening any depth skill. A verified local chain with
   matching preconditions is the cheapest path there is.
5. Search public writeups once the challenge name and event are known, or when
   local evidence stops producing new hypotheses. On a known platform this is
   usually faster than blind enumeration. Record in the solved note whether the
   chain was self-derived or reproduced from a writeup.

## Signal to router

Open the thin router first; it is usually enough. A depth skill is 2,000–10,000
tokens for its index alone and its directory can exceed 100,000 — opening one
early both burns context and anchors the next hypothesis.

| Observed | Router | Depth, only after a signal |
|---|---|---|
| HTTP target or web source, endpoint, login | `../web-triage/` | one `web-*`, else `../ctf-web/` |
| Binary plus input, crash, checksec | `../pwn-binary-triage/` | `../pwn-rop/`, `../ctf-pwn/` |
| Binary whose logic must be understood, packed, firmware | `../rev-triage/` | `../ctf-reverse/` |
| Ciphertext, RSA, AES, hash, nonce | `../crypto-triage/` | `../ctf-crypto/` |
| PCAP, memory, disk, stego, logs | `../forensics-triage/` | `../ctf-forensics/` |
| LLM or chatbot, model file, IoT firmware or protocol | `../ai-iot-triage/` | `../ctf-ai-ml/` |
| Person, photo, domain, handle in public sources | `../osint-triage/` | `../ctf-osint/` |
| Jail, encoding chain, game or VM, programming task | `../ctf-misc/` | one misc reference |
| Obfuscated script, PE or .NET sample, C2 traffic | `../rev-triage/` | `../ctf-malware/` |

Unsure? Do not guess and do not open several. Re-run
`python3 tools/skill_select.py` with one more observation.

## Time management in a timed contest

- First 30 percent: sweep every easy challenge and bank the points.
- Middle 50 percent: medium challenges, plus hard ones where an idea already
  exists.
- Last 20 percent: verify and submit. Do not open a new direction.
- Time-box: easy 15–30 min, medium 30–60 min, hard 60–120 min.
- Stuck past 15 minutes: re-read the brief for a missed hint, change mechanism
  layer, then park and return. Do not sit on one challenge.
- Split categories by strength. Do not put two people on one challenge unless
  both are otherwise blocked.

## Flag format

`CTF{} FLAG{} flag{} HTB{} <brand>{}` — confirm the format the brief states
before submitting. More in `references/flag-formats.md`.

## Agent-assisted flag verification

When using an automated solver, open `references/agent-verification.md` before
accepting its output. Agent-written `flag.txt`, `evidence.txt`, and `repro.sh`
are claims until an independent verifier accepts the exact candidate. Prefer a
manifest hash or supplied `flagCheck`; otherwise preserve a verbatim live
response or artifact excerpt and pass it through the normal evidence hook.

Keep `live-response` separate from `artifact`/local reproduction. If a verifier
rejects a candidate, preserve it as rejected, do not call the flag hook, and
retry only through a bounded feedback loop. Wrapper scripts must keep `HOME`
and other process configuration variables unchanged; use a repository-specific
root variable instead.

## Frequently used one-liners

```bash
echo X | base64 -d                                    # base64
echo X | xxd -r -p                                    # hex
tr 'A-Za-z' 'N-ZA-Mn-za-m'                            # rot13
python3 -c "import urllib.parse;print(urllib.parse.unquote('X'))"
python3 -c "from pwn import *;print(cyclic(200))"     # pattern
python3 -c "from pwn import *;print(cyclic_find(b'aaXX'))"
```

More in `references/common-tools.md`.

## Discipline

- Route to the right category, then let that router lead. Do not solve here.
- One hypothesis, one decisive test, then ask whether a new signal appeared. If
  not, escalate — see `../LOOP_DISCIPLINE.md`.
- Park a class at priority 0 rather than closing it; see
  `../../HYPOTHESIS_PROTOCOL.md`.
- Keep the ledger current with `../../tools/state.py`.
- Contest rules first: if AI assistance is forbidden, this system is for practice
  beforehand, not for use during the event.
