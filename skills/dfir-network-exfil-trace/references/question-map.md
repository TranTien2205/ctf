# Question map

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Map the investigation question to its modules before probing.

| Question shape | Open first | Then |
|---|---|---|
| how much left this host | `q-bytes-left-host.md` | `tap-endpoints-ip.md`, `art-srum-usage.md` |
| which external peer | `q-dominant-peer.md` | `tap-conv-tcp.md`, `tap-conv-udp.md` |
| is it periodic / beaconing | `q-periodic-beacon.md` | `beacon-delta.md`, `beacon-io-stat.md` |
| what left inside DNS | `q-what-inside-dns.md` | `chan-dns-labels.md`, `tool-dns-exfil.md` |
| does the SNI match where bytes went | `q-sni-vs-dst.md` | `fld-tls-sni.md`, `chan-fronting.md` |
| how big were the uploads | `q-post-body-size.md` | `chan-http-post.md`, `tap-exports.md` |
| did credentials leave cleartext | `q-cleartext-creds.md` | `tap-credentials.md` |
| when was the peer first seen | `q-first-seen-peer.md` | `cook-new-peers.md` |
| rare/odd ports | `q-rare-port.md` | `cook-in-set.md` |
| longest-lived session | `q-long-session.md` | `tap-conv-tcp.md` |
| fixed-size chunks | `q-chunked-exfil.md` | `deep-tcp-flags-shape.md` |
| ICMP carrying data | `q-icmp-payload.md` | `chan-icmp.md` |
| what left over FTP/SMB/TFTP/mail | `q-ftp-data-out.md` | `tap-exports.md` |
| DNS is actually HTTPS | `q-doh-tell.md` | `chan-doh.md` |
| domain-fronting | `q-fronting.md` | `chan-fronting.md`, `deep-sni-vs-esni.md` |
| upload to paste/share site | `q-paste-upload.md` | `chan-cdn-abuse.md` |
| UA clustering | `q-ua-anomaly.md` | `chan-http-post.md` |
| service does not match port | `q-port-mismatch.md` | `tap-io-phs.md` |
| highly asymmetric flow | `q-asymmetric-flow.md` | `tap-conv-tcp.md` |
| one peer owns the volume | `q-single-peer-volume.md` | `tap-endpoints-ip.md` |
| capture window | `q-capture-window.md` | `tool-tshark-version.md` |
| when the burst happened | `q-peak-interval.md` | `tap-io-stat.md` |
| protocol mix | `q-protocol-mix.md` | `tap-io-phs.md` |
| reverse shell shape | `q-reverse-shell-tells.md` | `tool-net-dialog.md` |
| DNS failure storm vs tunnel | `q-dns-failure-storm.md` | `chan-dns-labels.md` |
| which process sent it | `scen-which-process.md` | `art-sysmon-3.md`, `meth-join-process.md` |
| was there exfiltration at all | `scen-exfil-yes-no.md` | `meth-falsifier.md` |
| what was sent | `scen-what-was-sent.md` | `tap-exports.md`, `tool-dns-exfil.md` |

## Using the map

The left column is how questions are actually phrased in a Sherlock-style
bundle. Open the middle module first; the right column is where its output
feeds next. If the first module is dry after three shapes, the question
itself routes to the next artifact family — `meth-question-map`.
