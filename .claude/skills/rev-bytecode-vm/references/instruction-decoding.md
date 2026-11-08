# Bytecode and custom VMs: decode the instruction set first

A custom-VM challenge ships a program in a bespoke instruction set — the flag
is the input the program accepts. You can't patch a VM the way you patch a
native compare; you read the program.

## Step 1 — find the instruction table

```bash
strings -a -t x ./bin | grep -iE 'usage|op|opcode|instr'   # often named in source
```

The opcode dispatch is a jump table or a `switch`/`if-else` chain in the
interpreter function — in `objdump -d` it's the big indirect `jmp *table(,%eax,4)`
or the long if-else on the opcode byte.

## Step 2 — map opcode → operation

Each case in the dispatcher is one instruction: `MOV/ADD/XOR/LOAD/STORE/
CMP/JMP/JNZ/CALL`. Write the mapping as you read them — a dozen opcodes
covers most CTF VMs.

## Step 3 — disassemble the embedded program

The VM's bytecode lives in `.rodata` or a big initialized array. Disassemble
it against your opcode map — by hand, or write a 30-line Python loop:

```python
code = open("embedded.bin","rb").read()
OPS = {0x01:"MOV",0x02:"ADD",0x03:"XOR",0x10:"CMP",0x20:"JMP",0x30:"HALT"}
i = 0
while i < len(code):
    op = code[i]; i += 1
    print(OPS.get(op, "?%02x" % op), code[i:i+4]); i += 4
```

## The check shape that decides the answer

| Program does | Answer is |
|---|---|
| reads input, compares byte-by-byte to constants | the constants — read them out |
| transforms input (xor/permute), compares to a digest | invert the transform on the digest |
| computes a hash and compares | can't invert — emulate or patch the VM |
| navigates a graph/maze | the path is the flag — BFS the transitions |

## The fast path

If the VM's `cmp`/`jz` on a wrong byte exits — a single wrong-byte early-exit
is a *side-channel*: input that survives longer is closer to right. Feed
byte-by-byte and time/step the exit to recover the flag without disassembling.

## Falsifier

The binary isn't a VM at all — the "instruction set" is a real architecture
(ARM, MIPS, x86); route to `../rev-native-check/` or `../pwn-binary-triage/`.

## Traps

- The opcode table is *in the binary*, not in the bytecode file — find the
  dispatcher in the interpreter, not the embedded blob.
- Some VMs pack operands in the opcode byte (`op | arg<<4`); decode the
  operand format before reading the program.
- The program may be *self-checking* — it can hash its own bytes and bail
  if you patch them; read it, don't modify it.
