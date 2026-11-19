# Parser differentials — the filter's parse vs the browser's parse

## The core model

```text
the server-side filter parses the URL with ITS parser (urllib/parse_url/
URI/regex) and reads a host/scheme/relative-ness from THAT parse.
the browser resolves the SAME string with ITS parser (WHATWG URL) and
goes to a DIFFERENT host.
the bypass is the string where the two parsers disagree on the host.
```

The open-redirect bypass IS a parser differential — `web-parser-differential`'s
sibling, URL-specific.

## The `urllib.parse` vs the browser — the canonical disagreements

| The URL | `urllib.parse.urlparse` | The browser (WHATWG) |
|---|---|---|
| `https://target.com@evil.com` | `netloc=target.com@evil.com`, `hostname=evil.com` | host=`evil.com` |
| `https://evil.com\@target.com` | `path=evil.com\@target.com`? — `\@` is in path, `hostname=None`? — actually `urlparse('https://evil.com\\@target.com')` -> `netloc=evil.com\@target.com`? — the `\@` is not a separator to urllib | host=`target.com` (the `\` is a path-sep to browsers) |
| `https://evil.com#@target.com` | `netloc=evil.com`, `fragment=@target.com` | host=`evil.com` + fragment |
| `https://evil.com?@target.com` | `netloc=evil.com`, `query=@target.com` | host=`evil.com` + query |
| `https://evil.com%5c.target.com` | `netloc=evil.com%5c.target.com`, `hostname=evil.com%5c.target.com` | host=`evil.com.` (`%5c`=`.` after decode+backslash-norm) |
| `https:%2f%2fevil.com` | `path=%2f%2fevil.com`, `hostname=None` | host=`evil.com` (the `%2f` decodes to `//`) |
| `//evil.com` | `scheme=''`, `netloc=evil.com`, `hostname=evil.com` | host=`evil.com`, scheme-relative |
| `//evil.com\@target.com` | `netloc=evil.com\@target.com`? — the `\@` splits | host=`target.com` |
| `https:evil.com` | `path=evil.com`, `hostname=None` | host=target.com (relative to the current origin) |
| `https:/\evil.com` | `path=/\evil.com`? or host=`evil.com` | host=`evil.com` (`\`→`/`) |
| `\\evil.com` | `path=\\evil.com`, `hostname=None` | host=`evil.com` (UNC/`\\`→`//`) |
| `/\evil.com` | `path=/\evil.com` | host=`evil.com` (`\`→`/`) |
| `https://evil.com%23target.com` | `netloc=evil.com%23target.com`, `hostname=evil.com%23target.com` | host=`evil.com`, fragment=`target.com`? — the `#` after decode |
| `https://evil.com%3ftarget.com` | `netloc=evil.com%3ftarget.com` | host=`evil.com`, query=`target.com`? |
| `https://evil.com%40target.com` | `netloc=evil.com%40target.com`, `hostname=target.com`? — `%40`=`@` | host=`target.com` (the `@` after decode) |

## The WHATWG-specific behaviors — the browser-only gaps

| The URL | The browser | A naive parser |
|---|---|---|
| `https:target.com` | host=target.com (absolute scheme, no `//`) | a relative path |
| `https:/\evil.com` | host=`evil.com` | an invalid/relative |
| `\\evil.com` | host=`evil.com` | a relative path |
| `\/evil.com` | host=`evil.com` | a relative path |
| `https://evil.com\@target.com` | host=`target.com` (`\@` → `@`) | host=`evil.com`? |
| `https://evil.com%5c@target.com` | host=`target.com`? | host=`evil.com` |
| `https://target.com%5c.evil.com` | host=`target.com`? — the `\` is a sep | host=`target.com` |
| `https:target.com.evil.com` | host=`target.com.evil.com` | a relative path |

## The framework-parser shapes

| Framework | The check | The bypass |
|---|---|---|
| Django `url_has_allowed_host_and_scheme` | `urlparse` host + `allowed_hosts` | `//evil.com` passes if `allowed_hosts` unchecked; `https://evil.com\@target.com` |
| Rails `redirect_to` | `URI.parse` host | `//evil.com` (host=evil.com) unless `allow_other_host: false` (Rails 7+) |
| Express `res.redirect(url)` | no built-in check | `//evil.com`/`https://evil.com` — the app must check |
| Flask `redirect(url)` | no built-in check | `//evil.com`/`https://evil.com` |
| ASP.NET `Redirect(url)`/`LocalRedirect` | `Url.IsLocalUrl` checks `~/`/`/` | `\\evil.com`/`/\/evil.com` — `IsLocalUrl` rejects `//` but `\/`? — the `\/` and `\` shapes |
| Laravel `redirect($url)` | no built-in check | `//evil.com`/`https://evil.com` |
| Spring `redirect:` | the `RedirectView` — `setHosts`/`setContextRelative` | a `redirect:` prefix vs a free `RedirectView` |
| Go `http.Redirect` | `url.Parse` host | `//evil.com` — `URL.Hostname()=evil.com`; a `strings.HasPrefix(u,"/")` check on `//evil.com` passes |
| PHP `header("Location: $url")` | no built-in check | `//evil.com`/`https://evil.com`/`parse_url` differentials |

## The regex/string-check differentials — no real parse

| The check | The bypass |
|---|---|
| `strpos($url, 'target.com') !== false` | `evil.com/target.com`/`evil.com?target.com` |
| `preg_match('/^\/[^\/]/', $url)` | `//evil.com` starts `//` — fails the `[^/]` — hmm, `//evil.com` = `/` + `/` — `^\/[^\/]` needs the 2nd char non-`/` — so `//evil.com` FAILS; `\/evil.com`? `\/` = `\` — `^\/` then `\` non-`/` — `\/evil.com` PASSES and resolves to `evil.com` |
| `preg_match('/^https?:\/\//', $url)` | `https:/\evil.com` — `https:/` + `\` — the `\/\`? — `https:/\evil.com` = `h`,`t`,...,`:`,`/`,`\` — `^https?:\/\/` needs `//` — `:/` then `\` — FAILS; but `https:\\evil.com`? the regex sees `https:` + `\\` — fails `\/` — hmm |
| `url.indexOf('target.com') !== -1` | `evil.com/target.com` |
| `url.startsWith('/')` | `//evil.com` |
| `!url.includes('://')` | `//evil.com`/`\\evil.com` — no `://` |
| `url.startsWith(baseUrl)` | `https://target.com.evil.com` |

## The decode-order differentials

```text
the server decodes THEN checks    -> send the encoded form; the decoded
                                   host is checked -> a decoded-evil.com
the server checks THEN decodes    -> send the encoded form; the RAW host
                                   is checked -> an encoded-bypass
the server checks the ENCODED     -> the check reads `%2f`/`%5c`/etc.
                                   literally -> an encoded-host bypass
```

## The differential-record

`differential: <the-filter-parse>: <the-browser-parse>: <the-bypass-url>`
— the two parsers' host-reads + the URL that exploits the disagreement.
