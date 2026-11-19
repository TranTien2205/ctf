# 32-bit fmtstr — the x86 shape


x86 (32-bit): ALL args on the stack — %1$p already reads stack memory;
writes are 4-byte; addresses are 4 bytes — everything is smaller.

## Steps

1. All args on the stack — your input appears at a low N.
2. %n writes 4 bytes (the whole pointer).
3. Addresses are 4 bytes — plant with struct.pack('<I', addr).
4. No register args — the first %p already reads stack data.

## Falsifier

The binary is 64-bit: different arg layout; see x86-vs-x64.

x86 chains are often simpler — no register-arg complication.
