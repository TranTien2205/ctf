# Case studies — canonical shapes (catalogue, not local solves)

## Ethernaut's "Delegation" — delegatecall

`Delegation.fallback` does `delegatecall(msg.data)` to `Delegate`. `Delegate`
has `pwn() { owner = msg.sender; }`. `delegatecall` preserves `msg.sender` —
calling `Delegation`'s fallback with `pwn()`'s selector runs it on Delegation's
storage with `msg.sender` = the original caller → the caller becomes owner.
The chain: `cast send $DELEGATION "pwn()"` (the fallback delegates it).

## Ethernaut's "Force" — selfdestruct force-feed

`Force` has no receive/fallback and `isSolved` is `address(this).balance > 0`.
No `call{value}` or `.transfer` succeeds — but a funded attacker contract's
`selfdestruct(Force)` force-sends ether. The chain: deploy `Attack{value: 1}`,
`attack.boom(force)`.

## Ethernaut's "Telephone" — tx.origin

`Telephone.changeOwner` checks `tx.origin != msg.sender`. Deploy a `Phish`
contract; the caller calls `Phish.attack(telephone)` → `changeOwner` sees
`tx.origin` = caller (EOA) ≠ `msg.sender` = Phish → owner = caller.

## Ethernaut's "Re-entrancy" — the drain

`Reentrance.withdraw` does `call{value}` then `balances -=`. A `receive`-hook
attacker re-enters `withdraw` before the balance settles — drains the contract.
The chain: deposit seed, `withdraw` → `receive` re-enters.

## Ethernaut's "Vault" — private is not secret

`Vault.unlock(bytes32)` checks `_password == password` where `password` is
`private`. `cast storage $VAULT 1` reads it; `unlock(password)` unlocks.

## Ethernaut's "Token" — the underflow

`Token` on `pragma ^0.5` — `transfer` underflows `balances[msg.sender] - value`
below 0 → wraps to `2**256`. The `require` passes; the balance is huge →
transfer the overflowed balance.

## The parity wallet — the library kill

A `WalletLibrary` (the shared impl) had a callable `initWallet`; calling it
through the wallet's `delegatecall` owned the wallet's context, then `kill`
selfdestructed the WALLET — the library-code-in-caller-context chain. Real-world
(the $30M+ freeze), the shape the `delegatecall`+`selfdestruct` modules encode.

## The shape each proves

| Case | The mechanism it proves |
|---|---|
| Delegation | delegatecall preserves msg.sender on the caller's storage |
| Force | selfdestruct force-feeds a no-receive contract |
| Telephone | tx.origin ≠ msg.sender down a contract chain |
| Re-entrancy | checks-effects-interactions violated → drain |
| Vault | private vars are public via storage reads |
| Token | pre-0.8 arithmetic wraps silently |
