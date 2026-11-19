# Per-endpoint map — the channel → what it carries

## A file

`.pem`/`.der`/`.crt`/`.key` → `n`,`e` (public) or `n`,`e`,`d`,`p`,`q`,`dp`,`dq`,
`qInv` (private). `.json`/`.txt`/`.bin` → the integers. `.py` → the generator.
**Read, don't probe** — the file is the handout.

## A socket / `nc host port`

- **prints `n`,`e`,`c` then exits** → transport; treat as the numbers.
- **a menu / a loop** (encrypt, decrypt, sign, query) → `crypto-symmetric-oracle`
  — a *computing* service, not this class.
- **returns a signature on a fixed `m`** → `crt` Bellcore if it can fault;
  a signature-forgery class if it signs arbitrary `m`.

## An HTTP endpoint

A web endpoint that serves RSA values → the *web* class owns it (`web-*`). This
class owns the RSA math, not the transport.

## A `.pcap` / capture

A captured handshake or key exchange → the RSA values in the capture; the
recovery is the same.

## The boundary

- numbers → `crypto-rsa`
- a computing oracle → `crypto-symmetric-oracle`
- `g`,`h`,a curve → `crypto-ecc-dlog`
- a keystream → `crypto-prng`

## The rule

The endpoint determines the *class*, the numbers determine the *attack*. Read
the numbers first; the endpoint tells you whether the bug is in the math or the
service.
