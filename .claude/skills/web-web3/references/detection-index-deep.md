# Detection index (deep) — the complete signal inventory

## The predicate signals (the strongest)

| `isSolved()` reads | The class |
|---|---|
| `owner()`/`msg.sender`-ish | access-control / tx.origin / delegatecall |
| `balance`/`address(this).balance` | reentrancy / selfdestruct / accounting |
| `flag`/`locked`/`solved`/`locked()` | access-control / visibility |
| `answer`/`winner`/`guess`/`roll` | weak-randomness / front-running |
| `count`/`balances[x]` | integer-overflow / reentrancy / accounting |
| `code.length`/`extcodesize`/`exists` | selfdestruct / constructor-EOA |
| `signer`/`verified`/`recovered` | signature |
| `rate`/`shares`/`price`/`totalAssets` | accounting-vault / flashloan-oracle |
| a composite `a && b && c` | a chain — `multi-step-chains.md` |

## The source signals (per keyword)

| Keyword | Class |
|---|---|
| `delegatecall` | delegatecall |
| `call{value:` then `-=` | reentrancy |
| `tx.origin` | tx.origin |
| `selfdestruct` | selfdestruct |
| `block.timestamp`/`blockhash`/`prevrandao`/`coinbase`/`difficulty` | weak-randomness |
| `private`/`internal` as a secret | visibility |
| `ecrecover`/`ECDSA`/`recover`/`permit` | signature |
| `initialize`/`init`/`initializer`/`setup` | uninitialized-proxy |
| `unchecked` | integer-overflow (0.8+) |
| `pragma ^0.4`-`^0.7` | integer-overflow |
| `deposit`/`withdraw`/`shares`/`rate`/`stake`/`redeem`/`claim`/`borrow`/`flash`/`flashLoan` | accounting/flash |
| `winner`/`claim`/`auction`/`bid`/`first` | front-running |
| `for`/`while` over a growing set | gas-griefing-dos |
| `transfer`/`transferFrom`/`balanceOf`/`mint`/`burn`/`totalSupply`/`decimals` | token-standards |
| `extcodesize`/`codesize`/`address(this).code` | constructor-EOA |
| `keccak256`/`sha3`/`hash` | signature / commit / answer |
| `assembly`/`inline` | the hidden-logic — disasm |
| `onlyOwner`/`onlyX`/`nonReentrant`/`require`/`modifier` | the guard surface |
| `fallback`/`receive`/`payable` | the entry |
| `super`/inheritance/`is` | the layout — the collision |

## The bytecode signals (per op)

| Op | The signal |
|---|---|
| `DELEGATECALL`/`CALLCODE` | delegatecall |
| `CALL` + `SSTORE` after | reentrancy |
| `SELFDESTRUCT` | selfdestruct |
| `STATICCALL` | the snapshot read |
| `ORIGIN` | tx.origin |
| `TIMESTAMP`/`BLOCKHASH`/`NUMBER`/`DIFFICULTY`/`COINBASE`/`GASPRICE`/`BASEFEE` | weak-randomness / ordering |
| `CODESIZE`/`EXTCODESIZE`/`EXTCODEHASH`/`EXTCODECOPY` | the EOA/contract check |
| `SSTORE`/`SLOAD` | the storage ops — the collision / the predicate's slots |
| `CREATE`/`CREATE2` | the deploy bugs |
| `SHA3`/`KECCAK256` | the hash surface |
| precompile `0x01` (`ecrecover`) | signature |
| `REVERT`/`INVALID` | the guard |
| `BALANCE`/`SELFBALANCE`/`ADDRESS`/`CALLER`/`CALLVALUE` | the context reads |

## The package signals

| Signal | The read |
|---|---|
| `Setup.sol`/`isSolved()` | the predicate-driven shape |
| a `.sol` file | the class |
| an RPC endpoint + a private key | the live instance |
| `foundry`/`hardhat`/`truffle`/`brownie` config | the toolchain |
| an ABI/JSON | the intended functions |
| a deploy script | the contract layout |

## The state signals

| Signal | The read |
|---|---|
| `cast call` the getters | the predicate's values |
| `cast storage` | the private + the predicate slots |
| `cast balance` | the ether surface |
| `cast logs`/`cast tx` | the leaked secrets / the constructor args |
| `cast code` | the bytecode (vs the `.sol`) |
