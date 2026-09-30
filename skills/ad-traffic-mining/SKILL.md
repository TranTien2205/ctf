---
name: ad-traffic-mining
description: >
  Recover another team's working exploit out of your own captured traffic, and
  turn it into a farm-ready exploit. Use in an attack-defense contest as soon as
  any other team has attacked your service — which is usually before you have
  finished reading the source. Covers the capture, the split into single requests,
  ranking against a baseline, telling a working exploit from a failed attempt, and
  making your own exploit expensive to steal back.
tags: [process, method, attack-defense, capture, replay, exploit, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "no baseline capture exists, so every request scores as equally interesting"
    - "a candidate replays cleanly against your own box and returns no flag"
    - "the capture is not pointed at the service's real port"
evidence_level: catalogue
---
# Attack-defense traffic mining — Process Skill

**Catalogue method. Nothing in this repository has solved an attack-defense
contest.** What is measured, in this session and recorded here because it changes
the commands, is the *pipeline*: the `tshark follow` form that `tools/ad/traffic_mine.py`
used to document put the victim's **response** into the parsed request body. On one
loopback capture, mining a follow dump produced 8 occurrences of `HTTP/1.0` in the
output; the same capture through `tools/ad/cap_split.py` produced 0. That is the
difference between a replay command that carries your victim's response at a third
team and one that carries the attacker's request.

## Why this is the highest-return move in the game

Every other team is attacking your service with an exploit that already works.
Their payloads arrive at your own interface. Recovering one is usually faster than
finding the bug yourself, and it is immediately usable against every other team,
because everyone runs the same code. You are being handed working exploits.

## First probe

```bash
python3 tools/ad/traffic_mine.py --baseline baseline/ --live live/ --top 10
```

**Falsifier:** every live request scores zero against the baseline. Either nobody
has attacked this service yet, or `--live` is not pointed at traffic for it. A
capture with no baseline is the same failure wearing a different hat: without
`--baseline` every request looks equally interesting, which is the same as having
no signal at all.

## The pipeline, in order

1. **Capture, bounded.** `dumpcap`, not `tcpdump`: measured on this box,
   `/usr/bin/dumpcap` carries `cap_net_admin,cap_net_raw` and `/usr/bin/tcpdump`
   carries none, so `dumpcap` needs no sudo. Always bound it with `-a`, or the
   disk fills and you lose the service to a full filesystem rather than to an
   exploit.
   ```bash
   dumpcap -i <iface> -q -f 'tcp port <port>' -a duration:120 -w live.pcap
   ```
2. **Split into one request per file.** Never feed a follow dump to the miner:
   ```bash
   python3 tools/ad/cap_split.py --pcap live.pcap --out live/
   ```
   Read the `skipped` count in its JSON. A large `skipped` with a small `requests`
   means the display filter missed the port, not that nobody attacked you. The
   `tshark` version is printed for the same reason: a field-name drift between
   versions shows up as `requests: 0`, and the version line is what tells you that
   is what happened.
3. **Rank against the baseline**, as in the first probe above.
4. **Read the reasons, not the score.** The score orders the list; the `reasons`
   say what the other team was doing. A candidate whose only reason is an unusual
   parameter name is worth less than one naming a traversal or an operator.

## Telling a working exploit from a failed attempt

This is the part that wastes the most time, and the capture alone cannot answer it.
Three discriminators, cheapest first:

- **Repetition.** A team that found a bug farms it every tick. The same shape
  arriving from the same source once a tick is a working exploit; a burst of forty
  variants in ten seconds is somebody fuzzing, and copying it copies their failure.
- **Your own response.** Replay the candidate against **your own** service and read
  what comes back. A flag-shaped string in the response is proof; a 400 or a 500 is
  proof of the opposite. Do this before aiming it at anyone.
- **The `immune` list.** `tools/ad/flag_farm.py` prints `immune`: teams that
  returned nothing while others returned flags. They have patched. Their patch is
  the shortest and most precise description of the bug, and reading it is faster
  than re-deriving the bug.

## Turning a candidate into a farm-ready exploit

`traffic_mine.py` hands back a `curl` templated on `$TARGET` with the victim's
`Host` removed. That is a replay, not an exploit. To farm it:

- Wrap it in a script that takes the host as `argv[1]` or reads `TARGET_HOST` from
  the environment, and prints any flag it finds to stdout. `flag_farm.py` scans
  both stdout and stderr, so a bare `print()` is enough.
- **Strip every credential the other team's request carried.** Their `Cookie` and
  `Authorization` belong to them, not to you: a replay that keeps them either fails
  against a third team or authenticates as the attacker. Register your own account
  and use your own token.
- Make it idempotent and quiet. It runs once per team per tick for the rest of the
  contest.
- Then prove the plumbing before there is any hurry:
  ```bash
  python3 tools/ad/flag_farm.py <config>.json --once --dry-run
  ```
  `--dry-run` holds the flags rather than submitting them, and says so; nothing is
  lost by rehearsing.

## Your exploit is also traffic

Everything above is being done to you. Three things make an exploit expensive to
steal, and none of them is worth more than five minutes:

- Do not send a payload that is self-describing. `../../flags/current` names the
  target of the bug; an encoded or indirect form does the same work and reads as
  noise in someone else's capture.
- Do not send it more often than you need to. One request per team per tick is a
  much smaller sample than a retry loop.
- Accept that it will be stolen anyway, and spend the time on the next bug instead
  of on hiding this one. The `immune` list cuts both ways: once you patch, you have
  told everyone what the bug was.
