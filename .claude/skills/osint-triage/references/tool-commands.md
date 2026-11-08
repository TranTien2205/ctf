# OSINT Tool Commands

## Subdomain Enumeration (Passive)

```bash
# Certificate transparency
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# SecurityTrails API
curl -s "https://api.securitytrails.com/v1/domain/target.com/subdomains" \
  -H "APIKEY: YOUR_KEY" | jq -r '.subdomains[]' | awk '{print $0".target.com"}'

# Subfinder (aggregates multiple sources)
subfinder -d target.com -silent -o subdomains.txt
```

## Technology Stack Fingerprinting

```bash
# Wappalyzer CLI
wappalyzer https://target.com

# WhatWeb
whatweb -a 3 https://target.com

# Check job postings for tech mentions
curl -s "https://www.linkedin.com/jobs/search/?keywords=target.com" | grep -iE "(AWS|Azure|Kubernetes|Docker)"
```

## Public Code Repository Search

```bash
# GitHub dorking for exposed secrets
# https://github.com/search?q=org:target-company+password
# https://github.com/search?q=org:target-company+api_key

# TruffleHog (scan for secrets in commit history)
trufflehog git https://github.com/target-company/repo --only-verified
```

See also:
- `email-pattern-detection.md` — theHarvester and email enumeration tools
- `leak-aggregator-sources.md` — HaveIBeenPwned, Dehashed, and credential search tools
- `cloud-asset-discovery.md` — AWS/Azure/GCP cloud asset enumeration tools
