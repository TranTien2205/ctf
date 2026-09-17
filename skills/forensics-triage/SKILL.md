---
name: forensics-triage
description: >
  Digital forensics challenge triage. Use when CTF challenge involves PCAP,
  disk images, memory dumps, log files, steganography, or file carving.
  Supports network forensics, memory analysis, disk forensics, and file analysis.
tags: [forensics, pcap, memory, disk, steganography, logs]
environment: [ctf, lab]
---

# Forensics CTF Triage

## File Type Identification
```bash
file ./challenge
binwalk ./challenge
xxd ./challenge | head -20
strings ./challenge | head -50
```

## PCAP Quick Triage
```bash
tshark -r challenge.pcap                      # Read pcap
tshark -r challenge.pcap -Y "http"            # HTTP only
tshark -r challenge.pcap -Y "dns"             # DNS queries
tshark -r challenge.pcap --export-objects http,./exported_files
```

## Decision Tree
- PCAP file → `references/network-forensics.md`
- Memory dump → `references/memory-analysis.md`
- Disk image → `references/disk-forensics.md`
- Steganography → `references/steganography.md`
- Log files → `references/log-analysis.md`
- Suspicious binary → `references/malware-analysis.md`
- Document/PE analysis → `references/document-analysis.md`

## References
- `references/network-forensics.md` - Network capture analysis
- `references/memory-analysis.md` - Memory dump analysis with Volatility
- `references/disk-forensics.md` - Disk image forensics
- `references/steganography.md` - Steganography detection and extraction
- `references/log-analysis.md` - Log file analysis
- `references/malware-analysis.md` - Basic malware triage
- `references/document-analysis.md` - PE and document (Office/PDF) analysis

## Discipline

- Collect every parameter and size before choosing an attack; a named attack on
  guessed parameters wastes the budget.
- One technique class at a time. Budget and escalation as in
  `../LOOP_DISCIPLINE.md`.
- A recovered value is a hypothesis until it decrypts or validates against the
  supplied artifact.
