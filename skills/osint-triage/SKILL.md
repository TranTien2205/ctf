---
name: osint-triage
description: Lean OSINT router for public-source research, identity pivots, geolocation, and passive target profiling. Use before the deep ctf-osint reference.
---

# OSINT Triage

**Category**: Information Gathering
**Phase**: Pre-engagement reconnaissance
**Risk Level**: Low (passive, open-source intelligence)

---

## Purpose

Provides structured workflow for gathering publicly available information about a target organization before active enumeration begins. Helps identify attack surface, key personnel, technology stack, and potential entry points.

**Use this skill when**:
- Starting a new engagement or CTF box
- Need to understand target organization structure
- Looking for leaked credentials or exposed services
- Building initial wordlists for password spraying

---

## Workflow

### Phase 1: Target Organization Profiling

```
Domain/Company name provided
    ↓
├─ Corporate info (LinkedIn, Crunchbase)
├─ Email format detection
├─ Subdomain enumeration (passive)
└─ Public-facing infrastructure
    ↓
Generate employee list + email patterns
```

### Phase 2: Leaked Credential Search

```
Email list + domain
    ↓
├─ HaveIBeenPwned API
├─ Dehashed.com search
├─ Pastebin/leak aggregators
└─ Git commit history (if open-source project)
    ↓
Found credentials → test against VPN/Webmail/Office365
```

### Phase 3: Technology Stack Fingerprinting

```
Public websites/services
    ↓
├─ Wappalyzer / BuiltWith
├─ Job postings (mentions AWS, Azure, etc.)
├─ Public GitHub repos (Dockerfile, requirements.txt)
└─ SSL certificate transparency logs
    ↓
Generate targeted CVE list
```

### Phase 4: Attack Surface Discovery

```
Passive DNS + certificate transparency
    ↓
├─ Subdomain enumeration (crt.sh, SecurityTrails)
├─ IP range identification (BGP/WHOIS)
├─ S3 bucket naming patterns
└─ Cloud asset discovery (Azure blob, GCP buckets)
    ↓
Prioritize high-value targets
```

---

## Integration with Other Skills

- **external-recon**: Transition to active enumeration after OSINT complete
- **credential-hygiene**: Test found credentials safely (rate limiting)
- **web-triage**: Use tech stack info to guide vulnerability scanning
- **service-enumeration**: Prioritize services based on OSINT findings

---

## References

- `references/email-pattern-detection.md` - Generating employee email lists
- `references/leak-aggregator-sources.md` - Public breach databases
- `references/cloud-asset-discovery.md` - AWS/Azure/GCP enumeration
- `references/tool-commands.md` - Subfinder, WhatWeb, TruffleHog, and other tool commands
- `references/output-template.md` - OSINT report template
- `references/legal-considerations.md` - Legal & ethical boundaries
