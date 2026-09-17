# Memory Forensics (Volatility)

## Basic Setup
```bash
# Volatility 3 (current)
python3 vol.py -f memory.dmp windows.info

# Volatility 2 (legacy, some plugins still preferred)
volatility -f memory.dmp imageinfo
```

## Identifying OS Profile (Volatility 2)
```bash
volatility -f memory.dmp imageinfo
# Note suggested profile for subsequent commands
```

## Process Listing
```bash
# Vol3
python3 vol.py -f memory.dmp windows.pslist
python3 vol.py -f memory.dmp windows.pstree

# Vol2
volatility -f memory.dmp --profile=Win10x64 pslist
volatility -f memory.dmp --profile=Win10x64 pstree
```

## Network Connections
```bash
python3 vol.py -f memory.dmp windows.netscan
volatility -f memory.dmp --profile=Win10x64 netscan
```

## Command History / Console Buffer
```bash
python3 vol.py -f memory.dmp windows.cmdline
volatility -f memory.dmp --profile=Win10x64 cmdscan
volatility -f memory.dmp --profile=Win10x64 consoles
```

## Extracting Process Memory (for further analysis)
```bash
python3 vol.py -f memory.dmp windows.memmap --pid <PID> --dump
volatility -f memory.dmp --profile=Win10x64 procdump -p <PID> -D output/
```

## Registry Analysis
```bash
python3 vol.py -f memory.dmp windows.registry.hivelist
python3 vol.py -f memory.dmp windows.registry.printkey --key "SOFTWARE\Microsoft"
```

## Extracting Password Hashes
```bash
volatility -f memory.dmp --profile=Win10x64 hashdump
```

## File Extraction from Memory
```bash
python3 vol.py -f memory.dmp windows.filescan
python3 vol.py -f memory.dmp windows.dumpfiles --pid <PID>

volatility -f memory.dmp --profile=Win10x64 filescan | grep -i "target_file"
volatility -f memory.dmp --profile=Win10x64 dumpfiles -Q <offset> -D output/
```

## Malware Detection
```bash
# Detect hidden/injected processes
python3 vol.py -f memory.dmp windows.malfind

# YARA scanning against memory
python3 vol.py -f memory.dmp windows.vadyarascan --yara-file rules.yar
```

## Finding Strings/Secrets in Memory
```bash
strings memory.dmp | grep -i "password\|flag\|key"
bulk_extractor -o output/ memory.dmp   # Auto-extract emails, URLs, credit cards, etc
```

## Linux Memory Analysis
```bash
python3 vol.py -f memory.dmp linux.pslist
python3 vol.py -f memory.dmp linux.bash    # Bash history from memory
python3 vol.py -f memory.dmp linux.netstat
```

## Hidden Process Detection (Volatility 2)
```bash
volatility -f memory.dmp --profile=Win10x64 psxview
```

## Network Connections (Volatility 2 - connscan)
```bash
volatility -f memory.dmp --profile=Win10x64 connscan
```

## DLLs and Handles (Volatility 2)
```bash
volatility -f memory.dmp --profile=Win10x64 dlllist
volatility -f memory.dmp --profile=Win10x64 handles
```

## Browser History (Volatility 2)
```bash
volatility -f memory.dmp --profile=Win10x64 iehistory
```

## Full Memory Dump of Process (Volatility 2)
```bash
volatility -f memory.dmp --profile=Win10x64 memdump -p <PID> -D output/
```

## Volatility 3 Additional Commands
```bash
vol -f dump.raw windows.pslist
vol -f dump.raw windows.pstree
vol -f dump.raw windows.netscan
vol -f dump.raw windows.cmdline
vol -f dump.raw windows.filescan
vol -f dump.raw windows.dumpfiles --pid PID
```

## Common CTF Memory Forensics Patterns
```
1. Find suspicious process → malfind or pstree anomalies (unusual parent-child)
2. Extract process memory → search for flag string or decode embedded data
3. Check clipboard/console history → cmdscan/consoles for typed commands
4. Extract loaded DLLs/injected code → dlllist, malfind
5. Recover deleted/hidden files → filescan + dumpfiles
```

## Tools
```
Volatility 2/3      # Primary memory forensics framework
bulk_extractor       # Fast pattern extraction (emails, URLs, etc)
Rekall                # Alternative memory forensics framework
```
