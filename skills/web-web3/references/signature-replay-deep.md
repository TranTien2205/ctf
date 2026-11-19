# Signature / ecrecover (deep) — the full replay and forgery surface

## The ecrecover contract

```solidity
ecrecover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) → address
```

Recovers the signer's address from an ECDSA sig. Returns `address(0)` on any
malformed input — a contract that doesn't check for `0` accepts a bad sig as
the zero-signer.

## The replay surface

A sig is valid for the EXACT message it signed. Replay needs the signed message
to lack a field that would bind it:

| Missing field | The replay |
|---|---|
| no `nonce` | the same sig claims repeatedly |
| no `chainid` | a sig from chain A works on chain B |
| no `msg.sender` binding | anyone replays a leaked sig as themselves |
| no contract address | a sig for contract A works on contract B |
| no expiry/`deadline` | a stale sig works forever |
| no function/action binding | a sig for one action is spent on another |

## The malleability shape

An ECDSA sig `(r, s, v)` has a mirror `(r, n-s, v^1)` that recovers the SAME
address. A contract that prevents replay by keying on the sig BYTES is bypassed
by the mirror — the `s` must be in the lower half-order (`s <= n/2`, the
`OpenZeppelin ECDSA`/`EIP-2` check) to kill malleability.

## The zero-address shape

```solidity
address signer;   // defaults to address(0)
require(ecrecover(hash, sig) == signer);   // a bad sig recovers 0 → passes!
```

A bad/malformed sig recovers `address(0)`; if `signer` is `address(0)`
(uninitialized) or the check accepts `0`, the forged sig passes.

## The wrong-hash shape

- `toEthSignedMessageHash`/`personal_sign` prefixes `"\x19Ethereum Signed
  Message:\n32"` — a contract that skips the prefix accepts a sig made for a
  different message type (a raw-digest sig)
- `abi.encodePacked` collision — `encodePacked(a, b)` collides for
  differently-split dynamic args: `encodePacked("ab","c") == encodePacked("a","bc")`
  → a sig for one `(a,b)` validates another
- `ecrecover` on a hash that includes attacker-controlled fields the signer
  didn't intend

## The `permit` / `meta-tx` shape

An ERC-2612 `permit` or a meta-tx relayer — a sig authorizing a transfer or a
gasless call. The replay surface is the same: nonce/chainid/deadline binding.
The EIP-712 `domainSeparator` carries the chainid+contract — a missing/wrong
domain is the cross-contract replay.

## The exploit

```solidity
// no nonce → replay
target.claim(sig, amt); target.claim(sig, amt);
// zero-address: a malformed sig recovers address(0)
target.claim(badSig, amt);   // if signer defaults to 0
// mirror: flip s and v → the same address, different sig bytes
```

## The evidence

`cast call` the balance/flag — a replayed/forged sig changed it. The sig bytes,
the recovered address, and the state read are the chain.
