# Quick check — the 60-second orientation

## Is this skill in scope?

```
admin bot / report form + a client-side payload?  -> debugging aid
a WebDriver/Grid/CDP endpoint answering?           -> attack surface
neither?                                          -> not this class
```

## The three commands that decide

```bash
# 1. is a driver exposed?
curl -s -m5 -X POST http://T:9515/session -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
#    -> sessionId = attack surface live

# 2. is it a Grid?
curl -s -m5 http://T:4444/status
#    -> node inventory = Grid

# 3. is CDP exposed?
curl -s -m5 http://T:9222/json
#    -> target list = CDP live
```

## The one probe that decides the aid

```
grep -ri 'bot\|admin\|visit\|report' <handout>   -> a bot flow?
```

## The decision

| Answer | Open |
|---|---|
| `sessionId` | `attack-surface.md` + `per-endpoint.md` |
| Grid | `grid-remote.md` |
| CDP | `cdp.md` |
| bot source | `local-bot.md` + `local-bot-deep.md` |
| bot flow, no source | `local-bot.md` |
| nothing | the class is dead — record why |

## The trap to avoid first

Do not fire a guessed payload at the live bot — the blind channel is
the expensive path. The local reproduction is the skill's point;
build it before the first payload.

## The two anchors

- `apexsurvive` — local-bot debugging -> a stored-XSS chain
- `tornadoservice` — the tunnel interstitial that costs bot visits

## The one rule that runs through all of it

Development evidence (local) is not impact evidence (live) — the flag
is the live exfil or the `source`/`cookies`/`screenshot`, gated through
`tools/hooks.py pre-flag`.
