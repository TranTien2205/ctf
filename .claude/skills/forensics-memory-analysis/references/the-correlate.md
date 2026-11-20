# Correlating memory with other artifacts

A memory image rarely stands alone in a bundle — it sits beside a
pcap, a disk image, or an event log. Correlate rather than treat
in isolation:

- netscan endpoint ↔ a pcap flow — confirms a C2 channel.
- filescan path ↔ a disk-image file — confirms what was opened.
- cmdline timestamp ↔ a Security.evtx 4688 event — confirms run.
- A memory-resident credential ↔ an auth.log success — who used it.

The correlation is often the finding — the pcap shows the traffic,
the memory shows the process that made it.

Each side corroborates the other — cite both in the record.
