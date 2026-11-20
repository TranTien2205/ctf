# Class boundaries

- An exfiltration TIMELINE/attribution → dfir-network-exfil-trace.
- A pure encoding in the bytes → misc-encoding-carrier.
- A disk image → forensics-disk-image.
- A media file → forensics-stego.

## The discriminator per peer

- **dfir-network-exfil-trace** — the answer is *who exfiltrated what
  when*, not a flag string. Same pcap, different question.
- **misc-encoding-carrier** — the bytes themselves are an encoded
  message (base64 chain, a cipher); the packet structure is
  incidental.
- **forensics-disk-image** — a filesystem/disk artifact, not traffic.
- **forensics-stego** — a media file's pixels/samples, not traffic.
- **A USB capture** — linktype 189/220 routes IN to usb_hid, not
  out — it IS this class's job, just not a network flow.
- **A .har** — JSON HTTP export — har_dump inside this class.
