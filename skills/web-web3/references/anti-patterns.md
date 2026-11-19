# Anti-patterns — the patterns that look like progress but aren't

## The simulation-as-solve anti-pattern

Running `forge test`/`cast call` and declaring the challenge solved — the fork/
dry-run is LOCAL; the live chain is unchanged. The solve needs a live `cast send`
+ a re-read `isSolved()`. The dry-run is a step, not the finish.

## The send-guessing anti-pattern

Sending `cast send` after `cast send` guessing at the transition — each is
attributable and permanent. The enumeration (`cast call`/the function list)
finds the transition for free; the send is the last step, not the search.

## The "many variants" anti-pattern

Sending 5 slightly-different `cast send`s for the same transition after it
reverted — the revert reason is the signal, not a payload-fuzzing problem. Read
the `cast run` trace; fix the unmet precondition; a sixth variant doesn't help.

## The private-key-in-notes anti-pattern

Recording the supplied private key in notes/scripts — it's a credential.
Record the ADDRESS and "the supplied key was used," never the key value.

## The instance-hardcoding anti-pattern

Hardcoding the RPC/key/addresses in a script — the challenge is per-instance;
a new instance's values differ. Always read from the live challenge.

## The source-trust anti-pattern

Reasoning only about the shipped `.sol` — the deployed bytecode can differ.
`cast code` early; if it differs, the bytecode is the truth.

## The "the obvious one is too easy" anti-pattern

Skipping the bare `setOwner`/`unlock` because it "can't be that easy" — the
unguarded setter IS the intended solve in most CTF web3. Check it first.

## The flag-in-response anti-pattern

Looking for a `flag{...}` in a `cast` output — there's no flag in the contract
response; the flag is the platform's reward for `isSolved() == true`. The
on-chain state change is the solve's proof; the flag comes after.

## The wrong-caller anti-pattern

Sending the exploit from a different key than the supplied caller — the tx is
attributable to the wrong EOA. `cast tx`'s `from` must equal `cast wallet
address --private-key $KEY`.

## The unbounded-loop anti-pattern

A reentrancy/`for` exploit with no termination bound — it runs out of gas and
reverts the whole tx. Bound the recursion by the target's balance or a counter.
