# The read-family matrix — which input function and what it allows — checklist

Different input functions allow different byte filters and bounds — the read function decides which shellcode/chain bytes survive.

## Checklist

- [ ] Identify the input function from source or disasm.
- [ ] gets/scanf %s: unbounded — the whole surface is open.
- [ ] read(fd,buf,n): n may be attacker-influenced — that's the bug.
- [ ] fgets/readline: stops at newline — no \x0a in the payload.

## Abort conditions

- scanf %s stops at whitespace — \x20\x09\x0a are banned bytes.
- read(n) where n is a signed int and checked 'n <= sizeof(buf)' without 'n > 0' — negative n passes.
- fgets is safe BY DESIGN unless the size arg is wrong — check the arg.

## Falsifier

Falsifier — the read is bounded to less than the saved-state distance: no write reaches the return address; not this class.
