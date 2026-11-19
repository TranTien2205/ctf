# Edge cases — every host-header edge case, exhaustively

The edge map — an edge, a probe, a result.

---

## 1. An empty Host — a valid negative

```bash
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host — a 400 is a valid negative
```

## 2. A whitespace Host — a valid negative

```bash
curl -s -D - -H 'Host:  ' "$BASE/"   # a whitespace host — a 400 is a valid negative
```

## 3. A tab Host — a valid negative

```bash
curl -s -D - -H 'Host: \t' "$BASE/"   # a tab host — a 400 is a valid negative
```

## 4. A newline Host — a valid negative

```bash
curl -s -D - -H 'Host: \n' "$BASE/"   # a newline host — a 400 is a valid negative
```

## 5. A carriage-return Host — a valid negative

```bash
curl -s -D - -H 'Host: \r' "$BASE/"   # a carriage-return host — a 400 is a valid negative
```

## 6. A null-byte Host — a valid negative

```bash
curl -s -D - -H 'Host: \0' "$BASE/"   # a null-byte host — a 400 is a valid negative
```

## 7. A Unicode Host — a valid negative

```bash
curl -s -D - -H 'Host: évil.example' "$BASE/"   # a Unicode host — a 400 is a valid negative
curl -s -D - -H 'Host: evi\u006c.example' "$BASE/"   # a Unicode host — a 400 is a valid negative
curl -s -D - -H 'Host: evi%6c.example' "$BASE/"   # a Unicode host — a 400 is a valid negative
```

## 8. A punycode Host — a valid negative

```bash
curl -s -D - -H 'Host: xn--vil-1na.example' "$BASE/"   # a punycode host — a 400 is a valid negative
curl -s -D - -H 'Host: xn--vil-1na' "$BASE/"   # a punycode host — a 400 is a valid negative
```

## 9. An IDN Host — a valid negative

```bash
curl -s -D - -H 'Host: évil.example' "$BASE/"   # an IDN host — a 400 is a valid negative
curl -s -D - -H 'Host: evi\u006c.example' "$BASE/"   # an IDN host — a 400 is a valid negative
curl -s -D - -H 'Host: evi%6c.example' "$BASE/"   # an IDN host — a 400 is a valid negative
```

## 10. A long Host — a valid negative

```bash
curl -s -D - -H 'Host: $(python3 -c "print('a'*1000)")' "$BASE/"   # a long host — a 400 is a valid negative
curl -s -D - -H 'Host: $(python3 -c "print('a'*10000)")' "$BASE/"   # a long host — a 400 is a valid negative
curl -s -D - -H 'Host: $(python3 -c "print('a'*100000)")' "$BASE/"   # a long host — a 400 is a valid negative
```

## 11. A null-byte Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example\0' "$BASE/"   # a null-byte host — a 400 is a valid negative
curl -s -D - -H 'Host: \0evil.example' "$BASE/"   # a null-byte host — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example\0target.com' "$BASE/"   # a null-byte host — a 400 is a valid negative
```

## 12. A port Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example:443' "$BASE/"   # a forged port — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example:8080' "$BASE/"   # a forged port — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example:0' "$BASE/"   # a forged port — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example:65535' "$BASE/"   # a forged port — a 400 is a valid negative
```

## 13. An IPv4 Host — a valid negative

```bash
curl -s -D - -H 'Host: 127.0.0.1' "$BASE/"   # an IPv4 host — a 400 is a valid negative
curl -s -D - -H 'Host: 0.0.0.0' "$BASE/"   # an IPv4 host — a 400 is a valid negative
curl -s -D - -H 'Host: 255.255.255.255' "$BASE/"   # an IPv4 host — a 400 is a valid negative
curl -s -D - -H 'Host: 10.0.0.1' "$BASE/"   # an IPv4 host — a 400 is a valid negative
curl -s -D - -H 'Host: 192.168.1.1' "$BASE/"   # an IPv4 host — a 400 is a valid negative
curl -s -D - -H 'Host: 172.16.0.1' "$BASE/"   # an IPv4 host — a 400 is a valid negative
```

## 14. An IPv6 Host — a valid negative

```bash
curl -s -D - -H 'Host: [::1]' "$BASE/"   # an IPv6 host — a 400 is a valid negative
curl -s -D - -H 'Host: [::ffff:127.0.0.1]' "$BASE/"   # an IPv6 host — a 400 is a valid negative
curl -s -D - -H 'Host: [2001:db8::1]' "$BASE/"   # an IPv6 host — a 400 is a valid negative
curl -s -D - -H 'Host: [fe80::1]' "$BASE/"   # an IPv6 host — a 400 is a valid negative
```

## 15. A double-dot Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example..internal' "$BASE/"   # a double-dot — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example..evil.example' "$BASE/"   # a double-dot — a 400 is a valid negative
curl -s -D - -H 'Host: ..target.com' "$BASE/"   # a double-dot — a 400 is a valid negative
```

## 16. A trailing-dot Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot — a 400 is a valid negative
curl -s -D - -H 'Host: target.com.' "$BASE/"   # a trailing dot — a 400 is a valid negative
curl -s -D - -H 'Host: internal.' "$BASE/"   # a trailing dot — a 400 is a valid negative
curl -s -D - -H 'Host: localhost.' "$BASE/"   # a trailing dot — a 400 is a valid negative
```

## 17. An @-separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example@internal' "$BASE/"   # an @-separator — a 400 is a valid negative
curl -s -D - -H 'Host: internal@evil.example' "$BASE/"   # an @-separator — a 400 is a valid negative
```

## 18. A #-separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example#internal' "$BASE/"   # a #-separator — a 400 is a valid negative
curl -s -D - -H 'Host: internal#evil.example' "$BASE/"   # a #-separator — a 400 is a valid negative
```

## 19. A ?-separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example?internal' "$BASE/"   # a ?-separator — a 400 is a valid negative
curl -s -D - -H 'Host: internal?evil.example' "$BASE/"   # a ?-separator — a 400 is a valid negative
```

## 20. A path-separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example/target.com' "$BASE/"   # a path separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com/evil.example' "$BASE/"   # a path separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example/internal' "$BASE/"   # a path separator — a 400 is a valid negative
curl -s -D - -H 'Host: internal/evil.example' "$BASE/"   # a path separator — a 400 is a valid negative
```

## 21. A backslash-separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example\\target.com' "$BASE/"   # a backslash separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com\\evil.example' "$BASE/"   # a backslash separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example\\internal' "$BASE/"   # a backslash separator — a 400 is a valid negative
curl -s -D - -H 'Host: internal\\evil.example' "$BASE/"   # a backslash separator — a 400 is a valid negative
```

## 22. A percent-encoded separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example%2etarget.com' "$BASE/"   # an encoded separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com%2eevil.example' "$BASE/"   # an encoded separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example%252etarget.com' "$BASE/"   # a doubly-encoded separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com%252eevil.example' "$BASE/"   # a doubly-encoded separator — a 400 is a valid negative
```

## 23. A multi-dot Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example...target.com' "$BASE/"   # a triple-dot — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example....target.com' "$BASE/"   # a quadruple-dot — a 400 is a valid negative
```

## 24. A colon-separator Host — a valid negative

```bash
curl -s -D - -H 'Host: evil.example:target.com' "$BASE/"   # a colon separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com:evil.example' "$BASE/"   # a colon separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example:internal' "$BASE/"   # a colon separator — a 400 is a valid negative
curl -s -D - -H 'Host: internal:evil.example' "$BASE/"   # a colon separator — a 400 is a valid negative
```
