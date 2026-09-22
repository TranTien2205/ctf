---
name: web-web3
description: >
  Action-oriented depth skill for Smart contract / web3. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: none listed.
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

1. Read the setup contract and solved condition first. Record the exact state
   predicate and the instance addresses.
2. Call read-only view functions and record the starting state.
3. Identify one state transition reachable by the supplied caller and predict
   its post-state before sending it.

Confirmation is the on-chain solved predicate changing after the attributable
transaction. A reverted transaction, a local simulation, or a guessed flag is
not confirmation.

## Operational probe

Before writing a transaction, capture:

```text
RPC endpoint, chain id, setup address, challenge caller, solved predicate,
starting storage/state, and the exact read-only calls used to obtain them.
```

Run read-only calls first. Then choose one state transition whose post-state can
be predicted from the setup contract. Confirmation requires the solved predicate
to change after the attributable transaction and a receipt/status proving it
was mined. A local simulation, a successful transaction with unchanged state,
or a guessed private key is inconclusive.

For a delegatecall or `tx.origin` hypothesis, prove the call path with a harmless
view/state marker before attempting the solved condition. Preserve calldata and
receipt output verbatim.

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
- Never assume a private key, RPC URL, or contract address from another
  challenge; use only values supplied for this instance.

## Routing

Depth, one named file at a time:

- `skills/ctf-web/web3.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
