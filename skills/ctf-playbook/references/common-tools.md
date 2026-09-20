# Common CTF Tools Reference

## General Purpose
```
CyberChef          # Swiss-army-knife for encoding/decoding/crypto (web-based, offline capable)
Ghidra             # Free NSA reverse engineering suite
GDB + pwndbg/gef    # Binary debugging with exploit-dev enhancements
Burp Suite          # Web proxy/testing (Community edition sufficient for most CTF)
Wireshark            # Network packet analysis
```

## Web
```
sqlmap              # Automated SQL injection
ffuf/gobuster        # Content/directory discovery
Burp Suite            # Intercepting proxy, Repeater, Intruder
nuclei                # Template-based vulnerability scanner
```

## Pwn/Binary Exploitation
```
pwntools (Python)   # Exploit development framework
ROPgadget/ropper     # Gadget finding for ROP chains
one_gadget           # Find single-gadget RCE in libc
checksec             # Binary protection identification
```

## Reverse Engineering
```
Ghidra               # Free decompiler/disassembler
IDA Free              # Alternative disassembler (free version limited)
radare2/r2            # CLI reverse engineering framework
dnSpy                 # .NET decompiler
jadx                   # Android APK decompiler
angr                    # Symbolic execution framework
```

## Crypto
```
RsaCtfTool           # Automated RSA attacks
SageMath              # Advanced math (factorization, lattice attacks)
CyberChef              # Quick encoding/cipher operations
hashcat/John           # Hash cracking
```

## Forensics
```
Volatility 2/3        # Memory forensics
binwalk                # Firmware/file extraction
Autopsy/TSK             # Disk forensics
steghide/zsteg/stegsolve # Steganography
Wireshark/tshark         # Network forensics
ExifTool                  # Metadata extraction
```

<!-- An Active Directory tooling section used to sit here. It was removed:
     this tree is jeopardy CTF only, and machine or domain work belongs to the
     other toolkit. tools/check_boundary.py fails the gate if it comes back. -->

## Quick Install Reference (Linux/Debian-based)
```bash
# Python-based tools
pip install pwntools requests pycryptodome sympy gmpy2

# Common apt packages
sudo apt install binwalk steghide exiftool nmap gdb radare2 sqlmap

# Go-based tools
go install github.com/ffuf/ffuf@latest
go install github.com/OJ/gobuster/v3@latest

# Impacket
pip install impacket
```

## Offline/Air-Gapped CTF Considerations
```
- CyberChef works fully offline once loaded (single HTML file)
- Ghidra/IDA work offline after install
- Keep local copies of wordlists (rockyou.txt, SecLists) before competition
- Verify tool licenses allow offline/competition use if required by rules
```
