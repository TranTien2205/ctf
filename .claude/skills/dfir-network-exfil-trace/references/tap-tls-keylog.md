# TLS decryption with a keylog file

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

When the bundle ships a session-key file, decryption is one preference, and
the encrypted channel becomes ordinary HTTP/DNS-visible traffic.

## Command

```bash
tshark -r capture.pcapng -o tls.keylog_file:sslkeys.log -q -z http,tree
```

Measured in `tshark -G currentprefs` on this box: `tls.keylog_file` (line
5387), `ssh.keylog_file` (5019), `wg.keylog_file` (5630).

## Reading

After decryption, all the HTTP taps, `follow,tcp`, and `--export-objects
http` apply to what was TLS. The "what left over the encrypted channel"
question is then an HTTP question, not a TLS question.

## Evidence rule

Say explicitly that the content was recovered via keylog decryption and name
the keylog file. The excerpt must come from the decrypted pass — never quote
TLS ciphertext and claim its contents.

## Trap

Keylog entries map to sessions by client random; a capture truncated before
the handshake leaves later sessions undecryptable even with the file. Check
`io,phs` after `-o` to confirm decrypted protocols appeared.

## Pivot

No keylog shipped -> SNI/`ip.dst` are the only destination names;
`fld-tls-sni`.
