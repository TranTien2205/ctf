# Remote fmtstr — protocol framing of specifiers


Remote fmtstr services read a line and printf it: your specifiers ride
the socket — the framing (newline, length) is the only wrinkle.

## Steps

1. Send 'AAAA.%N$p\n' over the socket; read the reflected output.
2. Line-reads need the trailing newline.
3. Specifier bytes (% etc.) are printable — no transport filtering
   usually.
4. Planted pointers need raw bytes — \x00 can't ride a line-read.

## Falsifier

The transport strips or escapes %: the specifiers never reach printf.
