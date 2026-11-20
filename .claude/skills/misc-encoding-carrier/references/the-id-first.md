# Identify the carrier BEFORE decoding

Alphabet, distinct-character count, and length modulus separate
hex/base64/base32/base85/base58 at a glance — one command names the
carrier; only then decode.

    python3 tools/enc_detect.py --file blob.txt

## The tell

Alphabet + count + modulus names the carrier in one command.

## One command

Alphabet + count + modulus -> the carrier.
