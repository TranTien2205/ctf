---
name: web-triage
description: >
  Jeopardy web recognition router. Use at the START of any jeopardy web
  challenge (source usually given + one endpoint + one flag). Maps a
  source/response SIGNAL to the likely bug class and the fastest first probe,
  then routes to the specialized skill references/ for depth. PULL only.
tags: [web, jeopardy, triage, recognition, ctf]
environment: [ctf]
---

# Jeopardy Web — Recognition Router

Jeopardy web != pentest. You are usually given SOURCE. Task is not "enumerate"
— it is: read source, find the SINK, prove ONE bug, get ONE flag.
(Black-box recon lives in external-recon/; do not crawl here.)

## Step 0 — before any payload
1. Read the whole source. Find where user input reaches a dangerous sink.
2. Note the stack (framework, language, DB, parser, template engine).
3. Locate WHERE the flag is (env? DB row? file /flag? admin-only route?).
   The bug you need is the one that REACHES the flag, not the flashiest one.

## Signal -> Class -> First probe -> Depth
| Source / response signal | Class | First probe | Depth |
|---|---|---|---|
| string-concat SQL (WHERE x='$in'), SQL error, bool/time diff | SQLi | ' then ' OR 1=1-- - | web-sqli/references/, KB SQL Injection |
| Mongo find({..req..}), $ne/$gt accepted | NoSQLi | {"$ne":""} | KB NoSQL Injection |
| render_template_string, Template(in), input in template | SSTI | {{7*7}} / ${7*7} / #{7*7} | web-ssti/references/ (engine-detection first) |
| os.system/exec/subprocess(shell=True)/backticks | Command inj | ;id  |id  $(id) | KB Command Injection |
| pickle.loads/yaml.load/PHP unserialize/Java readObject; base64 blob in cookie | Deserialization | gadget / O: / !!python | web-deserialization/references/ |
| XML parser, lxml/libxml no resolve_entities=False, <?xml | XXE | <!ENTITY xxe SYSTEM "file:///flag"> | KB XXE |
| requests.get(url)/img/pdf fetch/webhook, admin-bot visits URL | SSRF | internal host / 169.254.169.254 / gopher | web-ssrf/references/, KB SSRF |
| include($_GET), file_get_contents($in) | LFI->RCE | php://filter/convert.base64-encode/resource= -> log poison / /proc/self/environ | KB (add if missing) |
| jwt.decode alg-from-token, weak secret, none allowed, kid | JWT | alg:none / crack secret / kid path-traversal | KB JWT Weak/Leaked Secret |
| PHP == on hashes, strcmp($in,$x), loose compare | Type juggling | 0e... magic hash / arr[]= | KB PHP Type Juggling |
| JS merge/deep-assign, __proto__ in JSON body | Prototype pollution | {"__proto__":{"isAdmin":true}} | KB (add if missing) |
| upload + weak ext/mime check | File upload | .phtml / magic-byte / .htaccess | web-file-upload/references/, KB File Upload Bypass |
| WHERE id=req.param no ownership check, sequential IDs | IDOR | +-1 the id / other user id | web-idor/references/, KB IDOR |
| check-then-act on balance/coupon/one-time | Race condition | fire N parallel requests | KB (add if missing) |
| registration/verify/reset logic, mass-assignment | Auth/logic bypass | extra field / skip step / dup email | web-auth-session/, KB Auth Bypass |
| input reflected in HTML, admin-bot fires it | XSS (bot) | steal cookie / CSP bypass / SSRF-chain | web-xss/references/, KB XSS |
| custom proxy/WAF/gateway trước backend (Rust/Go/nginx-lua), rule chặn path/header/method | Parser differential / desync | so khớp cách proxy vs backend parse cùng bytes | references/http-parser-differential.md |

Reference cards = the local CTF skill references and reviewed CTF cards when available.

## Pull payload variants
Khi trung class nhung can bien the (bypass WAF/filter cu the):
grep -ri "<keyword>" skills/ctf-web/
hoac: python solver/recognize.py --grep "<class> <dau hieu>"

## Discipline (theo ../LOOP_DISCIPLINE.md)
- Mot class -> thu probe re nhat truoc, doc ket qua, hoi "co tin hieu moi khong?"
- Khong co tin hieu moi sau vai lan -> SAI class, quay lai bang tren, doi gia thuyet.
- Flag phai reach duoc tu bug: neu bug khong cham flag, do khong phai bug cua bai.
