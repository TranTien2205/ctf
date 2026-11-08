---
name: ad-service-triage
description: >
  Attack-defense router. Use at the START of an attack-defense contest, once per
  service. You run the same code every other team runs, availability is scored
  continuously, and the flag rotates every tick — so the order of work is not the
  jeopardy order. Find the flag store, the paths that reach it, and what the
  organiser's checker needs, then route to exactly one depth skill. Routes; never
  solves.
tags: [process, router, attack-defense, availability, flag-store, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "a service is red on the organiser's checker: that outranks every attack"
    - "two passes over the source produce no path that reaches the flag store"
    - "the team host list is not yet confirmed from the official brief"
evidence_level: catalogue
---
# Attack-defense service triage — Router

**Catalogue router. Nothing in this repository has solved an attack-defense
contest**, so nothing below is local experience. What grounds it is the shape of
the game and four measured properties of this tree's own tooling, named where they
matter. Treat it as a procedure, not as a solve.

## Why the jeopardy order is wrong here

`tools/decide.py`, `tools/hooks.py` and `tools/state.py` budget probes against ONE
target and gate ONE verified flag. Four assumptions change in attack-defense, and
each one inverts a habit:

| Jeopardy habit | Attack-defense reality |
|---|---|
| one flag, then you are done | the flag rotates every tick; you need a farm, not a verdict |
| you only attack | you are also the target, and availability is scored continuously |
| hypotheses come from source and chain cards | the best ones arrive in your own capture, written by other teams |
| a probe budget stops you sinking time | over-patching costs more than the exploit did |

Availability cannot be won back. A flag is scored once per tick; a service that is
down is losing points every tick until it is up. So **every ordering decision
below resolves in favour of availability.**

## Minute zero, before any source reading

Three things, in this order, and none of them is an exploit:

1. **Write the health spec and save a green baseline.** Without a baseline saved
   *while the service still works*, there is nothing to compare a patch against:
   ```bash
   python3 tools/ad/sla_check.py <spec>.json --save t0.json
   ```
   Write the checks from the organiser's checker if they publish it, and from the
   service's own happy path if they do not. A check that only asserts `200` on `/`
   passes happily while the feature the checker exercises is broken.
2. **Start the baseline capture.** The baseline is the organiser's checker talking
   to a service nobody is attacking yet, and it cannot be made later:
   ```bash
   dumpcap -i <iface> -q -f 'tcp port <port>' -a duration:120 -w baseline.pcap
   python3 tools/ad/cap_split.py --pcap baseline.pcap --out baseline/
   ```
3. **Assume every credential you were given is public.** Every team booted the
   same image, so every default password, SSH key, database credential and API
   token in it is known to everyone. Rotate, then re-run `sla_check.py` to prove
   nothing broke.

## Then read the source, in this order

Not routes-first. **Flag-store-first**, because the flag store is the only thing
the scoreboard pays for:

1. Where does a flag physically live? A table, a file, a key in a cache, an
   environment variable the app reads per request. Name the file and line.
2. Which code paths read it? Every one of them, including the ones no route
   reaches yet.
3. Which of those paths is reachable from outside, and with what authorization?
4. What does the checker have to be able to do? That set is what a patch may not
   break, and it is usually narrower than the whole feature.

## Route on what you found

| What the source shows | Open |
|---|---|
| a request value reaching the flag store's query | `web-sqli`, or `web-nosqli` when the value stays an object |
| a path or filename parameter reaching the store's file | `file-read-primitives` |
| a value rendered by a template engine | `web-ssti` |
| an object merge, or a key that reaches a prototype | `web-prototype-pollution` |
| an identifier in a path or body with no ownership check | `web-idor` |
| a signed or encrypted token the app trusts | `web-auth-session` |
| a value interpolated into a server-side fetch | `web-ssrf` |
| deserialization of anything client-supplied | `web-deserialization` |
| an upload whose name or type the app trusts | `web-file-upload` |
| nothing yet, and other teams are already attacking you | **`ad-traffic-mining` — do this before inventing a hypothesis** |

Two attack-defense skills are not bug classes and are needed regardless of which
row fires: `ad-patch-without-breaking-sla` before the first patch, and
`ad-planted-backdoor-hunt` inside the first thirty minutes.

## First probe

Not a payload. The cheapest discriminating action is to ask whether another team
has already written the exploit for you:

```bash
python3 tools/ad/traffic_mine.py --baseline baseline/ --live live/ --top 10
```

**Falsifier:** the live capture holds nothing that departs from the baseline —
either nobody has attacked this service yet, or the capture is not pointed at it.
Then, and only then, go back to the source and the routing table above.

## What ends the triage

The service is green and a baseline is saved; the flag store and every path to it
are named with a file and a line; the team host list is transcribed from the
official brief; and exactly one depth skill is open. Anything else is still
triage.
