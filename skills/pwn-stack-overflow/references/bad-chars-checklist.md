# Bad characters — which bytes the input path strips — checklist

The read function's allowed byte set determines which shellcode/chain bytes are legal. A banned byte kills the exploit silently.

## Checklist

- [ ] Identify the input function and its byte-filtering behavior.
- [ ] For shellcode: sc_gen reports which banned bytes the stub contains — pick the stub that avoids them.
- [ ] For ROP addresses: a banned byte in an address needs a different address or a write gadget.
- [ ] Test: send a probe of all bytes 0x00-0xff and see which survive.

## Abort conditions

- \x00 (null) always terminates C strings — in scanf %s it also ends input.
- \x0a (newline) ends fgets/line reads.
- A ROP chain with \x00 in an address needs the address rewritten via a mov gadget.

## Falsifier

Falsifier — a needed address/opcode contains a banned byte and no equivalent exists: the chain must be reworked or the class is wrong.
