# Common Flag Formats

## Standard Formats by Platform
```
CTF{...}                    Generic/custom CTF
FLAG{...}                    Generic
HTB{...}                     HackTheBox
picoCTF{...}                 picoCTF
CSAW{...}                    CSAW CTF
DUCTF{...}                   DownUnderCTF
flag{...}                    Lowercase variant (common)
```

## Format Characteristics
```
- Usually wrapped in curly braces: PREFIX{content}
- Content often includes: alphanumeric, underscores, hyphens
- Sometimes MD5/SHA1 hash format instead: PREFIX{32_hex_chars}
- May be base64 or hex encoded even within the braces
```

## Searching for Flags in Files/Output
```bash
# Generic flag pattern search
grep -rEoi "[a-z0-9_]+\{[^}]+\}" . 2>/dev/null

# Specific known prefix
grep -rEoi "flag\{[^}]+\}" .
grep -rEoi "ctf\{[^}]+\}" .

# In binary files (strings first)
strings binary | grep -Ei "flag\{|ctf\{"

# Search extracted/mounted filesystems
grep -r "flag{" /mnt/extracted/ 2>/dev/null
find / -iname "flag*" -o -iname "*.flag" 2>/dev/null
```

## Common Flag Locations
```
/root/flag.txt, /home/user/flag.txt      Linux challenges
C:\Users\*\Desktop\flag.txt                Windows challenges
Environment variables (env, printenv)        Process/container challenges
Database entries (look in obvious tables)    Web challenges
HTTP response headers or cookies              Web challenges
File metadata (EXIF, comments)                 Forensics/stego challenges
Memory dumps (strings on .dmp file)             Forensics challenges
```

## Encoded Flag Recognition
```bash
# If flag doesn't match expected pattern directly, check for encoding
echo "POSSIBLE_FLAG" | base64 -d
echo "706f737369626c65" | xxd -r -p    # hex decode
echo "cgsn{...}" # rot13 - decode and check
```

## Flag Validation Checklist
```
1. Confirm exact prefix format expected by the specific CTF (check rules/scoreboard)
2. Check for case sensitivity (flag{} vs FLAG{})
3. If flag looks like a hash (32/40/64 hex chars in braces), verify against submission format
4. If multiple potential flags found, submit the one most contextually relevant to challenge
5. Watch for decoy/fake flags planted in challenges - verify via the actual vulnerability chain
```

## Submitting via Automation (if platform has API)
```bash
curl -X POST https://ctf-platform.com/api/submit \
    -H "Authorization: Bearer TOKEN" \
    -d '{"challenge_id": 123, "flag": "flag{recovered_value}"}'
```
