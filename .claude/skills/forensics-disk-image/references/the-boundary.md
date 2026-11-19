# Class boundaries

- A photo/media with hidden data → forensics-stego.
- A filesystem timeline for an investigation →
  dfir-filesystem-timeline.
- A pure encoding in a file → misc-encoding-carrier.

## The discriminator per peer

- **forensics-stego** — the flag is in the *pixels/samples*, not the
  filesystem structure. A carved media file whose content hides the
  flag is stego; a deleted media file's bytes is disk-image.
- **dfir-filesystem-timeline** — the answer is a *timeline or an
  attribution*, not a flag file. DFIR reads the same $MFT/journal
  artifacts but for the event history.
- **misc-encoding-carrier** — the file's bytes are an *encoded
  message*, not a deleted/hidden filesystem object.
- **forensics-memory-analysis** — a memory/RAM image, not a disk.
- **forensics-pcap-carve** — a packet capture, not a disk image.

## The rule

Match the artifact: disk/volume/container → here; pixels/samples →
stego; timeline/attribution → dfir; memory → memory-analysis; pcap
→ pcap-carve.
