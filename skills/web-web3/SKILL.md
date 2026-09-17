---
name: web-web3
description: >
  Smart contract / web3. Open after the router or tools/classify.py named this class.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, web3, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# Smart contract / web3

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

read the setup contract and the solved condition first; that names the exact state you must reach

**Falsifier** — the observation that closes this class: the solved condition depends on state no external caller can change
## Recognise

A Solidity source file, an RPC endpoint, and a setup contract. The challenge
usually ships a `Setup` contract with a solved condition.

## Confirm

**Read the setup contract and the solved condition first.** It names the exact
state you must reach, and it is the only definition of success — everything else
is a route to it.

## Where the routes usually are

Delegated calls that execute foreign code in this contract's storage; access
checks that read the transaction origin rather than the immediate caller;
arithmetic or accounting that can be driven to a state the author did not expect;
and any function that is reachable before initialisation.

## Traps

- The RPC endpoint and the private key are supplied per instance; nothing here is
  reusable across instances.
- Reading the deployed bytecode is often faster than reasoning about the source
  when the two might differ.

## Routing

Depth, one named file at a time:

- `skills/ctf-web/web3.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
