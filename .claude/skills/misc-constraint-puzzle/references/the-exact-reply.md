# The exact reply — trailing bytes matter

`send:1\n` — does the answer want `\n`, `\r\n`, nothing? Capture
the reply shape verbatim; a wrong terminator reads as silence.

## The bytes

Send exactly the captured reply shape.

## Verbatim

The captured reply shape is the contract.
