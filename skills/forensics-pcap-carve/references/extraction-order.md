# Extraction order for captures

## Step 0 — the hierarchy decides

```bash
tshark -r cap.pcap -q -z io,phs
```

The protocol that dominates is the carrier. A 90% DNS capture is a
DNS-exfil challenge; a 95% TCP capture wants follow-stream.

## Per-protocol extraction

| Protocol | The flag usually rides | Commands |
|---|---|---|
| HTTP | object payloads | `tshark -r cap -q --export-objects http,./objs` then grep/inspect |
| DNS | query-name labels | `tshark -r cap -Y dns -T fields -e dns.qry.name \| sort -u` — concat labels, decode b64/hex |
| ICMP | payload bytes | `tshark -r cap -Y icmp -T fields -e data` |
| TCP | stream content | `tshark -r cap -q -z follow,tcp,ascii,N` per stream id |
| UDP | datagram payloads | `tshark -r cap -Y udp -T fields -e data.data` |
| TLS | usually NOT breakable | look for the plaintext sibling (http, ftp, smtp) in the same cap |
| FTP/SMTP | command+file | follow stream; `--export-objects` imf/ftp-data |
| USB | keystrokes in interrupt data | `-e usb.capdata` + a HID report map |

## Split-flag shapes

| Shape | Extraction |
|---|---|
| one byte per packet | `-T fields -e <field>` piped to `xxd -r -p` or tr -d |
| flag in packet lengths | `-e frame.len` or `-e tcp.len`, subtract baseline |
| flag in timing | inter-arrival deltas `-e frame.time_delta`, threshold to 0/1 |
| flag in IP IDs/ports | `-e ip.id` / `-e tcp.srcport` hex-concat |

## Traps

- Follow-stream is TCP-only and shows ONE direction per view — read both.
- `strings` over the whole capture misses anything the dissector would have
  decompressed (gzip HTTP bodies) — export objects, don't grep raw bytes.
- A protocol labeled "data" in the hierarchy is where custom encodings hide;
  `xxd` that packet directly.
