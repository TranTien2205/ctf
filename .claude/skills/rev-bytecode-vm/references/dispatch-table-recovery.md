# Recovering the dispatch table — the ISA

A custom VM's ISA is its dispatch table. Recover every handler.

## Shape A — the switch

    switch(op) {
      case 0x01: push(prog[pc++]); break;
      case 0x02: push(pop()+pop()); break;   // add
      case 0x03: push(pop()^pop()); break;   // xor
      case 0x10: push(input[ip++]); break;   // read flag byte
      case 0x20: if(pop()!=pop()) fail(); break;  // cmp
      case 0x30: pc += pop(); break;         // jmp
      case 0xff: print(win); return;
    }

Name each: 0x01=push_imm, 0x02=add, 0x03=xor, 0x10=read_char,
0x20=cmp_eq, 0x30=jmp_rel, 0xff=win.

## Shape B — the handler array

    void (*handlers[256])(ctx) = {h_push, h_add, ...};

Indexed by opcode — recover each function's semantics.

## Naming the operations

The semantics that matter for a flag-checker:
- Which op reads the input? (load_input / read_char)
- Which op compares? (cmp, test, jz)
- Which op wins? (print win / return true)

## Immediate vs register operands

Some VMs encode immediates in the byte after the opcode; others use
registers — decode whichever the handlers read.

## Evidence

The full opcode table + a decoded program listing.
