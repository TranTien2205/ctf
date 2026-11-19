# Verified chains — honest status

## Catalogue class — no local solve

`web-web3` is a **catalogue** class: nothing in this toolkit has solved a
smart-contract challenge yet. `knowledge/chains/` carries no web3 card. The
corpus is published knowledge (EVM semantics, the standard bug classes, the
CTF challenge shape), not locally verified experience — a starting point, not
proof.

## What a real solve proves

A solved web3 challenge is evidence the corpus can absorb:

```text
the challenge:  Setup.sol + Challenge.sol + RPC + key
the predicate:  isSolved() reads owner() == tx.origin / balance == 0 / ...
the path:       the bug class + the exact transition sequence
the evidence:   isSolved() false → true, the tx hashes, the receipts
```

When a real solve lands, `classify_solve.py --chain <id>` files it, the chain
card records the predicate→transition map, and this class moves from
`catalogue` to `verified`.

## The canonical references (catalogue)

The standard CTF web3 corpus the module content derives from:

| Source | The shape |
|---|---|
| Ethernaut (OpenZeppelin) | the canonical 30-challenge series — delegatecall, tx.origin, reentrancy, storage, force-feed, denial |
| Capture the Ether | the older series — guess-the-number, token sale, retirement fund |
| Damn Vulnerable DeFi | the DeFi-flavoured series — flash loans, oracles, governance |
| Paradigm CTF | the harder corpus — MEV, custom EVM, advanced accounting |
| Slither / the EVM spec | the detection rules and the semantics |

Each named bug-class module cites the shape it derives from. A solve's
`../field-notes.md` entry is the LOCAL evidence the corpus is missing.
