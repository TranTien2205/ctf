# Per-channel map — how the value arrives → the parse

## File on disk

`*.pem`, `*.der`, `*.crt`, `*.key`, `*.json`, `*.txt`, `*.bin`, `*.py` — read
and parse. `RSA.importKey` for keys/certs; `json.load` for lists; `re.findall`
for raw numbers.

## Socket / `nc`

```
nc host port
n = ...
e = ...
c = ...
```
`recv` → parse the ints. If the socket *responds to input* → an oracle
(`crypto-symmetric-oracle`).

## Stdout / a script's output

`python3 chal.py` → prints `n`,`e`,`c` → capture and parse.

## A capture file

`.pcap`/`*.cap` → `tshark -r x.pcap -Y rsa` or `scapy` → the handshake `n`,`e`
and the `c`.

## A certificate / chain

`.crt`/`.pem` chain → `openssl x509 -pubkey` → `n`,`e`. A *partial* chain → the
leaked fields.

## A hexdump / a `.der`

`openssl asn1parse -in x.der` → the `SEQUENCE` fields → `n`,`e`,`d`,`p`,`q`.

## The channel → the class

| Channel | The class |
|---|---|
| file with numbers | `crypto-rsa` |
| socket printing numbers | `crypto-rsa` (transport) |
| socket computing | `crypto-symmetric-oracle` |
| a web endpoint | `web-*` |
| a capture | `crypto-rsa` (the RSA in it) |

## The rule

The channel is *how* the values arrive — the *class* is what the bug is. Parse
the values into the sheet; the channel rarely matters after extraction.
