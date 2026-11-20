# Channel: TLS with a shipped keylog

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

`-o tls.keylog_file:sslkeys.log` then the whole HTTP toolkit applies. Verify decryption worked (`io,phs` should now show `http`/`json`) before quoting any 'decrypted' field. `tap-tls-keylog` has the measured preference names.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
