# Mechanism catalogue — every EVM mechanism enumerated

## The opcode-level inventory

| Opcode | Reads/writes | The class it enables |
|---|---|---|
| `CALL` | a foreign call, forwards gas+value | reentrancy, the callback |
| `CALLCODE` | legacy delegatecall | the same as delegatecall |
| `DELEGATECALL` | foreign code on caller storage | delegatecall/collision/kill |
| `STATICCALL` | read-only foreign call | read-only-reentrancy |
| `CREATE`/`CREATE2` | deploy a contract | the address/constructor/resurrect |
| `SELFDESTRUCT` | delete + force-send | force-feed/delete/kill |
| `SSTORE`/`SLOAD` | storage write/read | the predicate's slots |
| `SHA3`/`KECCAK256` | a hash | the sig/answer/commit |
| `ORIGIN` | `tx.origin` | tx.origin |
| `CALLER` | `msg.sender` | the caller check |
| `CALLVALUE` | `msg.value` | the ether check |
| `CALLDATALOAD`/`CALLDATASIZE`/`CALLDATACOPY` | the calldata | the dispatch |
| `ADDRESS` | `address(this)` | the self-reference |
| `BALANCE`/`SELFBALANCE` | ether balances | the balance predicate |
| `TIMESTAMP`/`NUMBER`/`BLOCKHASH`/`DIFFICULTY`/`COINBASE`/`GASPRICE`/`GASLIMIT`/`BASEFEE`/`CHAINID` | block context | weak-randomness / ordering |
| `CODESIZE`/`EXTCODESIZE`/`EXTCODECOPY`/`EXTCODEHASH` | code size | the contract/EOA check |
| `GAS`/`GASLIMIT` | remaining gas | the gas gate / the loop bound |
| `REVERT`/`INVALID`/`RETURN` | control | the guard / the revert |
| `LOG0-4` | an event | the leaked-secret surface |
| `ECRECOVER`/`SHA256`/`RIPEMD160`/`IDENTITY`/`MODEXP`/`EC*`/`BLAKE2F` | the precompiles | signature/crypto |

## The account model

- EOA — has a private key, no code, `extcodesize == 0`
- contract — has code, `extcodesize > 0`, storage, a balance
- a contract under construction — `extcodesize == 0` (the window)
- a selfdestructed contract — code/storage erased, balance moved

## The transaction fields

`from`, `to`, `value`, `data`, `gasLimit`, `gasPrice`/`maxFee`/`maxPriority`,
`nonce`, `chainid`, `type`. The `from` is the attribution; `nonce` orders the
account's txs; `chainid` binds the chain.

## The block fields

`number`, `timestamp`, `coinbase`, `difficulty`/`prevrandao`, `gaslimit`,
`basefee`, `hash(n)`. All public; `hash(current)=0`, `hash(>256-old)=0`.

## The mechanism-to-bug map

Every mechanism's misuse is a bug class — `mechanism-map.md` + `detection-map.md`
index them. The catalogue's point: the EVM gives a small primitive set, and the
bugs are the ways a contract mis-uses each one.
