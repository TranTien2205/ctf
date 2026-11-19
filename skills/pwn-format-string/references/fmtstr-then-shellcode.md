# Fmtstr feeding shellcode — write the code, then the ptr


The %n write can place SHELLCODE bytes into a writable+executable region,
then a second write redirects execution into it — self-contained exploit.

## Steps

1. Find a WX region (rare — check the triage) or make the write land in
   an executable buffer.
2. %n sequence writes the shellcode bytes into it.
3. A second %n write points a return/GOT at the shellcode's address.
4. python3 tools/sc_gen.py execve64 --raw — the bytes.

## Falsifier

No WX region and no RWX path: shellcode can't execute — use ROP-style
writes to existing code instead.
