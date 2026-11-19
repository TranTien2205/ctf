# Common mistakes — the ways the open-redirect test goes wrong

## Mistake 1 — claiming the redirect without the Location

```text
"the param is a redirect" — but you never read the Location header.
the param exists + a 302 returns ≠ the redirect carries the canary.
the evidence is the verbatim Location: value — nothing else confirms.
```

## Mistake 2 — following the redirect instead of reading it

```bash
curl -sL "$BASE/login?next=https://evil.com"     # WRONG — -L follows it
curl -si "$BASE/login?next=https://evil.com" | grep -i location  # RIGHT
```

`-L` follows the redirect — you never see the `Location:` header. The
oracle is the VERBATIM header; use `--max-redirs 0` or read `-i` headers
with follow=False.

## Mistake 3 — treating `Location: /` as open

```text
Location: /dashboard   <- a safe relative — the filter FORCED it.
                         that's a strong-negative, not a candidate.
```

## Mistake 4 — treating a reflected param as a redirect

```text
<a href="/x?next=https://evil.com">  <- the param reflected in a LINK;
                                        the server didn't redirect —
                                        the victim has to click; that's
                                        a reflected-XSS/phishing surface,
                                        not a server-side open-redirect
```

## Mistake 5 — only trying `next`

```text
the param vocabulary is ~100 names; only trying `next` misses url/redir/
redirect_uri/return/returnTo/goto/callback/RelayState/post_logout_redirect_uri/
back/Referer/stored/etc.
```

## Mistake 6 — only trying `https://evil.com`

```text
the filter likely checks the simple form; the bypasses are //host,
%5c, userinfo, subdomain, encoded-char, double-encode, unicode, scheme
— the arms the filter-shape names
```

## Mistake 7 — a client-side redirect read as server-side

```text
a meta-refresh/location.href is the CLIENT-side twin; the server didn't
emit a Location — the carrier + the sink's source are the evidence; a
JS-blocked javascript: is a client-side block, not a server confirm
```

## Mistake 8 — the allowlist-gap read as a full open-redirect

```text
Location: https://target.com.evil.com  <- the SUFFIX gap — the host is
                                          target.com.evil.com (attacker-
                                          controlled IF you own evil.com's
                                          subdomain) — a subdomain-
                                          allowlist gap; it IS a bypass
                                          but reads "the string contains
                                          target.com" — record the parsed
                                          host precisely
```

## Mistake 9 — not checking the chain

```text
a confirmed open-redirect with no laundered trust is a phishing link —
the CTF value is the chain (OAuth/SSRF/XSS/bot); a standalone open-
redirect is often the intended answer, but check the downstream first
```

## Mistake 10 — a guessed param's null response read as a class verdict

```text
?next=... -> 200 render   <- 'next' isn't the param; the verdict is a
                             weak-negative (wrong param), not "no open-
                             redirect" — sweep the vocabulary first
```

## Mistake 11 — the Referer-header test conflated with a param

```text
/back with Referer: evil.com is a Referer-derived surface, not a param —
a different mechanism; record it separately
```

## Mistake 12 — the stored-redirect missed by single-endpoint sweep

```text
the param is set on /set-next and fired on /login — a single-endpoint
sweep on /login shows no open-redirect; the two-step is missed
```

## Mistake 13 — the double-decode skipped

```text
the server decodes twice; a single-encoded arm passes the check but the
double-encoded arm reaches the browser decoded — try the %25 arms
```

## Mistake 14 — the `javascript:` blocked read as a confirm

```text
a javascript: scheme reaching a sink is browser-split — Chrome blocks
location.href='javascript:...' in some contexts; the verbatim evidence
is the sink-value; the exploitability is browser-dependent — record both
```

## Mistake 15 — reporting "open redirect found" without the verbatim bytes

```text
the confirm needs the Location: verbatim in --response; "it redirected
to my URL" without the header bytes is a claim, not evidence
```
