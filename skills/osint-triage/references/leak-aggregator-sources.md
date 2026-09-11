# Leak Aggregator Sources

Directory of public breach databases and leak aggregators for credential discovery during OSINT phase.

---

## Major Aggregators

### 1. HaveIBeenPwned (HIBP)

**URL**: https://haveibeenpwned.com  
**Access**: Free API (rate limited), paid API for bulk queries  
**Coverage**: 12+ billion accounts from 600+ breaches

**API Usage**:
```bash
# Check single email
curl "https://haveibeenpwned.com/api/v3/breachedaccount/user@target.com" \
  -H "hibp-api-key: YOUR_KEY"

# Check domain (requires paid key)
curl "https://haveibeenpwned.com/api/v3/breaches?domain=target.com" \
  -H "hibp-api-key: YOUR_KEY"
```

**Output**: List of breaches, no plaintext passwords (privacy-focused).

### 2. Dehashed

**URL**: https://dehashed.com  
**Access**: Paid subscription ($4-10/month)  
**Coverage**: 18+ billion records, includes plaintext passwords

**CLI Usage**:
```bash
# Install
pip3 install dehashed

# Search by email
dehashed search --email user@target.com

# Search by domain
dehashed search --domain target.com

# Search by username
dehashed search --username johndoe
```

**Output**: Email, username, password, hash, source breach.

### 3. LeakCheck

**URL**: https://leakcheck.io  
**Access**: Freemium (limited free searches), paid API  
**Coverage**: 15+ billion records

**API Usage**:
```bash
curl "https://leakcheck.io/api/public?check=user@target.com" \
  -H "X-API-Key: YOUR_KEY"
```

### 4. IntelligenceX

**URL**: https://intelx.io  
**Access**: Paid (includes darknet search)  
**Coverage**: Surface web, darknet forums, paste sites

**Use case**: Deep search including Telegram leaks, darknet markets.

---

## Manual Search Sources

### Paste Sites

**Pastebin**: https://pastebin.com
```bash
# Google dork for target.com leaks
site:pastebin.com "target.com" password
```

**Ghostbin**: https://ghostbin.co  
**Rentry.co**: https://rentry.co  
**Paste.ee**: https://paste.ee

**Automation**:
```bash
# psbdmp (monitors Pastebin for keywords)
python3 psbdmp.py -k "target.com"
```

### GitHub Search

**Public repo credential leaks**:
```bash
# GitHub dork
site:github.com "target.com" password
site:github.com "target.com" api_key
site:github.com org:target-company password

# Gitleaks (scan specific repo)
gitleaks detect --source https://github.com/target/repo

# TruffleHog
trufflehog git https://github.com/target/repo --only-verified
```

### Darknet Forums

**Breach forums**: breachforums.is, raidforums (seized), exploit.in  
**Access**: Tor browser required  
**Search**: Use forum search for company name or domain

**WARNING**: Accessing darknet forums may be illegal in some jurisdictions. Confirm legal standing before accessing.

---

## Credential File Formats

### Common Leak Formats

**Email:Password**:
```
john.doe@target.com:Password123!
jane.smith@target.com:Summer2023
```

**Email:Hash**:
```
john.doe@target.com:5f4dcc3b5aa765d61d8327deb882cf99
jane.smith@target.com:e99a18c428cb38d5f260853678922e03
```

**Username:Email:Password**:
```
jdoe:john.doe@target.com:Password123!
jsmith:jane.smith@target.com:Summer2023
```

### Processing Leak Files

```bash
# Extract only target.com emails
grep -i '@target\.com' leak_combo.txt > target_creds.txt

# Remove duplicates
sort -u target_creds.txt > target_unique.txt

# Split into email and password
awk -F':' '{print $1}' target_unique.txt > emails.txt
awk -F':' '{print $2}' target_unique.txt > passwords.txt

# Count unique passwords (for password policy analysis)
awk -F':' '{print $2}' target_unique.txt | sort | uniq -c | sort -rn | head -20
```

---

## Hash Cracking

If leaks contain only hashes:

### Identify Hash Type
```bash
# hashid
hashid -m '5f4dcc3b5aa765d61d8327deb882cf99'
# Output: MD5

# hash-identifier
hash-identifier
# Paste hash when prompted
```

### Crack with Hashcat
```bash
# MD5 example
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt

# NTLM
hashcat -m 1000 -a 0 ntlm_hashes.txt rockyou.txt

# bcrypt (slow)
hashcat -m 3200 -a 0 bcrypt_hashes.txt rockyou.txt
```

### Online Hash Lookup
- CrackStation: https://crackstation.net
- Hashes.com: https://hashes.com
- cmd5.org: https://www.cmd5.org

---

## Privacy & Legal Considerations

### Ethical Usage

✅ **Allowed**:
- Checking if client organization appears in breaches (with authorization)
- Alerting users to change compromised passwords
- Analyzing password patterns for security awareness training

❌ **Not Allowed**:
- Downloading full breach databases for unauthorized use
- Credential stuffing on third-party services
- Sharing leaked credentials publicly

### Data Handling

1. **Encrypt storage**: Store leaked credentials in encrypted containers
2. **Limit access**: Only authorized team members
3. **Secure deletion**: Wipe files after engagement completion
4. **No retention**: Do not keep leak data beyond project scope

```bash
# Encrypt leak files
gpg -c target_creds.txt
# Output: target_creds.txt.gpg

# Secure deletion after use
shred -vfz -n 10 target_creds.txt
```

---

## Integration with Password Spraying

Once credentials found:

```bash
# Test against Office365 (example)
# Use o365spray with found passwords
python3 o365spray.py --username emails.txt --password passwords.txt --rate 1 --lockout 5

# See: ../credential-hygiene/references/lockout-aware-spraying.md
```

**CRITICAL**: Always implement rate limiting and lockout awareness.

---

## Automated Leak Monitoring

### Setup Alerts for Future Leaks

**HaveIBeenPwned domain monitoring**:
- Subscribe to breach notifications for `@target.com` emails

**Google Alerts**:
```
"target.com" + (password OR leak OR breach OR dump)
```

**GitHub monitoring**:
```bash
# Use git-secrets to prevent future leaks
git clone https://github.com/awslabs/git-secrets
cd git-secrets
make install

# Add patterns to detect
git secrets --add 'target\.com.*password'
git secrets --add '[A-Za-z0-9]{32}' # API keys
```

---

## Tools Summary

| Tool | Purpose | Cost |
|------|---------|------|
| HaveIBeenPwned | Breach notification | Free API (rate limited) |
| Dehashed | Plaintext password search | $4-10/month |
| LeakCheck | Credential search | Freemium |
| IntelligenceX | Darknet + paste sites | Paid |
| TruffleHog | Git repo secret scanning | Free |
| Gitleaks | Git repo secret scanning | Free |
| psbdmp | Pastebin monitoring | Free |

---

## Cross-Reference

- Email enumeration: `email-pattern-detection.md`
- Password spraying: `../credential-hygiene/references/lockout-aware-spraying.md`
- Hash cracking: `../credential-hygiene/references/hash-cracking-modes.md`
- OSINT workflow: `../SKILL.md`
