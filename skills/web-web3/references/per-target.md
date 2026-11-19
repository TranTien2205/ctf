# Per-target map — the contract type → the likely bug

## The challenge-contract inventory

| Contract type | The likely bug |
|---|---|
| a `Setup`/`Challenge` pair | the predicate-driven solve — read `isSolved()` |
| a `Proxy`/`Implementation` pair | delegatecall, storage-collision, uninitialized-proxy |
| a `Vault`/`Bank`/`Wallet` | reentrancy, accounting, the force-feed |
| a `Token`/`ERC20`/`ERC721` | overflow (old), approval, the hook-reentrancy |
| a `Library`/`WalletLibrary` | delegatecall-into-code, the uninitialized init |
| a `Lottery`/`Guess`/`Flip` | weak-randomness |
| a `Lock`/`Vault`-locked | visibility (private secret) |
| a `Shop`/`Buyer`/`Sell` | a view/pure function returning a lie (price), or interface-mismatch |
| a `Gate`/`Gatekeeper` | `msg.sender != tx.origin`, `gasleft()`, a key derived from data |
| a `King`/`Elevator`/`Shop` | a contract that must handle an unexpected callback/revert |
| a `Preservation`/`PuzzleWallet` | delegatecall / storage-collision |
| a `Recovery`/`SimpleToken` | a lost address — `cast` the deploy, or CREATE the known address |
| a `Dex`/`Staking`/`FlashLoan` | accounting-vault, share-price, flash-loan skew |
| a `Denial`/`DOS` | a withdraw-loop that runs out of gas — a malicious partner refusing |
| an `AlienCodex`/`array`-extender | an `array.length--` underflow to write any slot (pre-0.8 `array.length`) |

## The "the contract is missing" case

`Recovery`/`simpleToken` — a deployed contract's address is lost. Recover it:
- the deploy tx creates it — `cast tx <deploy-hash>` shows the `creates` address
- `cast getAddress <deployer> <nonce>` computes the CREATE address
- CREATE2: `keccak256(0xff . deployer . salt . keccak256(initcode))[12:]` — `cast`/`cast computeAddress`

## The "many contracts" case

A setup that deploys several contracts — map them: which holds the predicate,
which is the attack surface, which is a red herring. The predicate's contract is
the target; the others are the path to it.
