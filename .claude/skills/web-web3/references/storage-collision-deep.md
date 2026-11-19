# Storage collision (deep) — the slot-math reference and every collision shape

## The layout rules in full

```
scalar vars in declaration order → slots 0, 1, 2, ...
a var < 32 bytes packs right-to-left with neighbors in one slot
  e.g. address (20B) + bool (1B) + uint64 (8B) pack into slot N
mapping(k => v) at declared slot p → value at keccak256(abi.encode(k, p))
dynamic array T[] at declared slot p → length at p, elem[i] at keccak256(p) + i
bytes/string at slot p → len<=31: bytes + len*2 in p; len>=32: len*2+1 at p,
                         data at keccak256(p) + i*32 chunks
struct S at slot p → its members fill p, p+1, ... in declaration order
a contract inheriting B → B's vars take the low slots first (C3 linearization)
```

## The delegatecall collision (the main shape)

`delegatecall` runs impl code on PROXY storage. The impl's declared var N
writes the proxy's slot N — if the layouts differ, the write lands wrong.

```
Proxy declares:  impl_addr(slot0)  owner(slot1)
Impl declares:   a(slot0)          owner(slot1)  ← a collides with impl_addr!
```

`impl.setA(x)` through `delegatecall` writes PROXY slot 0 → `impl_addr = x`.
The next delegatecall goes to the attacker's contract.

## The verification method

```bash
# map the proxy's real slots
cast storage $PROXY 0; cast storage $PROXY 1; cast storage $PROXY 2
# map the impl's declared slots — read the source; each Nth var → slot N
# find the impl function that writes a slot that is owner/impl/predicate in the proxy
```

The slot-number match — not the var name — is what matters. `cast index`/
`cast keccak` compute the mapping/array element slots.

## The packed-slot collision

Two small vars share a slot — a setter for one can clobber the other if the
code writes the whole slot. A `bool` next to an `address` — writing the address
with a wrong-width store clobbers the bool. Detection: `cast storage` the
packed slot, split the bytes by the declared widths.

## The "the impl is the target" collision

A `delegatecall` to a SETTABLE impl — `setImpl(attacker)` changes the target;
then the impl's `owner`-writing function delegatecalled writes the proxy's
owner. Two-step: set the impl, then delegatecall a function that writes the
owner slot.

## The AlienCodex array-shape (pre-0.8)

```solidity
bytes32[] public codex;
function retract() { codex.length--; }   // underflows length to 2**256-1
function revise(uint i, bytes32 v) { codex[i] = v; }   // writes ANY slot
```

An `array.length--` underflow (pre-0.8, no check) makes the array's storage
span the whole space — `codex[i] = v` writes `keccak256(slot) + i` for ANY i →
overwrite slot 0 (`owner`) by computing `i = 0 - uint(keccak256(slot))` mod 2^256.

## The evidence

`cast storage $PROXY <owner-slot>` = attacker after the collision write;
`isSolved() → true`. The slot read before/after proves the write landed on the
protected slot, not the intended one.
