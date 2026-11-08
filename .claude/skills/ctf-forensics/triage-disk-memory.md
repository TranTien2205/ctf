# Disk, VM and memory images

Offline images and what can be recovered from them. Depth in
`disk-and-memory.md`, `disk-advanced.md` and `disk-recovery.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Disk / VM / Memory Forensics

```bash
# Disk images
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd && photorec image.dd

# VM images (OVA/VMDK)
tar -xvf machine.ova
7z x disk.vmdk -oextracted "Windows/System32/config/SAM" -r

# Memory (Volatility 3)
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.cmdline
vol3 -f memory.dmp windows.netscan
vol3 -f memory.dmp windows.dumpfiles --physaddr <addr>

# String carving
strings -a -n 6 memdump.bin | grep -E "FLAG|SSH_CLIENT|SESSION_KEY"

# Coredump
gdb -c core.dump  # info registers, x/100x $rsp, find "flag"
```

See [disk-and-memory.md](disk-and-memory.md) for full Volatility plugin reference, VM forensics, and VMware snapshots. See [disk-advanced.md](disk-advanced.md) for deleted partition recovery, ZFS forensics, and ransomware analysis.


## Windows Password Hashes

```bash
# Extract with impacket, crack with hashcat -m 1000
python -c "from impacket.examples.secretsdump import *; SAMHashes('SAM', LocalOperations('SYSTEM').getBootKey()).dump()"
```

See [windows.md](windows.md) for SAM details and [network-advanced.md](network-advanced.md) for NTLMv2 cracking from PCAP.


## Browser Forensics

- **Chrome/Edge:** Decrypt `Login Data` SQLite with AES-GCM using DPAPI master key
- **Firefox:** Query `places.sqlite` -- `SELECT url FROM moz_places WHERE url LIKE '%flag%'`

See [linux-forensics.md](linux-forensics.md) for full browser credential decryption code.


