# Signal to Skill Mapping (Extended)

## HTTP-Level Signals
```
Signal                                          → Route to
SQL error string in response                    → web-sqli/references/error-based.md
Response length/content differs on true/false    → web-sqli/references/boolean-blind.md
Response time varies with payload                → web-sqli/references/time-blind.md
Input reflected unescaped in HTML                 → web-xss
Input reflected in JS context                      → web-xss/references/dom-xss.md
Server makes outbound request based on input       → web-ssrf
Template expression evaluated (e.g. {{7*7}}=49)     → web-ssti
File upload accepts arbitrary extension/content      → web-file-upload
Sequential numeric IDs in URLs                        → web-idor/references/sequential-enumeration.md
UUIDs in URLs, some predictable                       → web-idor/references/uuid-analysis.md
Base64/serialized-looking cookie or param              → web-deserialization/references/detection.md
JWT token used for session                               → web-auth-session
Password reset token in URL/email                         → web-auth-session
```

## Response Header Signals
```
Signal                                → Implication
X-Powered-By: PHP                     → check php-deser.md, php extension bypass
Set-Cookie: JSESSIONID                → check java-deser.md
Server: nginx + no CSP                → check web-xss (weak output encoding likely)
Access-Control-Allow-Origin: *        → CORS misconfig, check web-ssrf/idor via API
```

## Behavioral Signals
```
Signal                                        → Route to
App fetches remote images/PDFs from URL param  → web-ssrf
App renders user-supplied "template" or "theme" → web-ssti
App has admin panel reachable without auth       → web-auth-session (access control)
App exposes internal IPs/hostnames in errors       → web-ssrf (internal boundary is now named)
App uses object storage URLs (presigned, etc.)      → web-idor (identifier in the URL)
```

## When Multiple Signals Overlap
Prioritize by:
1. Confidence (how certain is the signal, e.g. explicit SQL error > vague timing)
2. Impact (auth bypass / RCE > information disclosure)
3. Effort (quick payload test > building custom exploit chain)

Work the highest-confidence, highest-impact, lowest-effort hypothesis first,
then move down the list systematically. Document each test and result before
moving to the next signal.
