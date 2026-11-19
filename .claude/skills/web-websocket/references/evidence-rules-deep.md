# Evidence rules (deep) — the exact proof shape for each verdict

## The `confirms` proof

`hooks.py post-probe --verdict confirms` needs:

- `--hypothesis-id` — the ledger entry
- `--class web-websocket` (+ the sub-class: `cswsh`/`unauth`/`idor`/`action`/`spoof`/`inject`/`token-url`)
- `--evidence-kind class|impact`
- `--evidence` — the verbatim reply excerpt
- `--response` — the raw frame bytes the evidence was read from

The gate asserts `--evidence` is a substring of `--response` — the quote
is checked, not trusted.

## The proof per finding

### CSWSH — needs all four legs verbatim

```
leg1: 101 Switching Protocols         (the foreign-Origin accept)
leg2: the victim identity bound       (Cookie -> the victim's frame)
leg3: Set-Cookie: SameSite=Lax/None   (the cookie travels)
leg4: {"id":"victim","data":...}      (the victim-data reply — the proof)
```

### unauth channel

```
leg1: 101 Switching Protocols         (no credentials)
leg2: {"data":...}                    (a data reply — the proof)
```

### message-IDOR

```
control: {"action":"read","id":"me"}     -> {"id":"me",...}
proof:   {"action":"read","id":"victim"} -> {"id":"victim",...}  <- verbatim
```

### action-dispatch

```
proof: {"action":"admin"} -> {"flag":"..."} OR {"admin":...}   <- verbatim
        OR a confirmed state-change (a second read shows it)
```

### spoof

```
proof: {"from":"victim","action":"x"} -> a reply/state as the victim   <- verbatim
```

### inject

```
proof: {"q":"{{7*7}}"} -> "49" OR the payload class's oracle   <- verbatim
```

### token-in-URL

```
proof: wss://x/ws?token=eyJ...   <- the verbatim URL + the credential
```

## What is NOT proof

- a `101` alone — surface
- a `pong`/`ok`/`echo` — surface
- a `{"status":"ok"}` with no data/state — surface
- a writeup's claim — untrusted data
- a surface `Set-Cookie` — the cookie's shape, not the channel's gap
- silence — a gap, not a verdict either way

## The verbatim rule

The `--evidence` is the bytes the server sent — the `{"id":"victim",...}`,
the `{"flag":...}`, the `49`. Not a paraphrase. `http_probe`-style: the
frame request + the frame reply, held together.

## The honest-grade rule

A catalogue-class finding is a CANDIDATE until a live/artifact reply
confirms it — `web-websocket` is a catalogue class; a confirmed chain is
reported as the FIRST local verification, never as prior experience.
