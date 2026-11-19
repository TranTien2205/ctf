# Verified chains — the solved business-logic exploits in this repository

A verified chain is a solve that already happened here — a `knowledge/chains/`
card with the evidence ancestry intact. This module indexes the verified
business-logic chains. A card is a **candidate shape**, never a proof —
its `first_confirming_probe` runs against THIS target before anything is
reused.

## Card 1 — Pachinko Revisited: the validator gap under a transform

- Card: `knowledge/chains/pico-pachinko-revisited-node-offset-scale-wrap-instruction-overwrite.json`
- Challenge: "NAND circuit checker on a custom CPU" (Pachinko / Pachinko Revisited)
- Platform: picoCTF 2025
- Stack: Express, Node.js, WASM, custom CPU emulator
- Mechanism alphabet: `scaling-after-check` (validator reads raw index,
  memory write uses transformed address) + `trust-in-earlier-step` (the
  checker trusts the program bytes it itself executes)

### The shape

The service loads a user-supplied NAND circuit description into a custom
CPU emulator. Node IDs are bounds-checked, then arithmetically
transformed (offset + scale) before the address is used. The transformed
address lands in a region that also holds the program's own instructions —
so an in-range-checked ID can wrap into instruction memory and overwrite
the interpreter's own bytes. A privileged instruction appended at the
collision point executes before the CPU halts.

### Pre-conditions (all must hold)

1. User indices are bounds-checked, then arithmetically transformed before
   address use.
2. The transformed address targets memory that also contains code.
3. Possible gaps: checking pre-scaling values, word-size wrapping, and a
   shared interpreter/program address space.

### The five links

1. Read the client bundle for the accepted submission format and the real
   goal; ignore unreferenced constants (dead code).
2. Map the accepted ID range from server rejection behaviour, not the UI.
3. Stop probing variants when no distinguishing signal appears; change
   mechanism layer.
4. Select an index whose post-scaling address wraps into instruction
   memory; use it as a 2-byte arbitrary write.
5. Append privileged instructions after the processing loop so the CPU
   executes them before halting.

### First confirming probe (verbatim from the card)

- Submit a minimal correct circuit.
- Submit the same circuit with one node ID just past the checker's
  documented limit.
- Compare responses.
- Expected: success from the valid circuit and a different-layer rejection
  for the out-of-range value.
- Falsifier: both are rejected identically, indicating no validator gap.

### The transferable lesson (the whole point of this skill)

`web-logic-flaw` is not about "a NAND checker". It is about **two
validators disagreeing about the same value**:

```
validator A (the check):    id < LIMIT        — reads the RAW index
sink B      (the write):    mem[off + id*S]   — uses the TRANSFORMED index
                            └─ can land inside code when off + id*S wraps
```

Every scaling-after-check, unit-confusion, and trust-in-earlier-step bug
in this skill is the same sentence wearing different nouns. When the
checker bounds `id` but the sink computes `off + id*S mod 2^w`, the
question is always: *which `id` makes `off + id*S mod 2^w` land on a byte
the checker never looked at?*

## How to use this card

```bash
# find it
python3 tools/chain_match.py --source <handout> --record <challenge>

# read it — the card carries the probe and the traps
cat knowledge/chains/pico-pachinko-revisited-node-offset-scale-wrap-instruction-overwrite.json

# run ITS probe against THIS target — never assume the shape transfers
```

The card's signals are literals from its own handout (node IDs, a NAND
checker, an emulator). A new challenge sharing the *mechanism* — a checked
value transformed before use — does not share those literals, so
`family_leads` (the prose `chain[]` vocabulary) is the route that names
this card for an unseen target. A `family_leads` hit is a card to READ,
never a probe to run.
