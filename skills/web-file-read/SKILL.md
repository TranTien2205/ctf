---
name: web-file-read
description: Prove arbitrary file read or path traversal with a sentinel and its control — depths, encodings, prefix and suffix defeats, and what counts as a known file. Use when a parameter names a file, a template, a locale, a page or an attachment.
classes: lfi
---

# Arbitrary file read

Proof requirement: **a sentinel from a file whose contents are known, plus the
control request for a path that cannot exist.** Both records, or the grade stays
`supported`.

## Why the control is half the proof

Without it, a 200 containing text proves nothing: you do not know what the
endpoint returns for a path that is missing, for a path that is forbidden, or for
a path that exists but is not readable. One request fixes all three. The
`proof.file_read` tool issues it for you against `/etc/argus-<nonce>-does-not-exist`
and stores it as a `control` record.

## The sweep that finds it

`proof.file_read` walks depth against encoding automatically. What it tries, and
why each exists:

| shape | defeats |
|---|---|
| `/etc/passwd` | nothing — but an absolute path works more often than people expect |
| `../`, `../../`, up to six | a path joined to a root, at unknown depth |
| `....//` | a naive single-pass `../` stripper |
| `..%2f`, `%2e%2e%2f` | a filter that runs before URL decoding |
| `..%252f` | a filter that runs after one decode, where two happen |

What the sweep cannot guess, and you must supply:

- **A prefix the application prepends.** `/var/www/uploads/<value>` means you
  need to climb out of `uploads` first; count the segments from the error text or
  from the bundle.
- **A suffix it appends.** `<value>.html` is defeated by a null byte only on very
  old stacks; far more often the answer is a path that genuinely ends in that
  extension, or a directory traversal into a file that does.
- **An extension allowlist.** Read the code path if you have it. Guessing
  encodings against an allowlist is the most common way to spend twenty requests
  on a parameter that was never the one.

## What counts as a sentinel

A file whose *shape* you know, not whose contents you hope for:

- `/etc/passwd` — matched on `^user:x:uid:gid:` rather than on the word root
- `win.ini` — matched on a section header
- a private key header
- `/proc/self/environ` — also tells you the service account and sometimes a
  credential, which is a second finding with its own requirement

A file you cannot recognise is not a sentinel. "The response got longer" is not a
file read.

## Where this goes next

A readable file is a primitive, and the finding should say what it reaches:

- source code → the write paths and sinks for every other class
- a configuration file → credentials, which need their own proof (observed, and
  shown live against their own issuer, never a third party)
- `/proc/self/environ`, `/proc/self/cmdline` → the service identity and flags
- a session store or a database file → data access without SQL injection

Each of those is a separate hypothesis with its own class and its own proof. A
file read that is reported as "could lead to RCE" without the rce proof is a
candidate, and the ledger will record it as exactly that.
