# VM-Based / Bytecode Analysis

## Recognizing Custom VM Implementations
```
Common pattern in CTF reverse engineering challenges:
- Large switch-case or jump table dispatching "opcodes"
- A "bytecode" array/buffer processed sequentially
- Virtual "registers" or stack simulated in a local array/struct
- Instruction pointer (IP) variable incrementing through bytecode
```

## Identifying the Dispatch Loop
```c
// Typical structure to look for in decompiled code
while (ip < bytecode_len) {
    opcode = bytecode[ip++];
    switch (opcode) {
        case 0x01: /* ADD */ ...
        case 0x02: /* SUB */ ...
        case 0x03: /* PUSH */ ...
        // ...
    }
}
```

## Approach for Custom VM Challenges

### Step 1: Extract the Bytecode
```bash
# Usually embedded in .rodata or .data section, or read from input file
objdump -s -j .rodata ./binary
```

### Step 2: Reverse the Opcode Handlers
```
1. Identify each case in the switch statement
2. Determine what each opcode does (arithmetic, memory access, comparison, jump)
3. Build an opcode reference table (opcode value -> operation -> operand format)
```

### Step 3: Write a Disassembler/Emulator
```python
# Custom Python emulator matching the VM semantics
class VM:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.ip = 0
        self.stack = []
        self.registers = [0] * 16

    def run(self):
        while self.ip < len(self.bytecode):
            op = self.bytecode[self.ip]
            self.ip += 1
            if op == 0x01:  # ADD
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == 0x02:  # PUSH
                val = self.bytecode[self.ip]
                self.ip += 1
                self.stack.append(val)
            # ... continue for all opcodes
```

### Step 4: Solve the Challenge Logic
```
- Once emulator works, trace what the VM program is checking against user input
- Often it's validating a flag character-by-character or via checksum
- Either brute force valid input or reverse the check to derive the flag directly
```

## Real-World VM Obfuscators (Commercial Protectors)
```
VMProtect       # x86/x64 code virtualized into custom bytecode + VM
Themis/Themida  # Similar approach, adds anti-debug layers

# For these, full devirtualization is extremely time-consuming
# CTF challenges rarely use full commercial VM protectors due to complexity
# If encountered, consider:
# - Dynamic tracing (record all real CPU instructions executed during a run)
# - Focus on side effects/output rather than full understanding of VM internals
```

## Using angr for Symbolic Execution (Bypass Complex VM Checks)
```python
import angr

proj = angr.Project('./binary')
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)

# Explore to find state where "Correct" message is reached
simgr.explore(find=lambda s: b"Correct" in s.posix.dumps(1))
if simgr.found:
    solution_state = simgr.found[0]
    print(solution_state.posix.dumps(0))  # Recovered stdin that satisfies checks
```

## Tools
```
angr            # Symbolic execution framework - great for VM/complex logic challenges
Ghidra/IDA       # Decompile dispatch loop to understand opcode semantics
Unicorn Engine   # CPU emulator - useful for tracing real VM execution dynamically
```
