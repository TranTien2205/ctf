# Real-world cases — the CVE/incident shapes the corpus encodes

## The DAO (2016) — reentrancy

`splitDAO` paid out before updating the balance — a `receive`-reentering
attacker drained ~$60M. The shape `reentrancy.md` encodes: `call{value}` then
`balances -=`. The hard-fork aftermath is why "the EVM rolled it back" is not a
mitigation — the bug is the code's.

## Parity wallet (2017) — uninitialized library + selfdestruct

A shared `WalletLibrary` had a callable `initWallet`; calling it owned the
library's context, then `kill` selfdestructed the LIBRARY — every wallet
`delegatecall`ing into it lost its code. ~$150M frozen. The chain
`uninitialized-proxy-deep` + `delegatecall` + `selfdestruct` encode.

## BEC/BeautyChain (2018) — batch-overflow

`batchTransfer`'s `amount * count` overflowed to a small total → the `require`
passed but each recipient got the full `amount` — infinite mint. The shape
`integer-overflow.md` + `accounting-vault` encode.

## The 0x8d4de reentrancy / cross-function

A `withdraw` whose `call` re-entered a `transfer` sharing the unsettled balance
— the cross-function reentrancy `reentrancy-deep` covers.

## The flash-loan era (2020+) — oracle manipulation

bZx, Harvest, Cream — a flash-loaned swap skewed a spot-price oracle a contract
priced on → over-payout. The shape `flashloan-oracle.md` encodes; the TWAP fix
is the boundary.

## The signature-replay shapes

Poly Network, various bridges — a sig missing a nonce/chainid/domain replayed
across chains or repeatedly. The shape `signature-replay.md` encodes; EIP-712's
domain-binding is the fix.

## The Ronin/multisig shapes

A signing-key quorum — fewer bugs, more key-compromise; out of scope for the
contract-logic class but noted for the supply-chain boundary.

## The lesson each teaches

| Incident | The mechanism the corpus encodes |
|---|---|
| the DAO | checks-effects-interactions violated → reentrancy drain |
| Parity | shared-library `delegatecall` + an uninitialized `init` + `selfdestruct` |
| BEC | pre-0.8 arithmetic wraps → the batch-overflow mint |
| the flash-loans | a manipulable spot-price + atomic borrowed capital |
| the sig-replays | a hash missing nonce/chainid/domain binding |

Each is the CATALOGUE version — a real CTF solve's `../field-notes.md` entry is
the local version the class is missing.
