# The fmtstr field manual — the condensed runbook


1. Confirm: input is the format — '%p' reflects a pointer.
2. Offset: 'AAAAAAAA' + %N$p scan — find the marker.
3. Leak: %p dump — name the pointers (binary/libc/stack).
4. Choose the write target — GOT/ret/hook/slot.
5. Plant the target address at an arg position.
6. %Nc %N$hn — write the bytes.
7. Read-back verify, then fire the redirect.

## The one-liner kernel

    AAAAAAAA.<ptr>.%Nc.%N$hn — marker, ptr, count, byte-write
