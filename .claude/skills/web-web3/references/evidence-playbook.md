# Evidence playbook — the record-and-verify sequence

## Step 1 — capture the start

```bash
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC    # → false — the BEFORE
cast call $CH "owner()(address)" "locked()(bool)" --rpc-url $RPC
cast balance $CH --rpc-url $RPC
```

## Step 2 — the exploit

```bash
# the attributable tx
cast send $CH "fn(args)" <args> --private-key $KEY --rpc-url $RPC
# or the attack contract:
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
cast send $SOLVER "run()" --private-key $KEY --rpc-url $RPC
```

## Step 3 — the verify

```bash
cast receipt <txhash> --rpc-url $RPC                  # status 0x1, from = caller
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # → true — the AFTER
cast tx <txhash> --rpc-url $RPC                      # the calldata + the from
cast run <txhash> --rpc-url $RPC                      # the trace
```

## Step 4 — the record

```text
the chain id + the RPC host
the supplied caller's address (never the key)
the setup + challenge addresses
the predicate's exact expression
the calldata / the attack-contract source
the tx hashes + the receipts
the before/after isSolved() + getters + slots
```

## Step 5 — the hooks.py call

```bash
python3 tools/hooks.py post-probe --challenge <name> \
  --verdict confirms --evidence "isSolved()=true tx=0x<hash>" \
  --response "$(cast call $SETUP 'isSolved()(bool)' --rpc-url $RPC; cast receipt <txhash> --rpc-url $RPC)"
```

The `--response` is the verbatim `cast` output — the substring check validates
the `isSolved()=true` quote.

## The "what if the flag isn't in a response" rule

The flag isn't in the contract's return — it's the platform's reward for
`isSolved() == true`. The solve's evidence is the on-chain transition; the
flag's evidence is the platform's response. Both recorded.

## The "partial evidence" case

A `status: 0x1` + a still-`false` `isSolved()` → the tx mined but didn't solve —
record the tx + the still-false read as a NEGATIVE — the transition was wrong.
