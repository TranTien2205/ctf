# Closing notes — the discipline in short

## The one rule

**The solve is `isSolved()` going `false → true` on the live chain, from a
transaction attributable to the supplied caller, with a receipt proving it was
mined.** Everything else — the `.sol`, the bytecode, the `cast` calls — is the
path to that transition.

## The three reads

1. `isSolved()` first — the predicate names the class.
2. The reachable-call inventory — which function writes the predicate's slot.
3. The state — `cast storage`/`cast balance` — the `private` secrets and the
   starting values.

## The one send

The iteration is in `cast call`/`forge` dry-runs — free and unattributable.
The `cast send` is the solve action — attributable, permanent, the last step
after the transition is named and simulated.

## The honest-status note

`web-web3` is `catalogue` — published knowledge, no local solve. The corpus is
the standard CTF web3 surface (Ethernaut/CTF/Damn-Vulnerable-DeFi shapes); a
real solve's `../field-notes.md` entry moves it to `verified`. Treat every module
as a starting point, and record what the live chain actually does.

## The trap list in one line

The class exists because a contract can't tell its caller apart from a
contract, can't hide its storage, can't control what a `call`ed contract does
back, and can't take back a transaction — every bug is one of those limits.

## The escalate rule

3 reverted transactions on the same transition, or every reachable writer of
the predicate's slot enumerated and closed → `decide.py escalate` — a wrong
class guess or a different contract in the setup, not a sixth payload.
