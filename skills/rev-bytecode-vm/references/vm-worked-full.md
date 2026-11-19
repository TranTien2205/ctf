# Worked — a custom VM flag-checker, end-to-end

A binary `chal` takes argv[1] as the flag, runs a VM over a program
array, prints WIN/LOSE.

## 1. Triage

    r2 -A ./chal; afl; iz
    pdf @ main

`iz` shows "WIN"/"LOSE"; `main` calls `vm_run(prog, argv[1])`.

## 2. The dispatch

    pdf @ sym.vm_run
    # case 0x01: push(imm)
    # case 0x10: push(argv[1][ip++])     -- read
    # case 0x20: cmp, jz
    # case 0xff: win

Table recovered: 0x01=push, 0x02=xor, 0x10=read, 0x20=cmp_eq,
0x30=jmp, 0xff=win.

## 3. The program

prog[] decodes (per read+transform+cmp):

    10          ; read flag[i]
    01 0x37     ; push 0x37
    02          ; xor
    01 0x52     ; push 0x52
    20          ; cmp_eq
    30 +6       ; jz continue
    ... fail

Per byte: flag[i] ^ 0x37 == 0x52 → flag[i] = 0x65 'e'.

## 4. Invert

Extract every expected+key pair; flag[i] = expected[i] ^ key[i].

## 5. Verify

    ./chal 'e...'  → WIN

## Evidence

The decoded program listing + the accepted input.
