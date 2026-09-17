# Document & Executable Analysis (Forensics/CTF)

## PE Analysis (Suspicious Executables)
```bash
# Use PE Studio, Detect It Easy (DIE)
# Check imports for suspicious API calls
strings suspicious.exe | grep -iE "CreateRemoteThread|VirtualAlloc|WriteProcessMemory"

# VirusTotal (offline)
# Use YARA rules
yara -r rules/ suspicious.exe
```

### Suspicious Import Indicators
```
VirtualAlloc + WriteProcessMemory + CreateRemoteThread   → Process injection
WinExec / ShellExecute                                     → Command execution
InternetOpenUrl / URLDownloadToFile                        → Network/download capability
CryptEncrypt / CryptDecrypt                                → Encryption (possible ransomware)
RegSetValue                                                 → Persistence via registry
```

## Document Analysis (OLE/Office)
```bash
# OLE/Office documents
olevba document.docm          # Extract macros
oleid document.docm           # Identify OLE features
python3 oledump.py document.docm  # Dump streams
```

## PDF Analysis
```bash
pdfid.py document.pdf
pdf-parser.py --object OBJ_NUM document.pdf
```

## Tools Reference
```
PEStudio / Detect It Easy (DIE)  # Static PE analysis
olevba / oleid / oledump          # Office macro/OLE extraction
pdfid.py / pdf-parser.py          # PDF structure analysis
YARA                              # Pattern-based malware identification
```
