# Signature / ecrecover — replay, malleability, and the zero-address

## The shape

```solidity
function claim(bytes memory sig, uint amount) public {
    bytes32 h = keccak256(abi.encode(msg.sender, amount));
    require(ecrecover(h.toEthSignedMessageHash(), sig) == signer);
    balances[msg.sender] += amount;
}
```

`ecrecover` recovers the signer's address. The bug is in WHAT gets hashed and
WHETHER the signature can be reused or forged.

## The bug classes

| Bug | The shape |
|---|---|
| **replay** | the signed message lacks a nonce → the same sig claims repeatedly |
| **cross-chain replay** | no `chainid` in the hash → a sig from chain A works on chain B |
| **missing msg.sender binding** | the hash doesn't include `msg.sender` → anyone replays a leaked sig |
| **zero-address** | `ecrecover` returns `address(0)` on a bad sig — a `== address(0)`-unprotected `signer` default, or a check that accepts `address(0)` |
| **malleability** | an `(r, s, v)` with a flipped `s`/v recovers the same address — a replay-protection keyed on the sig bytes is bypassed by the mirror sig |
| **wrong hash** | the message hashed differs from what's checked — sign for a benign message, spend a different one |

## The detection fingerprint

- `ecrecover`/`ECDSA.recover`/`ecsign` in the contract
- a `claim`/`withdraw`/`permit` gated on a signature
- the signed hash's fields — check for `nonce`, `chainid`, `msg.sender`, expiry
- **falsifier**: the hash binds nonce+chainid+sender+expiry and the sig isn't
  malleable-checked-but-usable

## The exploit

```solidity
// replay: no nonce → send the same sig twice
target.claim(sig, amount);   // first
target.claim(sig, amount);   // replay — balances double

// zero-address: a malformed sig recovers to address(0)
// if signer defaults to address(0) and the check is recover==signer → passes
target.claim(badSig, amount);
```

## The personal-message prefix

`toEthSignedMessageHash` / `personal_sign` prepends `"\x19Ethereum Signed Message:\n32"`.
A contract that forgets the prefix (raw `ecrecover(hash, sig)`) accepts a sig
made for a DIFFERENT message format — a transaction-level signature reused as a
message sig. Check whether the contract prefixes before replaying.

## The evidence

`cast call` the balance/flag before/after — a replayed or forged sig changes the
state. The receipt + the balance read are the proof; the sig bytes are the
artifact.
