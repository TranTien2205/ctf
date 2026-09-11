# Email Pattern Detection

Guide for identifying corporate email formats and generating employee email lists for password spraying and phishing simulations.

---

## Common Email Formats

| Format | Example | Likelihood |
|--------|---------|------------|
| `firstname.lastname@` | john.doe@target.com | 60% |
| `firstnamelastname@` | johndoe@target.com | 15% |
| `flastname@` | jdoe@target.com | 10% |
| `firstname@` | john@target.com | 5% (small companies) |
| `f.lastname@` | j.doe@target.com | 5% |
| `lastname.firstname@` | doe.john@target.com | 3% |
| `firstinitiallastname@` | jdoe@target.com | 2% |

---

## Detection Methods

### 1. Public Email Disclosure

**LinkedIn profiles**:
- Employees often list contact emails
- Sales/support staff usually have public emails

**Company website**:
```bash
# Scrape contact emails
curl -s https://target.com/about | grep -oE '[a-zA-Z0-9._%+-]+@target\.com' | sort -u
curl -s https://target.com/team | grep -oE '[a-zA-Z0-9._%+-]+@target\.com' | sort -u
```

**Press releases / blog posts**:
- Author bylines often include emails
- Check Wayback Machine for historical contacts

### 2. theHarvester

```bash
# Search multiple sources
theHarvester -d target.com -b google,bing,linkedin,twitter -l 500

# Example output:
# john.doe@target.com
# jane.smith@target.com
# Pattern detected: firstname.lastname@target.com
```

### 3. Hunter.io API

```bash
# Check email format
curl "https://api.hunter.io/v2/domain-search?domain=target.com&api_key=YOUR_KEY" | jq '.data.pattern'

# Example response:
# "{first}.{last}@target.com"
```

### 4. Email Verification Tools

Once you have a suspected format, verify with:

```bash
# Email-validator (checks MX records, syntax)
pip install email-validator
python3 -c "from email_validator import validate_email; validate_email('john.doe@target.com')"

# Holehe (checks if email registered on online services)
holehe john.doe@target.com

# If registered on Office365/Google Workspace, email likely valid
```

---

## Generating Employee Lists

### From LinkedIn

**Manual enumeration**:
1. Search: `site:linkedin.com/in "target company"`
2. Extract names from profiles
3. Apply detected email format

**Automated with theHarvester**:
```bash
theHarvester -d target.com -b linkedin -l 1000 > employees.txt
```

**CrossLinked tool** (specialized for LinkedIn scraping):
```bash
# Install
pip3 install crosslinked

# Run
python3 crosslinked.py -f '{first}.{last}@target.com' 'Target Company' -o emails.txt
```

### From Public Directories

**GitHub commits**:
```bash
# Clone company repos, extract commit authors
git clone https://github.com/target-company/repo
cd repo
git log --format='%ae' | sort -u | grep target.com
```

**WHOIS records**:
```bash
whois target.com | grep -iE '@target\.com'
```

**Leaked databases** (if in scope):
```bash
# Dehashed
dehashed search --email target.com | cut -d',' -f2 | sort -u
```

---

## Format Validation Workflow

```
1. Find 3-5 known valid emails
   ↓
2. Identify common pattern
   ↓
3. Generate candidate emails from employee names
   ↓
4. Verify with SMTP VRFY or Office365 enumeration
   ↓
5. Build final list of confirmed emails
```

### SMTP VRFY (if enabled)

```bash
# Test if SMTP server reveals valid emails
nc target.com 25
VRFY john.doe
# 250 = valid, 550 = invalid
```

**Note**: Most modern mail servers disable VRFY to prevent enumeration.

### Office365 User Enumeration

```bash
# o365creeper (checks if email exists in O365)
git clone https://github.com/LMGsec/o365creeper
python3 o365creeper.py -f emails.txt -o valid_emails.txt
```

**Method**: Attempts authentication, `AADSTS50034` error = invalid user, `AADSTS50126` = valid user but wrong password.

### Google Workspace Enumeration

```bash
# Check if email valid via password reset page
curl -s "https://accounts.google.com/signin/v2/identifier?email=john.doe@target.com" | grep -q "Couldn't find your Google Account" && echo "Invalid" || echo "Valid"
```

---

## Building Final Email List

### Deduplication & Validation

```bash
# Remove duplicates
sort -u raw_emails.txt > unique_emails.txt

# Validate MX records
while read email; do
  domain=$(echo $email | cut -d'@' -f2)
  dig MX $domain +short | grep -q '.' && echo $email >> valid_mx_emails.txt
done < unique_emails.txt

# Final list ready for password spraying
cat valid_mx_emails.txt
```

### Output Format

```
john.doe@target.com,John Doe,Sales Manager
jane.smith@target.com,Jane Smith,IT Director
bob.johnson@target.com,Bob Johnson,Developer
```

**Include name + title for context in password generation** (e.g., `Sales2024!`, `ITsupport123`).

---

## Password Generation from Emails

Once you have emails, generate targeted passwords:

```bash
# Common patterns
# CompanyName + Year + Special char
Target2024!
Target2023!

# Season + Year
Summer2024!
Winter2023!

# Employee name variations (for VIPs only, targeted attack)
John2024!
JDoe123!
```

See `../credential-hygiene/references/lockout-aware-spraying.md` for safe testing methodology.

---

## Legal & Ethical Notes

- **Email enumeration** = passive, generally safe
- **Email verification** = semi-active, may trigger logging
- **Password spraying** = active attack, requires written authorization
- **Phishing simulations** = requires explicit scope definition

Always confirm with client before testing credentials.

---

## Tools Summary

| Tool | Purpose | Installation |
|------|---------|--------------|
| theHarvester | Multi-source email scraping | `apt install theharvester` |
| CrossLinked | LinkedIn-specific enumeration | `pip3 install crosslinked` |
| Hunter.io | Email format detection (API) | Web-based |
| o365creeper | Office365 user validation | GitHub clone |
| Holehe | Check email on online services | `pip3 install holehe` |

---

## Cross-Reference

- Password spraying workflow: `../credential-hygiene/references/lockout-aware-spraying.md`
- Leak database search: `leak-aggregator-sources.md`
- OSINT workflow: `../SKILL.md`
