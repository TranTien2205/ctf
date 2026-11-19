# Framework matrix — each framework's redirect-check and its bypass

## Django

```python
# Django's check — url_has_allowed_host_and_scheme / is_safe_url (older)
from django.utils.http import url_has_allowed_host_and_scheme
if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
    return redirect(next_url)
# the check: the parsed host must be in allowed_hosts AND the scheme in {http,https}
```

| The check | The bypass |
|---|---|
| `url_has_allowed_host_and_scheme(url, allowed_hosts={host})` | `//target.com.evil.com`? NO — host is `target.com.evil.com`, not in `{target.com}` — UNLESS `allowed_hosts` includes `*.target.com` |
| `url_has_allowed_host_and_scheme` | `https://target.com@evil.com`? — `urlparse` host=`evil.com` — fails |
| `url_has_allowed_host_and_scheme` | `https://evil.com\@target.com` — `urlparse` reads the `\@` — Django 3.x normalized `\\`->`/`; older Django versions had the `\@` bypass (CVE) |
| `url_has_allowed_host_and_scheme` | `https:evil.com` — `urlparse` host=None, `is_safe_url` may treat as relative → redirect to `https:evil.com` which the browser resolves to target.com — a pass |
| no check — `redirect(next_url)` | any URL — `https://evil.com`/`//evil.com` |
| a substring `if 'target.com' in url` | `evil.com/target.com` |
| `allowed_hosts` with `*`/wildcards | a subdomain `x.target.com` |

## Rails

```ruby
redirect_to params[:next]  # <- Rails <7: any URL; Rails 7+: blocked unless allow_other_host
# Rails 7 raises UnsafeRedirectError on an external host unless:
redirect_to params[:next], allow_other_host: true  # <- explicitly allowed
```

| The check | The bypass |
|---|---|
| Rails 7+ default (no `allow_other_host`) | `UnsafeRedirectError` — the external redirect is blocked; only `//evil.com`/`https://evil.com` that pass `url_from`'s same-host check work — a `target.com.evil.com` fails unless `allow_other_host` |
| `redirect_to params[:next], allow_other_host: true` | any URL |
| `redirect_back(fallback_location:...)` | a Referer-derived — forge the Referer |
| `redirect_to url_from(params[:next])` | `url_from` checks same-origin; `//evil.com` fails |
| a substring check | `evil.com/target.com` |

## Express / Node

```javascript
res.redirect(req.query.next)  // <- no built-in check — any URL
// a manual check:
if (req.query.next.startsWith('/')) res.redirect(req.query.next)
```

| The check | The bypass |
|---|---|
| no check | `//evil.com`/`https://evil.com`/`javascript:...` — any |
| `next.startsWith('/')` | `//evil.com` — starts `/`, host=`evil.com` |
| `next.startsWith('/'); !next.startsWith('//')` | `\/evil.com`/`/\\evil.com` — `\/` passes `!//`, the browser resolves `\`→`/`, host=`evil.com` |
| `new URL(next, base)` + `url.hostname === 'target.com'` | `https://evil.com\@target.com` — `URL.hostname` reads `target.com`? or `evil.com`? — the `\@` in WHATWG URL |
| a regex | the parse-differentials |
| `url.parse(next).host === 'target.com'` | the legacy `url.parse` — `evil.com\@target.com` etc. |

## Flask / Python

```python
return redirect(request.args.get('next'))  # <- no built-in check
# a check:
from urllib.parse import urlparse
if urlparse(next).netloc == 'target.com': return redirect(next)
```

| The check | The bypass |
|---|---|
| no check | any URL |
| `urlparse(next).netloc == 'target.com'` | `https://target.com@evil.com`? — `netloc`=`target.com@evil.com` ≠ `target.com` — FAILS; `https://evil.com\@target.com`? — `netloc`=`evil.com\@target.com` — FAILS |
| `urlparse(next).netloc == 'target.com'` | `target.com:443@evil.com`? — `netloc`=`target.com:443@evil.com` — FAILS; the `hostname` vs `netloc` — `urlparse(...).hostname` strips userinfo — a `netloc` check on `target.com@evil.com` fails, a `hostname` check on `target.com.evil.com` fails |
| `urlparse(next).hostname == 'target.com'` | `target.com.evil.com`? `hostname`=`target.com.evil.com` — FAILS; `target.com.@evil.com`? hostname=`target.com.` — hmm |
| `next.startswith('/')` | `//evil.com` — starts `/` |
| `next.startswith('/') and not next.startswith('//')` | `/\evil.com`/`/\/evil.com` — `\/`/`/\` passes, browser resolves |
| `urlparse(next).netloc in allowed` | a `netloc`-vs-`hostname` gap |

## ASP.NET

```csharp
return Redirect(next);        // <- any URL
if (Url.IsLocalUrl(next)) return Redirect(next);  // <- the check
```

| The check | The bypass |
|---|---|
| `Url.IsLocalUrl(url)` — requires `/`, `~/`, or a local path | `\\evil.com`? — `IsLocalUrl` rejects `\\`... — historically `/\evil.com`, `//evil.com` — `IsLocalUrl` rejects `//` but `\/evil.com`? — the `\/` and `\` shapes have been bypasses |
| `Url.IsLocalUrl` | `/\evil.com`/`\\/evil.com`/`\\evil.com` — the backslash shapes |
| `Url.IsLocalUrl` | `//evil.com` — fails `IsLocalUrl`; but a `Redirect` without the check passes it |
| `LocalRedirect` vs `Redirect` | `LocalRedirect` throws on a non-local; `Redirect` doesn't check |
| a `Uri.IsWellFormedUriString` check | `https://target.com@evil.com` etc. |

## Laravel / PHP

```php
return redirect($request->input('next'));  // <- any URL
return redirect()->to($next);
return redirect()->away($next);   // <- away() skips the local check
```

| The check | The bypass |
|---|---|
| no check / `redirect()->away()` | any URL |
| a `Str::startsWith($url, '/')` | `//evil.com` |
| `parse_url($url, PHP_URL_HOST) === 'target.com'` | `https://target.com@evil.com`? `parse_url` host=`evil.com` — fails; `https://evil.com\@target.com`? `parse_url` — the `\@` |
| `filter_var($url, FILTER_VALIDATE_URL)` | validates SYNTAX not host — `https://evil.com` is a valid URL |
| `in_array(parse_url($url,PHP_URL_HOST), $allowed)` | the substring/`@`/`\` parser differentials |
| a regex `preg_match('/^https?:\/\/target\.com/', $url)` | `https://target.com.evil.com`/`https://target.com@evil.com` |

## Spring / Java

```java
return "redirect:" + next;               // <- the redirect: prefix — any URL
return new RedirectView(next);           // <- any URL
new RedirectView(next).setHosts("target.com");  // <- the host check
```

| The check | The bypass |
|---|---|
| `redirect:` prefix — no check | any URL |
| `RedirectView.setHosts([target.com])` | `https://target.com@evil.com`? — `URI.getHost`=`evil.com` — fails; the `\@`/parser differentials |
| `URI.create(next).getHost().equals("target.com")` | the Java `URI` parse — `evil.com\@target.com` |
| a `String.startsWith("/")` | `//evil.com` |

## Go

```go
http.Redirect(w, r, next, http.StatusFound)  // <- any URL
u, _ := url.Parse(next); if u.Hostname() == "target.com" { http.Redirect(...) }
```

| The check | The bypass |
|---|---|
| no check | any URL |
| `u.Hostname() == "target.com"` | `https://target.com@evil.com`? `Hostname`=`evil.com` — fails; `evil.com\@target.com`? |
| `strings.HasPrefix(u, "/")` | `//evil.com` — HasPrefix `/` true, host=`evil.com` |
| `strings.HasPrefix(u, "/") && !strings.HasPrefix(u, "//")` | `/\evil.com`/`\/evil.com` |

## The matrix-record

`framework: <fw>: <the-check-api>: <the-bypass-shapes>` — each framework's
canonical check + the bypass shapes that defeat it; the parser-differential
is the recurring mechanism.
