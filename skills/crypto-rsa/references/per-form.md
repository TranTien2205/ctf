# Per-form map — the artifact shape → the parse → the attack

## `.txt` / `.out` of numbers

```
n = 0x... / n = 12345...
e = 65537
c = 0x...
```
`re.findall(r'(?:0x)?[0-9a-fA-F]{20,}|\b\d{20,}\b')` → the integers → the sheet.

## `.pem` / `.der` / `.key` / `.crt` / `.pub`

`RSA.importKey(open(f,'rb').read())` → `n`,`e` + private fields if present.
`openssl x509 -pubkey -noout -in c.crt` for a certificate.

## `.json`

```json
[{"n":...,"e":...,"c":...}, ...]
```
`json.load` → a list of triples → `batch-gcd`/`hastad`.

## `.py` (the generator)

Read it — `next_prime`, `seed`, `getPrime(d)`, `p-1`, `e=3`, no pad. The
comment names the misuse.

## `.bin` / `.enc` / `.flag.enc`

The `c` bytes — `bytes_to_long` for the integer `c`.

## `.pcap` / `.pcapng`

A captured handshake — `n`,`e` in the certificate; `c` in the ciphertext.
`tshark`/`scapy` to extract.

## A socket transcript

`n=... e=... c=...` printed → the numbers. An interactive menu →
`crypto-symmetric-oracle`.

## A partial `.pem`

`-----BEGIN RSA PRIVATE KEY-----` with `p`/`d`/`dp`/`dq`/`qInv` redacted or
leaked → `coppersmith`/`crt`/`factor-from-d`.

## The form → the attack

| The form | The attack |
|---|---|
| numbers | the sheet → the discriminator |
| public `.pem` | `n`,`e` → the sheet |
| private `.pem` partial | `coppersmith`/`crt`/`factor-from-d` |
| `.json` list | `batch-gcd`/`hastad` |
| `.py` generator | the comment → the family |
| `.bin`/`.enc` | the `c` |
| socket | transport or oracle |
| capture | the `c` / the handshake |
