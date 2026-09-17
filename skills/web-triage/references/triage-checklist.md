# Web Triage Checklist

## Step 1: Passive Recon
```
[ ] View page source for comments, hidden fields, JS file references
[ ] Check robots.txt and sitemap.xml
[ ] Check /.git/, /.env, /config.php.bak, /backup.zip common leftover files
[ ] Review all JS files for API endpoints, hardcoded keys, internal paths
[ ] Check HTTP response headers (server, framework, security headers)
[ ] Check for security.txt or well-known disclosure policy
```

## Step 2: Crawl and Map
```
[ ] Every navigation link visited at least once
[ ] Every form identified (login, register, contact, search, upload)
[ ] Every API endpoint referenced in JS or network tab captured
[ ] Authenticated vs unauthenticated areas mapped separately
[ ] Multi-role testing planned if multiple account types exist (user/admin)
```

## Step 3: Input Point Inventory
```
[ ] All GET parameters listed per endpoint
[ ] All POST body fields listed per endpoint (form + JSON)
[ ] All custom/non-standard headers observed
[ ] All cookies listed with apparent purpose (session, preference, tracking)
[ ] File upload fields and accepted types noted
```

## Step 4: Quick Non-Destructive Probes
```
[ ] Single quote (') in each parameter → watch for SQL errors
[ ] Angle bracket (<>) reflection test → watch for unescaped output
[ ] {{7*7}} and ${7*7} → watch for template evaluation
[ ] ../../../etc/passwd in file-related parameters → path traversal signal
[ ] Large/malformed input → error message verbosity (stack traces = good signal)
[ ] HTTP method tampering (GET vs POST vs PUT) on discovered endpoints
```

## Step 5: Auth & Session Quick Check
```
[ ] Session token format identified (JWT, opaque, custom)
[ ] Cookie flags checked (HttpOnly, Secure, SameSite)
[ ] Password reset flow reviewed for token predictability/leakage
[ ] Registration flow reviewed for privilege assignment (role field tampering)
[ ] Logout behavior verified (session actually invalidated server-side)
```

## Step 6: Prioritize
```
[ ] Rank findings by likely impact and effort
[ ] Note which skill each hypothesis routes to
[ ] Start with lowest-effort, highest-confidence hypothesis first
```

## Deliverable
```markdown
# Triage Summary: [target]
- Technology stack: [...]
- Input points: [count and list]
- Quick-win findings: [...]
- Top 3 hypotheses (ranked): 
  1. [hypothesis] → [skill to use]
  2. [hypothesis] → [skill to use]
  3. [hypothesis] → [skill to use]
```
