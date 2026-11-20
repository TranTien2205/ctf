# Pcap-carve reference map

## Route
- the-workflow, the-hierarchy, the-map-index, the-traps

## Carriers
- the-export, the-field-carve, the-follow, the-dns, the-icmp,
  the-tcp-flags, the-ipid, the-ttl, the-len, the-timing, the-dport,
  the-data-proto, the-usb, the-rtp, the-har, the-http, the-ftp,
  the-smtp, the-telnet, the-irc, the-tftp, the-smb, the-pcapng,
  the-linktype, the-split-flag, the-seq-order, the-encoding

## Discipline
- the-verify, the-falsifier, the-evidence, the-boundary,
  the-checklist, the-worked-dns, the-worked-usb, the-worked-http,
  the-worked-icmp, the-worked-field

## Detail modules

- the proto- modules — every protocol's carve surface
- the fld- modules — every one-value-per-packet field
- the shape- modules — every carrier shape (split/chunked/tunnel/timing)
- the d2- modules — the per-step workflow details
- the-reassembly-note, the-common-hides, the-field-matrix,
  the-tunnel-note, the-object-note, the-stream-note,
  the-verify-note, the-carve-recap
