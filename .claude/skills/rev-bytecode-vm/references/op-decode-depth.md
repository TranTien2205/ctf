# Opcode decoding — reading a custom VM end-to-end

A custom-VM challenge ships a binary with a fetch-decode-execute
loop and a program byte array. Solving it = recover the opcode
table, decode the program, invert the check. This note walks the
full route.

## Step 1 — find the dispatch loop

The loop is a repeated read-index-execute pattern. In C source it's:

    while (pc < n) {
        op = prog[pc++];
        switch (op) { ... }
    }

or a handler table:

    handlers[op](ctx);

In disassembly look for an indexed load in a loop feeding an
indirect jump or a switch — `r2 -A ./chal; afl; pdf @ main`.

## Step 2 — recover the table

Each case/handler is one instruction's semantics. Read EVERY case —
the opcode→meaning map is the VM's ISA:

- push_imm / push_reg: a constant or register onto the stack
- pop, dup, swap: stack manipulation
- add, sub, xor, and, or, shl, shr: arithmetic
- load_input / read_char: consume flag bytes
- cmp, test: compare stack top to expected
- jz, jnz, jmp, call, ret: control flow
- print / win / fail: the verdict

## Step 3 — decode the program

The prog[] byte array IS the instruction stream. Decode per the
table: pc walks opcodes and their immediates; the program is a
sequence like `push 0x41; cmp; jz +4; fail` — a per-byte check.

## Step 4 — the check is in the stream

The program is usually a linear chain of `load input[i]; transform;
cmp expected[i]; jz continue; else fail` — the expected bytes sit
in the stream as immediates.

## Step 5 — invert or replay

- Direct cmp: the expected bytes ARE the flag.
- Transformed cmp (xor/add/rol): invert the transform on the
  expected bytes.
- Hash/digest: see rev-native-check — can't invert, but can verify.

## The trace fallback

If the table is runtime-generated, static recovery is incomplete:
run it, log (pc, opcode, stack) per step — the trace decodes the
program.

## Evidence

The decoded program + the produced input accepted by the VM.
