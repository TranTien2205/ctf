# Length extension — hash(secret||msg) forgery — playbook

A MAC built as sha1/sha256/md5 of secret||message is forgeable: the hash's internal state after the message is the digest itself — continue it with your appended data.

## Ordered playbook

1. Confirm the construction: hash(secret || known_message) with a Merkle-Damgard hash.
2. python3 tools/crypto_attack.py length-extension --hash sha1 --mac <original-mac> --secret-len <N> --orig <known-msg> --append '&admin=1'
3. The tool emits the forged MAC AND the exact bytes to submit (msg || glue-padding || appended).
4. Submit the extended message with the forged MAC; acceptance = class impact confirmed.
5. If the secret length is unknown, iterate --secret-len over the plausible range (usually 8..64) — the server tells you which length forged correctly.

## Falsifier

Falsifier — the forged MAC is rejected under every secret length tried: the MAC is HMAC, a keyed PRF, or a sponge hash, or the server appends after your data (suffix MACs don't extend forward).

## Commands

```bash
python3 tools/crypto_attack.py length-extension --hash sha1 --mac <mac> --secret-len 16 --orig 'user=guest' --append '&admin=1'
python3 tools/crypto_attack.py length-extension --help
```
