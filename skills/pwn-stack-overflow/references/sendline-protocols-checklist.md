# The sendline protocol — remote service shape — checklist

A remote pwn service reads a line, processes it, responds. The payload must survive the transport: newlines, length limits, and the service's framing.

## Checklist

- [ ] nc <host> <port> — read the banner/prompt first.
- [ ] Send payload + '\n' — most reads want the newline.
- [ ] For binary protocols: the length field may bound your input.
- [ ] Read the response; the flag or the crash is the answer.

## Abort conditions

- A length-prefixed protocol bounds the payload — the offset must fit inside it.
- Newline-terminated reads need the trailing '\n'.
- Some services read a fixed number of bytes regardless of newlines — send exactly that many.

## Falsifier

Falsifier — the service's read bound stops before your offset: the payload can't reach the saved state at this size.
