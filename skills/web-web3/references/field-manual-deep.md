# Field manual (deep) — the operational reference

## The complete command sheet

```bash
# environment
export RPC=<rpc> KEY=<privkey>
cast chain-id --rpc-url $RPC; cast block-number --rpc-url $RPC
cast wallet address --private-key $KEY; cast balance $ME --rpc-url $RPC

# the predicate + the contract
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC
cast call $SETUP "challenge()(address)" --rpc-url $RPC
cast code $CH --rpc-url $RPC | head -c 100

# the state
cast call $CH "owner()(address)" "locked()(bool)" "solved()(bool)" --rpc-url $RPC
for s in 0 1 2 3 4 5; do cast storage $CH $s --rpc-url $RPC; done
cast balance $CH --rpc-url $RPC
cast logs --rpc-url $RPC "address=$CH"   # the emitted secrets

# the dry-run
forge test --fork-url $RPC -vvvv
cast call $CH "fn(args)" --rpc-url $RPC   # the sim

# the send
cast send $CH "fn(args)" <args> --private-key $KEY --rpc-url $RPC
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
cast send $SOLVER "run()" --private-key $KEY --rpc-url $RPC

# the verify
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC
cast receipt <txhash> --rpc-url $RPC
cast run <txhash> --rpc-url $RPC
```

## The decision sheet

```
isSolved() reads:
  owner()         → a setter? setOwner/init/transferOwnership; tx.origin? delegatecall?
  balance         → a withdraw+call? reentrancy; refuses ether? selfdestruct; rate? accounting
  flag/locked     → a setter? access-control; a private gate? visibility
  answer/winner   → block.*? weak-randomness; first-come? front-running
  count/balances  → <0.8? overflow; call-then-update? reentrancy
  code.length     → selfdestruct; a constructor-EOA check? the constructor call
  signer          → ecrecover? signature replay/forge
  rate/shares     → accounting/flash
```

## The class files in order of likelihood

1. `access-control.md` — the bare setter is the most common solve
2. `reentrancy.md` — the drain
3. `delegatecall.md`/`storage-collision.md` — the storage-write
4. `tx-origin.md` — the origin/sender confusion
5. `integer-overflow.md` — the wrap
6. `visibility.md` — the readable secret
7. `weak-randomness.md` — the predictable source
8. `selfdestruct.md` — the force-feed/delete
9. `uninitialized-proxy.md` — the callable init
10. `signature-replay.md` — the replay/forge
11. `accounting-vault.md`/`flashloan-oracle.md` — the desync
12. `front-running.md` — the ordering
13. `gas-griefing-dos.md` — the DOS

## The discipline sheet

- the enumeration is free — the send is attributable
- the bare setter is the solve more often than a deep bug
- a `cast call` is never the solve
- the private key stays out of notes
- `cast code` early — the source can lie
- `cast storage` the low slots — `private` leaks
- 3 reverts → `decide.py escalate`
