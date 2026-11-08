# OSINT Output Template

Use this structured format to document OSINT findings.

```markdown
# OSINT Summary: target.com

## Organization Profile
- Industry: Technology/Finance/Healthcare
- Employee count: ~500 (LinkedIn)
- Locations: San Francisco, New York
- Email format: firstname.lastname@target.com

## Leaked Credentials
- 12 employees found in breaches (HaveIBeenPwned)
- 3 plaintext passwords found (Dehashed)
- Credentials file: leaked_creds.txt

## Technology Stack
- Web server: Nginx 1.21
- Framework: Django 3.2 (job posting mentioned)
- Cloud: AWS (CloudFront CDN detected)
- Auth: Okta SSO (login.target.com redirects)

## Attack Surface
### Subdomains (23 found)
- vpn.target.com (Fortinet SSL VPN)
- mail.target.com (Office365)
- jira.target.com (Atlassian Jira 8.20 - CVE-2022-0540)
- dev-api.target.com (unauthenticated Swagger docs)

### Cloud Assets
- s3://target-backups (publicly listable)
- target-prod.blob.core.windows.net (anonymous access)

## Priority Targets
1. dev-api.target.com - exposed API docs, may have debug endpoints
2. jira.target.com - known CVE, check for exploitation
3. s3://target-backups - download and analyze for credentials
4. VPN portal - test leaked credentials
```
