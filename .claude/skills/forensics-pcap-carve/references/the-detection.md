# Detection — when this class applies

A .pcap/.pcapng/.har/.cap handout — the answer in the traffic.

## The format read

- `.pcap` classic — the global header + records.
- `.pcapng` — Wireshark's default; SHB/IDB/EPB blocks.
- `.har` — JSON devtools export, not a pcap — har_dump.
- A USB linktype (189/220) — HID reports, not network — usb_hid.

## The first question

Which protocol dominates — io,phs/convs answers it before any
stream is followed. A 'data' protocol entry is the interesting
flow: the dissector failed on a custom encoding, which is exactly
where authors hide.

## Boundary

- An exfil timeline → dfir-network-exfil-trace.
- A media/USB linktype → routed within.
- A pure encoding → misc-encoding-carrier.
