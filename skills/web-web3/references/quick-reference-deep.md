# Quick reference (deep) — the complete one-card web3 operation

## The read (free)

```bash
export RPC=<rpc> KEY=<privkey>
cast chain-id; cast wallet address --private-key $KEY; cast balance $ME
cast call $SETUP "isSolved()(bool)"                     # the predicate
cast call $SETUP "challenge()(address)"                 # the target
cast code $CH | head -c 200; cast balance $CH
for s in 0 1 2 3 4 5; do cast storage $CH $s; done      # the slots
cast logs --rpc-url $RPC "address=$CH"                  # the emitted secrets
```

## The predicate → the class

| Reads | Class | First move |
|---|---|---|
| `owner()` | access-control | `cast send "setOwner"` |
| `balance` | reentrancy/selfdestruct/accounting | the withdraw + the ether routes |
| `flag`/`locked` | access-control/visibility | a setter / `cast storage` |
| `answer`/`winner` | weak-randomness/front-running | a Predict / a sequencer |
| `count`/`balances` | integer-overflow/reentrancy | the wrap / the re-enter |
| `code.length` | selfdestruct/constructor | `selfdestruct` / a constructor call |
| `signer` | signature | a replayed/forged sig |
| `rate`/`shares` | accounting/flash | the desync |

## The bug → the payload

```solidity
// access-control   → cast send "setOwner(address)" $ME
// reentrancy       → Reenter{ receive: v.withdraw() } + deposit+withdraw
// delegatecall     → a pwn() that writes the owner slot via the proxy.fallback
// storage-collision→ cast send "setA" → the impl write lands on the proxy's slot
// tx.origin        → Phish{ attack: Target.go() }
// integer-overflow → cast send "transfer" 1  (pre-0.8 wraps)
// weak-randomness  → Predict{ attack: compute the same-block answer + guess }
// selfdestruct     → Force{ payable-ctor, boom: selfdestruct(target) }
// uninitialized    → cast send "initialize(address)" $ME
// signature        → cast send "claim" the replayed/forged sig
// accounting       → deposit + donate + withdraw (desync the tracked value)
// visibility       → cast storage the slot → cast send the gate
// gas-griefing     → Partner{ receive: for(;;){} } / the loop-grow
```

## The verify

```bash
cast send ... --private-key $KEY --rpc-url $RPC
cast receipt <txhash> --rpc-url $RPC   # status 0x1, from = caller
cast call $SETUP "isSolved()(bool)"    # false → true = solved
```

## The rules

- `isSolved()` first — the predicate names the class
- enumerate reachable functions before the first `cast send`
- `cast call`/`forge` = sim; `cast send` = the solve
- `cast storage` reads `private` — no on-chain secret
- the bare setter is often the intended solve — check it first
- `catalogue` — published knowledge; `../field-notes.md` is the local layer
