# Origin values corpus — the complete bypass battery, categorized

Every `Origin` value to send and what it tests — the full battery
with expected results per check-shape.

---

## A. The reflect-test origins — does the server echo

```bash
'https://evil.com'
'https://attacker.example'
'https://anything.else'
'null'
'https://'+$RANDOM+'.com'          # a random origin — pure reflect
```

`ACAO:<sent>` → a reflect — THE vuln.

## B. The null-origin battery — opaque contexts

```bash
'null'                             # the opaque origin — data:, sandbox, file
```

`ACAO:null` → a sandboxed/data:/file: page reads credentialed.

## C. The lookalike-domain battery — the check-shape probes

```bash
# prefix — startswith('https://target.com')
'https://target.com.evil.com'      # the allowed prefix + a foreign suffix
'https://target.com.evil.co.uk'
'https://target.com.attacker.com'

# suffix — endswith('target.com')
'https://eviltarget.com'           # a foreign prefix + the allowed suffix
'https://attacker-target.com'
'https://x.target.com'             # a subdomain — also matches suffix

# substring — 'target.com' in origin
'https://evil-target.com'
'https://target.com.evil.com'
'https://evil.com/target.com'
'https://target.com'               # the literal — always passes substring
```

## D. The subdomain-trust battery — `*.target.com`

```bash
'https://sub.target.com'           # a normal subdomain
'https://anything.target.com'      # any subdomain
'https://x.y.target.com'           # a nested subdomain
'https://target.com'               # the apex — may or may not pass
```

## E. The URL-parse-confusion battery — `@`, `?`, `#`, dots

```bash
'https://target.com@evil.com'      # host=evil.com, 'target.com' is userinfo
'https://evil.com@target.com'      # host=target.com — a same-host variant
'https://evil.com?target.com'      # query carries the string
'https://evil.com#target.com'      # fragment carries it
'https://target.com%2eevil.com'    # %2e — an encoded dot
'https://target.com%252eevil.com'  # double-encoded dot
'https://target%60com.evil.com'    # backtick — %60
'https://target.com%60.evil.com'   # backtick subdomain-split
'https://target.com%5f.evil.com'   # underscore — %5f
'https://target.com.'              # a trailing dot
'https://target.com..'             # double trailing dot
```

## F. The scheme/port/case battery

```bash
'http://target.com'                # scheme-change — a scheme-agnostic check
'https://target.com:443'           # explicit port
'https://target.com:444'           # a different port
'HTTP://TARGET.COM'                # uppercase — a case-insensitive check
'https://TARGET.com'               # partial uppercase
'https://tArGeT.cOm'               # mixed case
```

## G. The special-char battery — regex/parser edge cases

```bash
'https://target_com'               # underscore — a regex that needs a literal dot
'https://target-com'               # hyphen
'https://target`com'               # backtick — a regex `target.com` unescaped
'https://targetXcom'               # no separator — a regex `target.com` unescaped
'https://target;com'               # semicolon
'https://target|com'               # pipe
'https://target.com;evil.com'      # a semicolon subdomain
'https://target.com|evil.com'      # a pipe
'https://target.com%3bevil.com'    # encoded semicolon
```

## H. The edge-case battery

```bash
'https://target.com.evil.com.'     # trailing dot on the lookalike
'https://target.com.evil.com:443'  # port on the lookalike
'https://target.com.evil.com/'     # a trailing slash
'https://target.com.evil.com/x'    # a path — an unusual origin
'https:////target.com'             # multiple slashes
'https:/target.com'                # a single slash — a parse oddity
'target.com'                       # no scheme — a bare host
'file://'                          # a file origin
'file:///etc/passwd'               # a file path origin
'chrome-extension://abc'           # an extension origin
'about:blank'                      # about:
'data:text/html,'                  # a data: URL as an Origin value
```

## I. The per-check result table — what each battery row proves

```text
sent                                 passes-if              check-shape
https://evil.com                     reflect               reflect-all
null                                 null-allowed           null in list
https://target.com.evil.com          prefix/substring       startswith/in
https://eviltarget.com               suffix/substring       endswith/in
https://evil-target.com              substring             'target.com' in origin
https://sub.target.com               subdomain-trust       *.target.com
https://target.com@evil.com          naive 'in' or parse    url-parse bug
https://evil.com?target.com          naive 'in'             url-parse bug
https://target.com%2eevil.com        decode-order bug       encoded-dot
https://target`com                   loose regex            unescaped-dot regex
http://target.com                    scheme-agnostic        no scheme check
https://TARGET.com                   case-insensitive       no case-normalize
https://target.com.                  trailing-dot           no normalize
file://                              file-allowed           a loose check
data:text/html,                      data-allowed           a loose check
```

## J. The full battery script — one sweep

```bash
TARGET_DOMAIN=$(echo "$BASE" | sed -E 's#https?://([^/:]+).*#\1#')
ORIGINS=(
  'https://evil.com' 'null'
  "https://${TARGET_DOMAIN}.evil.com" "https://evil${TARGET_DOMAIN}"
  "https://evil-${TARGET_DOMAIN}" "https://sub.${TARGET_DOMAIN}"
  "https://${TARGET_DOMAIN}@evil.com" "https://evil.com?${TARGET_DOMAIN}"
  "https://evil.com#${TARGET_DOMAIN}"
  "https://${TARGET_DOMAIN}%2eevil.com" "https://${TARGET_DOMAIN}%60.evil.com"
  "https://${TARGET_DOMAIN}_.evil.com" "https://${TARGET_DOMAIN}-.evil.com"
  "http://${TARGET_DOMAIN}" "https://${TARGET_DOMAIN}:443"
  "https://${TARGET_DOMAIN}." "HTTP://${TARGET_DOMAIN}"
  'file://' 'data:text/html,'
)
for o in "${ORIGINS[@]}"; do
  echo -n "$o => "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin' || echo 'no ACAO'
done
```

## K. The battery-result decision — which check-shape, which exploit

```text
a reflect passes `https://evil.com`         → any attacker page reads
a null-allow passes `null`                   → a data:/sandboxed page reads
a prefix passes `target.com.evil.com`        → a lookalike-domain page reads
a suffix passes `eviltarget.com`             → a lookalike-domain page reads
a substring passes `evil-target.com`         → a lookalike-domain page reads
a subdomain-trust passes `sub.target.com`    → a controlled-sub page reads
a url-parse passes `target.com@evil.com`     → a real evil.com page reads
a strict allowlist passes only the listed    → closed — pivot
```
