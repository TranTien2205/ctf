# The read-family matrix — which input function and what it allows

Different input functions allow different byte filters and bounds — the read function decides which shellcode/chain bytes survive.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| gets()/scanf %s / unbounded read | no bound, no filtering on length | full bytes allowed |
| read(fd,buf,n) with n controlled | n may exceed the buffer | length trick |
| fgets/readline | stops at newline | no \x0a in payload |
| memcpy/strcpy of counted length | bounded by a computed n | influence n |

## Steps

1. Identify the input function from source or disasm.
2. gets/scanf %s: unbounded — the whole surface is open.
3. read(fd,buf,n): n may be attacker-influenced — that's the bug.
4. fgets/readline: stops at newline — no \x0a in the payload.

## Falsifier

Falsifier — the read is bounded to less than the saved-state distance: no write reaches the return address; not this class.

## Traps

- scanf %s stops at whitespace — \x20\x09\x0a are banned bytes.
- read(n) where n is a signed int and checked 'n <= sizeof(buf)' without 'n > 0' — negative n passes.
- fgets is safe BY DESIGN unless the size arg is wrong — check the arg.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln>
```

## Cross-references

`bad-chars.md` · `boundary-cases.md`
