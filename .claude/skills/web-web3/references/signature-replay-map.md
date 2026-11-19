# Signature-replay map — the ecrecover bug shapes indexed

## The bug → the shape → the fix-it-should-have

| Bug | The shape | The fix |
|---|---|---|
| replay | a sig claims repeatedly | a `nonce`/`used` mapping in the hash |
| cross-chain replay | a chain-A sig on chain B | `block.chainid` / the EIP-712 domain |
| cross-contract replay | a contract-A sig on contract B | the contract address in the domain |
| missing sender-binding | anyone replays a leaked sig | `msg.sender` in the hash |
| zero-address | `ecrecover`→`0` passes a `==signer` check | `require(signer != address(0))` or a real signer |
| malleability | `(r, n-s, v^1)` mirrors the same address | `s <= n/2` (EIP-2) + the ECDSA lib |
| wrong-hash | a sig for one message spent on another | the exact message bound |
| `encodePacked` collision | `(a,b)` vs `(ab,c)` hash the same | `abi.encode` (not Packed) for dynamic args |

## The hash-field inventory

A replay-proof sig's hash binds:

```solidity
keccak256(abi.encode(
    msg.sender,      // WHO can spend it
    amount,          // WHAT it authorizes
    nonce,           // ONE-TIME use
    block.chainid,   // WHICH chain
    address(this),   // WHICH contract
    deadline,        // WHEN it expires
    theAction        // WHAT for
))
```

Each missing field is a replay vector — `signature-replay.md` for the shapes.

## The ecrecover return values

```
valid sig          → the signer's address
malformed sig      → address(0)   ← the zero-address bug's source
```

`ecrecover` returns `0` on ANY bad input — a `require(signer != address(0))` or
a real `signer` address closes the zero-address bug.

## The personal-sign prefix

`toEthSignedMessageHash(h)` / `personal_sign` prepends
`"\x19Ethereum Signed Message:\n32"`. A contract that uses raw `ecrecover(hash,
sig)` accepts a sig made for a different format — a tx-level sig reused as a
message sig. Check the prefix before replaying.

## The detection order

```bash
grep -n "ecrecover\|ECDSA\|recover" Challenge.sol   # the sig check
# read the hash's fields — which are bound? which missing?
```

`signature-replay-deep.md` for the full exploit shapes.
