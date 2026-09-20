---
name: ctf-misc
description: Router for challenges outside the main categories. Identify the carrier, then open exactly one named file. Pyjails, bash jails, encodings, esoteric languages, RF/SDR, game VMs, constraint solving.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch Skill
metadata:
  user-invocable: "false"
---

# CTF Miscellaneous - router

The last resort. Try a named category first: misc is where a challenge lands when
nothing else claims it, and that is also why it is the easiest place to waste an
hour reading.

This file routes. It holds no techniques of its own - each row below names one
file, and you open one.

## First probes

Two commands, before any hypothesis. They decide the row you take.

```bash
file challenge.*            # the carrier: archive, image, capture, audio, ELF, text
xxd challenge.* | head -5   # the magic bytes, when file says "data"
```

If the input is text rather than a file, run the encoding sweep in
`toolbox.md` before guessing at a cipher.

**Falsifier** - the observation that sends you out of this category: the carrier
turns out to be a binary to exploit, a capture to reconstruct, or a cryptosystem
with parameters. Those have their own routers; see *When to Pivot* below.

## Route to depth

Open one. Never browse the directory.

| Signal | File |
|---|---|
| Nothing identified yet; need the sweep, unpacking or a hash id | `toolbox.md` |
| Text that is clearly an encoded or enciphered layer | `encoding-and-cipher.md` |
| Long or multi-stage decoding chain, esolang, BCD, UTF-16 tricks | `encodings.md` |
| Verilog, Gray code, SMS PDU, UTF-9, MaxiCode, exotic formats | `encodings-advanced.md` |
| Data hidden in an image, audio, signal, capture or column of numbers | `data-hiding.md` |
| QAM, IQ samples, carrier recovery, timing sync | `rf-sdr.md` |
| A search problem, an oracle, a protocol to drive, a constraint system | `solvers.md` |
| A Python prompt with the way out removed | `pyjails.md` |
| A restricted shell | `bashjails.md` |
| Any other restricted execution context; a shell you already hold | `jails-and-shells.md` |
| A game, an emulator, a WASM or toy VM, a save file | `games-and-vms.md` |
| More of the same, by era | `games-and-vms-2.md`, `games-and-vms-3.md`, `games-and-vms-4.md` |
| The scoreboard, a chat API, or the event platform itself | `platform-and-network.md` |
| DNS as the target: ECS spoofing, NSEC walking, IXFR, rebinding, tunneling | `dns.md` |
| CTFd, driven from the command line | `ctfd-navigation.md` |

## When to Pivot

- If the puzzle is actually centered on cryptography or number theory, switch to `/ctf-crypto`.
- If the challenge is a real binary exploit instead of a jail, toy VM, or encoding problem, switch to `/ctf-pwn` or `/ctf-reverse`.
- If the input is mostly files, images, audio, or packet captures that need recovery work first, switch to `/ctf-forensics`.
- For ML/AI techniques (model attacks, adversarial examples, LLM jailbreaking), see `/ctf-ai-ml`.

## Discipline

- Open one file from the table, not two. Re-run `tools/skill_select.py` to change
  direction rather than opening a second file to browse.
- Misc rewards identification over cleverness. If two decodings both look
  plausible, the one that produces a printable, structured result wins; do not
  build a chain on top of a guess.
- Budget: five probes or fifteen minutes per carrier hypothesis. On exhaustion,
  park the branch at priority 0 with `tools/state.py --deprioritize` and change
  carrier - never try a sixth variant of the same decode.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install z3-solver pwntools Pillow numpy requests dnslib
```

**Linux (apt):**
```bash
apt install ffmpeg qrencode
```

**macOS (Homebrew):**
```bash
brew install ffmpeg qrencode
```

**Manual install:**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`

## What each depth file holds

Carried over from the previous index, so the table above can stay short.
Open one, by name, after the table has picked it.

- [toolbox.md](toolbox.md) - identification sweep, unpacking, archive and nested-archive extraction, hash id, one-liners, technique quick references
- [encoding-and-cipher.md](encoding-and-cipher.md) - common encodings, cipher identification workflow, keyboard shift, pigpen, Unicode steganography (variation selectors, tags block), UTF-16 endianness reversal
- [data-hiding.md](data-hiding.md) - IEEE-754 float packing, ASCII in numeric columns, QR reconstruction, audio, RF/IQ, USB mouse PCAP, 3D printer nozzle tracking
- [solvers.md](solvers.md) - pwntools interaction, Z3 and constraint solving, SHA-256 length extension, Levenshtein oracle, backdoor detection in source
- [jails-and-shells.md](jails-and-shells.md) - Python jail quick reference, HISTFILE read trick, SECCOMP high-bit fd bypass, rvim escape, SUID and GTFOBins, Linux privilege-escalation checks (scope note inside)
- [platform-and-network.md](platform-and-network.md) - CTFd without a browser, Discord API enumeration, DNS exploitation summary
- [pyjails.md](pyjails.md) - Python jail/sandbox escape techniques, quine context detection, restricted character repunit decomposition, func_globals module chain traversal, restricted charset number generation, class attribute persistence, f-string config injection via stored eval
- [bashjails.md](bashjails.md) - Bash jail/restricted shell escape techniques, HISTFILE file read trick, bash -v verbose mode, ctypes.sh direct C library calls
- [encodings.md](encodings.md) - Encodings, QR codes, esolangs, UTF-16 tricks, BCD encoding, multi-layer auto-decoding, indexed directory QR reassembly, multi-stage URL encoding chains
- [encodings-advanced.md](encodings-advanced.md) - Verilog/HDL, Gray code cyclic encoding, RTF custom tag extraction, SMS PDU decoding, multi-encoding sequential solvers, UTF-9, pixel binary encoding, hexadecimal Sudoku + QR assembly, TOPKEK, MaxiCode
- [rf-sdr.md](rf-sdr.md) - RF/SDR/IQ signal processing (QAM-16, carrier recovery, timing sync)
- [dns.md](dns.md) - DNS exploitation (ECS spoofing, NSEC walking, IXFR, rebinding, tunneling)
- [games-and-vms.md](games-and-vms.md) - WASM patching, Roblox place file reversing, PyInstaller, marshal analysis, Python env RCE, Z3 (including boolean logic gate network SAT solving), K8s RBAC, floating-point precision exploitation, custom assembly language sandbox escape via Python MRO chain
- [games-and-vms-2.md](games-and-vms-2.md) - Cookie checkpoint game brute-forcing, Flask cookie game state leakage, WebSocket game manipulation, server time-only validation bypass, De Bruijn sequence, Brainfuck instrumentation, WASM linear memory manipulation
- [games-and-vms-3.md](games-and-vms-3.md) - memfd_create packed binaries, multi-phase crypto games with HMAC commitment-reveal and GF(256) Nim, emulator ROM-switching state preservation, Python marshal code injection, Benford's Law bypass, parallel connection oracle relay, nonogram solver pipelines, 100 prisoners problem, C code jail escape via emoji identifiers, BuildKit daemon build secret exploitation, Docker container escape, Levenshtein distance oracle attack, taint analysis bypass via type coercion, shredded document pixel-edge reassembly
- [games-and-vms-4.md](games-and-vms-4.md) - Part 4 (2018-era): XSLT as Turing-complete VM, JavaScript MAX_SAFE_INTEGER successor equality, binary search oracle in comparison-only DSL, blind SQLi via script-engine timeout error, OEIS sequence lookup automation, QR code reassembly from format-string constraints, matrix exponentiation for Fibonacci recurrence, Tribonacci for frog-jump counting, Selenium + Tesseract dynamic CAPTCHA, Brainfuck→Piet multi-layer polyglot, bytebeat synth code recognition
- [ctfd-navigation.md](ctfd-navigation.md) - CTFd platform API navigation without browser: detection, token auth, challenge listing, file download, flag submission, scoreboard, hints, notifications, Python client class

## Field notes

Nothing in this category has been recorded from a solve in this tree yet. When
one is, `tools/classify_solve.py` files it, and this section names the file.
