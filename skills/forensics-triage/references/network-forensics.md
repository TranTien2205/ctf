# Network Forensics (PCAP)

## Basic Analysis

### tshark Commands
```bash
# Read pcap
tshark -r challenge.pcap

# HTTP requests
tshark -r challenge.pcap -Y "http" -T fields -e http.host -e http.request.uri -e http.response.code

# DNS queries
tshark -r challenge.pcap -Y "dns" -T fields -e dns.qry.name

# FTP credentials
tshark -r challenge.pcap -Y "ftp" -T fields -e ftp.request.command -e ftp.request.arg

# Telnet (cleartext)
tshark -r challenge.pcap -Y "telnet" -T fields -e telnet.data

# Follow TCP stream
tshark -r challenge.pcap -q -z follow,tcp,ascii,0
```

### Wireshark Filters
```
http                          # HTTP traffic
dns                           # DNS queries
ftp                           # FTP commands
telnet                        # Telnet data
tcp.port == 80               # Port 80
ip.src == 192.168.1.1       # Source IP
http.request.method == "POST" # POST requests
tcp.stream eq 5              # Specific TCP stream
```

## Extract Files from PCAP
```bash
# Wireshark: File > Export Objects > HTTP/SMB/TFTP
tshark -r challenge.pcap --export-objects http,./exported
tshark -r challenge.pcap --export-objects smb,./exported
```

## Common PCAP Patterns
- Cleartext credentials: FTP, Telnet, HTTP Basic Auth
- DNS exfiltration: Check TXT record data
- ICMP tunneling: Extract data from ICMP payloads
- HTTP file transfers: Export objects
- Steganography: Check unusual protocols

## Tools
```
Wireshark          # GUI analysis
tshark             # CLI analysis
NetworkMiner       # Auto-extract files/credentials
zeek               # Network monitoring
chaosreader        # Session reconstruction
```
