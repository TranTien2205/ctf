---
name: file-read-primitives
description: >
  Arbitrary file read and source disclosure. Use once a read primitive is proven
  — a path or file parameter, an admin read API, SSRF with a file scheme, XXE,
  local file inclusion, archive traversal, or process filesystem access — and the
  source, configuration or flag path still has to be located. Covers normalising
  the primitive, locating source, and escalating a read to execution.
tags: [file-read, lfi, traversal, source-leak, ssrf, xxe, rce]
environment: [ctf, lab, authorized-testing]
budget:
  max_attempts: 5
  stuck_threshold: 3
  time_hint: "35m"
  on_stuck: pivot
  stop_conditions:
    - "no file is readable after absolute paths, traversal and wrappers"
    - "read confirmed but no execution path after the escalation list is exhausted"
---

# File Read → Source → Foothold

A read primitive is a stepping stone. Prioritise finding the application source
and its configuration over dumping files at random: the source names the next
step, and guessing does not.

## Phase 1 — identify the primitive

- A parameter naming a page, file, path, download or URL
- A body field naming a file, possibly encoded
- SSRF with a file scheme, a redirector, or an archive wrapper
- XXE where an entity resolves to a local path
- A backup or restore feature that reads paths with elevated privileges
- Direct filesystem access from an already-obtained shell

## Phase 2 — prove and normalise

Try an absolute path first — many applications join the value incorrectly, so
traversal is not always needed. Then traversal at increasing depth. For PHP, a
filter wrapper that base64-encodes the source survives binary content and comment
stripping. If a filter removes traversal sequences or appends an extension, test
the doubled form and the terminator forms.

Record whether the response echoes the file raw or inside a structured body; that
decides how the extraction is scripted. Strip any prefix or suffix the page adds
before comparing content.

## Phase 3 — locate the source

The process filesystem is the fastest route on Linux: the command line of the
running process gives the interpreter and the entry point, and the environment
gives the working directory and any variables the deployment set. From there read
the application's own files: the entry module, the route definitions, the
configuration module, and the authentication layer.

The source is what turns a read into a chain. It names the hidden routes, the
filter logic, the datastore credentials and the signing secrets.

## Phase 4 — what to read, in order

1. Application source found in phase 3
2. Framework configuration and environment files — datastore credentials,
   signing keys
3. User home directories: keys, shell history
4. Scheduled jobs and service definitions
5. Backup archives
6. Web server configuration and any auth files it references

In a CTF the flag is often a file whose path the source names directly. Read the
source before sweeping the filesystem.

## Phase 5 — escalate read to execution

See `references/read-to-rce.md`. The usual routes: including a file the
application will execute, poisoning a log the application includes, chaining
filter wrappers, writing where a reloading process watches, a restore feature
that writes as well as reads, and a datastore that can write files.

## Route to depth

| Situation | File |
|---|---|
| The value reads files but is filtered | `references/traversal-and-wrappers.md` |
| Process filesystem is readable | `references/proc-and-source-enum.md` |
| Read is confirmed and execution is the goal | `references/read-to-rce.md` |

## Discipline

- Confirm the primitive on one known-readable path before building an extraction
  loop.
- Reading a file proves a read, not an exploit. Say which is which.
- On a shared instance, read; do not write.
- Budget and escalation as in `../LOOP_DISCIPLINE.md`.
