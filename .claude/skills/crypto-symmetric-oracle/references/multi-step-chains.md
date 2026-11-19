# Multi-step chains — when one primitive isn't the flag

The flag is rarely one oracle call away. The standard chains:

## Chain: ECB → cut-and-paste → admin → flag

1. ecb-detection: confirm ECB + map field blocks.
2. ecb-cut-and-paste: mint the 'admin' block from a chosen plaintext.
3. token-forgery-workflows: splice, submit, read the privileged response.
4. pre-flag the response bytes.

## Chain: padding oracle → decrypt → re-encrypt → forged token

1. cbc-padding-oracle: decrypt the captured token (~N×256 requests).
2. token-forgery-workflows: re-encrypt a modified plaintext (the same
   oracle encrypts if you control IV+blocks).
3. Submit; read the flag.

## Chain: nonce reuse → crib-drag → plaintext → embedded flag

1. iv-reuse-detection: collect the pair.
2. crib-drag: recover both plaintexts.
3. The flag sits inside one of them — read, don't re-encrypt.

## Chain: length-extension → forged MAC → admin endpoint → flag

1. hmac-vs-raw-mac: confirm raw MD construction.
2. length-extension: emit forged (msg||glue||append, mac).
3. Submit; the privileged response carries the flag.

## Chain: nothing → key-path → decrypt

1. authenticated-boundary fires (class closed for oracles).
2. key-path: find the seed/key in source or handout.
3. Decrypt the flag offline — crypto, but no oracle.

## The rule

Each chain step has its own falsifier; a chain dies at the FIRST step that
falsifies, not at the end. Verify step-by-step.
