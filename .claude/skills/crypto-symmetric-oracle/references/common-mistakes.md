# Common mistakes — the ones that cost real time

## Encoding mistakes

- XOR'ing hex or base64 strings instead of decoded bytes.
- Treating a base64'd token's CHARACTER positions as byte positions (4 chars
  = 3 bytes).
- URL-decoding (or failing to) the ciphertext before the oracle sees it —
  match what the endpoint actually receives.

## Alignment mistakes

- Forgetting the server's fixed prefix shifts your controlled boundary by
  prefix_len mod blocksize.
- Off-by-one at block edges: when input ≡ 0 (mod block), the target byte is
  in the NEXT block.
- Measuring block size on encoded output: base64 expands, hex doubles.

## Oracle mistakes

- Keying --ok-regex to the error page instead of the success page — inverts
  the loop and decrypts noise.
- Not handling the \\x01-pad false positive at the last byte.
- Confusing a framework 500 with a crypto-layer bad-pad signal.

## Crypto-model mistakes

- Expecting CBC bit-flip to produce a clean edit — it produces one garbage
  block; plan where the garbage lands.
- Trying length-extension on HMAC or SHA-3 — neither extends.
- Assuming 'AES-256' tells you the mode — it doesn't; ECB/CBC/CTR/GCM are
  different attacks.

## Evidence mistakes

- Recording a timing oracle from 5 samples.
- Calling a flag 'found' when it's a tool's candidate string, not yet read
  from a response.
- Not recording negative results — the next attempt re-probes the dead layer.
