# Bad characters — which bytes the input path strips

The read function's allowed byte set determines which shellcode/chain bytes are legal. A banned byte kills the exploit silently.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| scanf %s stops at whitespace | \x20\x09\x0a\x0b\x0d banned | avoid them |
| fgets stops at newline | \x0a banned | no newline bytes |
| read(n) raw | no byte filter | any bytes OK |
| input goes through a filter/validator | custom banned set | enumerate it |

## Steps

1. Identify the input function and its byte-filtering behavior.
2. For shellcode: sc_gen reports which banned bytes the stub contains — pick the stub that avoids them.
3. For ROP addresses: a banned byte in an address needs a different address or a write gadget.
4. Test: send a probe of all bytes 0x00-0xff and see which survive.

## Falsifier

Falsifier — a needed address/opcode contains a banned byte and no equivalent exists: the chain must be reworked or the class is wrong.

## Traps

- \x00 (null) always terminates C strings — in scanf %s it also ends input.
- \x0a (newline) ends fgets/line reads.
- A ROP chain with \x00 in an address needs the address rewritten via a mov gadget.

## Commands

```bash
python3 tools/sc_gen.py execve64 --raw   # reports any \x00\x0a\x0d\x20 bytes
```

## Cross-references

`ret2shellcode.md` · `read-family.md`
