# Log Analysis (Forensics)

## Common Log Types
```
Web server logs        access.log, error.log (Apache/Nginx)
Application logs        Custom app-specific logging
System logs             /var/log/syslog, /var/log/auth.log (Linux)
Windows Event Logs      Security.evtx, System.evtx, Application.evtx
Firewall logs           iptables, pfSense, etc.
Database logs           MySQL general_log, PostgreSQL log
```

## Web Server Log Analysis

### Apache/Nginx Access Log Format
```
IP - - [timestamp] "METHOD /path HTTP/1.1" status size "referer" "user-agent"
```

### Finding Attack Patterns
```bash
# SQL injection attempts
grep -iE "union.*select|' or '1'='1|sleep\(" access.log

# XSS attempts
grep -iE "<script|onerror=|onload=" access.log

# Path traversal attempts
grep -iE "\.\./|\.\.%2f" access.log

# Common webshell access
grep -iE "\.php\?c=|cmd=|shell\." access.log

# Scanner/tool user-agents
grep -iE "nikto|sqlmap|nmap|burp|gobuster" access.log
```

### Timeline of Specific IP Activity
```bash
grep "192.168.1.100" access.log | sort -t'[' -k2
```

### Status Code Analysis (find successful attacks)
```bash
awk '{print $9}' access.log | sort | uniq -c | sort -rn
grep " 200 " access.log | grep -iE "admin|shell|backdoor"
```

## Windows Event Log Analysis

### Key Event IDs for Security Investigation
```
4624    Successful logon
4625    Failed logon
4634    Logoff
4720    User account created
4728    User added to security group
4672    Special privileges assigned (admin logon)
1102    Audit log cleared (attacker covering tracks)
7045    New service installed
4698    Scheduled task created
```

### Parsing with PowerShell
```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} | Format-Table TimeCreated, Message
```

### Parsing with python-evtx / EvtxECmd
```bash
python3 -m evtx dump Security.evtx > security_events.xml
EvtxECmd.exe -f Security.evtx --csv output/ --csvf security.csv
```

## Linux Auth Log Analysis
```bash
# Failed SSH login attempts
grep "Failed password" /var/log/auth.log

# Successful logins
grep "Accepted password\|Accepted publickey" /var/log/auth.log

# Sudo usage
grep "sudo:" /var/log/auth.log

# Brute force detection (count failed attempts per IP)
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn
```

## Timeline Analysis (Log2Timeline / Plaso)
```bash
log2timeline.py timeline.plaso evidence.raw
psort.py -o l2t timeline.plaso > timeline.csv
```

## Windows Event Logs (Quick Reference)
```bash
# Use evtx_dump.py or EvtxECmd
python3 evtx_dump.py security.evtx > security.xml
```

## Correlating Multiple Log Sources
```bash
# Combine timestamps from different logs to build attack timeline
# Sort by timestamp across web, auth, and application logs
cat access.log auth.log | sort -k1,2 > combined_timeline.log
```

## Log Analysis Tools
```
grep/awk/sed          # Quick CLI pattern matching
GoAccess               # Real-time web log analyzer with visual dashboard
Splunk/ELK Stack        # Full log aggregation and search (if available)
lnav                    # Log file navigator with SQL-like queries
Chainsaw                # Fast Windows event log searching/hunting tool
```

## CTF-Specific Log Analysis Patterns
```
1. Identify anomalous requests (unusual paths, high frequency from single IP)
2. Look for the specific exploit request that led to compromise
3. Trace attacker's subsequent actions (data exfil, persistence commands)
4. Check for log tampering/deletion (gaps in sequence, cleared logs)
5. Extract flag if embedded in log entries themselves (encoded/obfuscated)
```
