# Penetration Test Report - 20261109-010802-127.0.0.1

- **Target:** `127.0.0.1` (20261109-010802-127.0.0.1)
- **Date:** 2026-11-09 01:08:02
- **Duration:** 0.4s
- **Agent model:** scripted-demo
- **Requests sent:** 56

## Executive summary

Demo run: SQLi + XSS + IDOR + info disclosure + forged-JWT admin takeover verified with verbatim evidence; host-header reflection left as a lead for manual follow-up.

| Severity | Count |
|---|---|
| Critical | 1 |
| High | 2 |
| Medium | 2 |

| OWASP Top 10 (2021) | Findings |
|---|---|
| A01 Broken Access Control | F03, F04 |
| A02 Cryptographic Failures | F05 |
| A03 Injection | F01, F02 |

## Engagement constraints

- **Scope hosts:** (target only)
- **Excluded paths:** none
- **Budgets:** 16 turns, 400 requests, 0 rps
- **Proxy:** no · **TLS verify:** no
- **Tool surface:** all


## Findings

### F05 - JWT weak secret: forged admin token accepted

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** jwt
- **CWE:** `CWE-347`
- **OWASP:** A02 Cryptographic Failures
- **Endpoint:** `http://127.0.0.1:42394/api/me`
- **Evidence:** r15

**Description**  
The lab JWT verifies against the dictionary secret 'secret123'; a forged admin token is accepted and its claims echoed back verbatim.

**Proof (verbatim excerpt)**  
```
"role": "admin"
```

**Remediation**  
Rotate to a high-entropy secret; prefer asymmetric signing.

<details><summary>Transcript r15: GET http://127.0.0.1:42394/api/user/1 -> 200</summary>

```http
GET http://127.0.0.1:42394/api/user/1
host: 127.0.0.1:42394
accept: */*
accept-encoding: gzip, deflate
connection: keep-alive
user-agent: •••redacted•••

HTTP/200
server: LabVuln/1.0 Python/3.12.0
date: Sun, 08 Nov 2026 18:08:03 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 75

{"id": 1, "username": "admin", "role": "admin", "email": "admin@lab.local"}
```
</details>

### F01 - SQL injection in /item id parameter

- **Severity:** High
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** sqli
- **CWE:** `CWE-89`
- **OWASP:** A03 Injection
- **Endpoint:** `http://127.0.0.1:42394/item?id=1`
- **Evidence:** r2

**Description**  
The quote probe produces a raw sqlite error - unsanitized input reaches the query.

**Proof (verbatim excerpt)**  
```
sqlite3.OperationalError
```

**Remediation**  
Use parameterized queries.

<details><summary>Transcript r2: GET http://127.0.0.1:42394/item?id=1%27 -> 500</summary>

```http
GET http://127.0.0.1:42394/item?id=1%27
host: 127.0.0.1:42394
accept: */*
accept-encoding: gzip, deflate
connection: keep-alive
user-agent: •••redacted•••

HTTP/500
server: LabVuln/1.0 Python/3.12.0
date: Sun, 08 Nov 2026 18:08:03 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 102

<html><body>sqlite3.OperationalError: unrecognized token: "'1''" near "1'": syntax error</body></html>
```
</details>

### F03 - IDOR: /api/user/<id> serves any user object

- **Severity:** High
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Category:** idor
- **CWE:** `CWE-639`
- **OWASP:** A01 Broken Access Control
- **Endpoint:** `http://127.0.0.1:42394/api/user/2`
- **Evidence:** r13

**Description**  
Neighboring ids return other users' objects with no authorization check.

**Proof (verbatim excerpt)**  
```
"username"
```

**Remediation**  
Enforce per-object ownership checks.

<details><summary>Transcript r13: GET http://127.0.0.1:42394/api/user/2 -> 200</summary>

```http
GET http://127.0.0.1:42394/api/user/2
host: 127.0.0.1:42394
accept: */*
accept-encoding: gzip, deflate
connection: keep-alive
user-agent: •••redacted•••

HTTP/200
server: LabVuln/1.0 Python/3.12.0
date: Sun, 08 Nov 2026 18:08:03 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 74

{"id": 2, "username": "alice", "role": "user", "email": "alice@lab.local"}
```
</details>

### F02 - Reflected XSS in /search q parameter

- **Severity:** Medium
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`
- **Category:** xss
- **CWE:** `CWE-79`
- **OWASP:** A03 Injection
- **Endpoint:** `http://127.0.0.1:42394/search?q=x`
- **Evidence:** r12

**Description**  
Canary chars < > " ' reflect unescaped in html context.

**Proof (verbatim excerpt)**  
```
<>'"&=/
```

**Remediation**  
Output-encode by context; add CSP.

<details><summary>Transcript r12: GET http://127.0.0.1:42394/search?q=x3am04xe2%3C%3E%27%22%26%3D%2F -> 200</summary>

```http
GET http://127.0.0.1:42394/search?q=x3am04xe2%3C%3E%27%22%26%3D%2F
host: 127.0.0.1:42394
accept: */*
accept-encoding: gzip, deflate
connection: keep-alive
user-agent: •••redacted•••

HTTP/200
server: LabVuln/1.0 Python/3.12.0
date: Sun, 08 Nov 2026 18:08:03 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 55

<html><body>Results for: x3am04xe2<>'"&=/</body></html>
```
</details>

### F04 - Exposed /.env and /.git/HEAD at web root

- **Severity:** Medium
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Category:** info-disclosure
- **CWE:** `CWE-200`
- **OWASP:** A01 Broken Access Control
- **Endpoint:** `http://127.0.0.1:42394/.env`
- **Evidence:** r20

**Description**  
Sensitive paths are served publicly - credentials and source-control metadata leak to anyone.

**Proof (verbatim excerpt)**  
```
SECRET_KEY=lab-secret-0123
```

**Remediation**  
Deny dotfile/VCS paths at the web server; rotate exposed secrets.

<details><summary>Transcript r20: GET http://127.0.0.1:42394/.env -> 200</summary>

```http
GET http://127.0.0.1:42394/.env
host: 127.0.0.1:42394
accept: */*
accept-encoding: gzip, deflate
connection: keep-alive
user-agent: •••redacted•••

HTTP/200
server: LabVuln/1.0 Python/3.12.0
date: Sun, 08 Nov 2026 18:08:03 GMT
content-type: text/plain
x-powered-by: LabVuln/1.0
content-length: 67

DB_HOST=db.internal
DB_PASSWORD=hunter2
SECRET_KEY=lab-secret-0123

```
</details>


## Test coverage

| Tool | Requests |
|---|---|
| http_request | 1 |
| probe_disclosure | 38 |
| probe_idor | 4 |
| probe_reflection | 1 |
| probe_sqli | 11 |
| probe_xfh | 1 |

**Probe families run:** probe_disclosure, probe_idor, probe_reflection, probe_sqli, probe_xfh

**Endpoints exercised (46):**

- `GET /.DS_Store`
- `GET /.aws/credentials`
- `GET /.env`
- `GET /.git/HEAD`
- `GET /.git/config`
- `GET /.gitignore`
- `GET /.npmrc`
- `GET /.svn/entries`
- `GET /WEB-INF/web.xml`
- `GET /actuator/env`
- `GET /actuator/heapdump`
- `GET /actuator/info`
- `GET /actuator/mappings`
- `GET /adminer.php`
- `GET /api-docs`
- `GET /api/me`
- `GET /api/user/0`
- `GET /api/user/1`
- `GET /api/user/2`
- `GET /api/user/3`
- `GET /arg404mutaivk2`
- `GET /backup.zip`
- `GET /composer.json`
- `GET /console`
- `GET /debug`
- `GET /debug/pprof/`
- `GET /debug/vars`
- `GET /docker-compose.yml`
- `GET /elmah.axd`
- `GET /health`
- `GET /item?id`
- `GET /manager/html`
- `GET /metrics`
- `GET /nginx_status`
- `GET /package.json`
- `GET /phpinfo.php`
- `GET /phpmyadmin/`
- `GET /reset`
- `GET /search?q`
- `GET /server-info`
- `GET /server-status`
- `GET /swagger.json`
- `GET /trace`
- `GET /v2/api-docs`
- `GET /web.config`
- `GET /wp-config.php~`

## Methodology

Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input
mapping -> hypothesis-driven probes (matched true/false pairs,
baseline-diffed) -> verification -> evidence-gated findings.
The complete request/response transcript is in `transcript.jsonl`
(56 entries). Working notes are in `notes.md`.

_All findings cite verbatim response excerpts verified against the
recorded transcript at write time._

<details><summary>Appendix: agent working notes (audit)</summary>

```
# Working notes - http://127.0.0.1:42394

## Agent summary (agent)

Demo run: SQLi + XSS + IDOR + info disclosure + forged-JWT admin takeover verified with verbatim evidence; host-header reflection left as a lead for manual follow-up.


```
</details>