---
name: web-command-injection
description: Prove command execution safely — separator sweeps, timing controls, the benign marker command with a nonce, and the blind case. Use when a parameter may reach a shell, when output looks like command output, or when an RCE needs a demonstration that is safe to put in a report.
classes: rce
---

# Command injection, and how to prove it without doing damage

Proof requirement: **the output of `id; echo <nonce>`, with the nonce matching
the probe.** That is the whole proof. Not a reverse shell, not a downloaded
binary, not a file written to `/tmp`, not a new user. The nonce is unguessable,
so its presence in the response cannot be explained any other way, and the
command changes nothing on the host.

This matters beyond etiquette. A reverse shell in an engagement report is a
finding a client cannot verify without rebuilding the host; `id` with a nonce is
a finding they can reproduce in one request.

## Finding the separator

The sweep, cheapest first, against one parameter you have reason to believe
reaches a shell:

| separator | works when |
|---|---|
| `;` | the value lands in a shell command, unquoted |
| `&&`, `\|\|` | same, and you want the result to depend on the first command |
| `\|` | the value is a filename position that reaches a pipe |
| `` `cmd` ``, `$(cmd)` | the value is inside double quotes |
| `%0a` (newline) | the value reaches a shell line, and `;` is filtered |
| `' ; '`, `" ; "` | the value is single- or double-quoted; break out first |

Each one is one `http.probe`. What you are looking for is not an error — it is a
**difference in the output that corresponds to the command running**.

## The timing control, and why one measurement is not enough

`sleep 5` versus `sleep 0`, **twice each, interleaved**. A single slow response
is a slow endpoint. Four measurements in two pairs is a mechanism. Use
`http.differential repeat=2` so the median is used and the self-similarity check
runs.

Do not use `sleep 30`. You are proving the mechanism, not testing patience, and
a long sleep in a thread pool is a small denial of service.

## The marker command

```
proof.exec_marker url="http://t/ping?host=127.0.0.1{payload}" separator=";" encode=url
```

`{payload}` goes **exactly** where the command belongs, including any quote or
bracket you need to break out of. The tool substitutes `id; echo <nonce>`,
sends it, and grades the response against the matrix. It reports three things:
whether the nonce came back, whether an identity line was present, and whether
anything in the request looked destructive — that last check will refuse to grade
a payload containing `rm -rf`, `nc -e`, `useradd` or a `/dev/tcp/` redirect, and
that refusal is not negotiable.

The intrusive tier must be enabled for the engagement. If it is not, the broker
refuses, and the right response is to ask the client rather than to work around
it.

## When the output does not come back

Blind command injection is common: the command runs and the response says
nothing. Two honest routes, in order:

1. **A collector callback.** `proof.oob_start` gives you a URL carrying a nonce.
   Put `curl <url>` or `wget -O- <url>` after the separator, then
   `proof.oob_check`. The hit records the source address, which also tells you
   what the host's egress looks like.
2. **A file read you can see.** If the application serves files, write the
   command output into a path it serves, read it, then delete it. This is a
   write, so it needs the intrusive tier and it needs cleaning up — record the
   cleanup in the ledger as its own evidence record.

No callback is **not** a negative result. It may mean the host has no egress,
which is a separate measurement and worth stating as one.

## What to put in the report

The request, the nonce, the identity line, and the sentence that the only
command executed was `id`. Then the impact in terms of what that identity can
reach — which usually requires one more read, not one more exploit.
