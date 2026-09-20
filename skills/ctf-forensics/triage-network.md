# Network captures

PCAP work: protocol reconstruction, exfiltration, and credential material that
leaks in a capture. Depth in `network.md` and `network-advanced.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Network Forensics Quick Reference

- **TFTP netascii:** Binary transfers corrupted; fix with `data.replace(b'\r\n', b'\n').replace(b'\r\x00', b'\r')`
- **TLS keylog decryption:** Import SSLKEYLOGFILE or RSA private key into Wireshark (Edit → Preferences → Protocols → TLS)
- **TLS weak RSA:** Extract cert, factor modulus, generate private key with `rsatool`, add to Wireshark
- **USB audio:** Extract isochronous data with `tshark -e usb.iso.data`, import as raw PCM in Audacity
- **NTLMv2 from PCAP:** Extract server challenge + NTProofStr + blob from NTLMSSP_AUTH, brute-force
- **WPA/WEP WiFi decryption:** `aircrack-ng -w wordlist capture.pcap` cracks WPA handshake; WEP cracked with enough IVs. See [network.md](network.md#wpawep-wifi-decryption-from-pcap-defcamp-ctf-2016).
- **PCAP repair:** `pcapfix -d corrupted.pcap` repairs broken PCAP headers/checksums for Wireshark loading. See [network.md](network.md#corrupted-pcap-repair-with-pcapfix-csaw-ctf-2016).
- **USB HID keyboard decoding:** Extract 8-byte HID reports from USB captures; byte 2 = keycode, byte 0 = modifiers (Shift). See [peripheral-capture.md](peripheral-capture.md#usb-hid-keyboard-capture-decoding-ekoparty-ctf-2016).
- **dnscat2 reassembly:** Decode hex/base32 subdomain labels, strip 9-byte dnscat2 header, deduplicate retransmissions, reassemble payload. See [network-advanced.md](network-advanced.md#dnscat2-traffic-reassembly-from-dns-pcap-bsidessf-2017).
- **USB keyboard LED exfiltration:** Host-to-device HID SET_REPORT packets toggle Caps Lock LED. Timing encodes Morse code. See [peripheral-capture.md](peripheral-capture.md#usb-keyboard-led-morse-code-exfiltration-bitsctf-2017).

See [network.md](network.md) for SMB3 decryption, credential extraction, and [linux-forensics.md](linux-forensics.md) for full TLS/TFTP/USB workflows.


## HTTP Exfiltration in PCAP

**Quick path:** `tshark --export-objects http,/tmp/objects` extracts uploaded files instantly. Check for multipart POST uploads, unusual User-Agent strings, and exfiltrated files (images with flag text). See [network.md](network.md#http-file-upload-exfiltration-in-pcap-metactf-2026).


## SMB RID Recycling via LSARPC (Midnight 2026)

Enumerate AD accounts from PCAP by analyzing LSARPC `LsaLookupSids` calls with sequential RIDs after Guest auth. Filter: `dcerpc.cn_bind_to_str contains lsarpc`.

See [network-advanced.md](network-advanced.md#smb-rid-recycling-via-lsarpc-midnight-2026) for full RPC call sequence and Wireshark filters.


## Timeroasting / MS-SNTP Hash Extraction (Midnight 2026)

Extract crackable HMAC-MD5 hashes from MS-SNTP responses by sending NTP requests with machine account RIDs. Crack with `hashcat -m 31300`.

```bash
# Extract NTP payloads, convert to hashcat format, crack
tshark -r capture.pcapng -Y "ntp && ip.src == <DC_IP>" -T fields -e udp.payload
hashcat -m 31300 -a 0 -O hashes.txt rockyou.txt --username
```

See [network-advanced.md](network-advanced.md#timeroasting--ms-sntp-hash-extraction-midnight-2026) for payload parsing script and full attack chain.


