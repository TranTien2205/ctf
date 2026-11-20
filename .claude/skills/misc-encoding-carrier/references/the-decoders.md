# The standard decoders — run them first

A blob that decodes cleanly under hex/base64/base32/url was an
encoding, not a cipher — the class closes. enc_detect peels
hex/base64/base32/url/gzip/zip/binary/decimal/octal/base85/morse.

## First

Standard decoders before any cipher guess — a clean decode closes it.

## The chain

Decode until plain or a layer fails.
