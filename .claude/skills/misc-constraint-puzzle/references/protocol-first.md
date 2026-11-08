# Capture first, solve second

## Step 1 — the manual transcript

```bash
nc host 31337
```

Record verbatim: banner text, prompt terminator (`> `, `: `, `\n`), the
question format, the expected answer shape, and the timeout. Everything the
solver does later is against THIS transcript, not a guess.

## Step 2 — stdlib client skeleton

```python
import socket, re
s = socket.create_connection(("host", 31337), timeout=10)
buf = b""
def until(marker=b"> "):
    global buf
    while marker not in buf:
        chunk = s.recv(4096)
        if not chunk: raise ConnectionError("closed")
        buf += chunk
    out, buf = buf.split(marker, 1)
    return out + marker

print(until().decode(errors="replace"))   # banner + first prompt
while True:
    q = until().decode(errors="replace")
    # parse q, compute answer
    s.sendall(answer + b"\n")
```

## Format edges that break solvers

| Edge | Fix |
|---|---|
| recv() returns half a puzzle | buffer-until-terminator, never assume message boundaries |
| two prompts arrive in one chunk | split on terminator, keep the tail in buf |
| prompt terminator changes (`>` -> `:`) | match on a regex of known terminators |
| late-round format drift | log raw bytes per round; the log shows where parsing dies |
| float/int formatting | `repr()` or match the service's exact format string |
| timeout tightens per round | recv timeout small, compute fast, precompute tables |

## When the service is not a puzzle

A socket that immediately runs a shell, evals input, or jails you is
misc-interpreter-escape, not this class. The constraint class is for
services whose difficulty is TIME or VOLUME, not restriction.
