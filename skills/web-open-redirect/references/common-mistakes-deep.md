# Common mistakes (deep) — the full failure taxonomy

## Mistake — the evidence-shape mistakes

```text
1. claiming "the redirect is open" without the verbatim Location: —
   the gate asserts evidence is a substring of response
2. recording "it redirected to evil.com" — the WORDS not the bytes —
   the verbatim 'Location: https://evil.com' is the evidence
3. a Location: on a non-3xx read as a redirect — a 201-Location is a
   'created-at' hint not a nav — read the status
4. a Location: evil.com (no scheme/ //) read as cross-origin — it
   resolves RELATIVE to the origin — same-origin, not the gap
5. a meta/JS escaped value read as a confirm — the client-side twin is
   sanitized — the verbatim attribute is the evidence
```

## Mistake — the probe-shape mistakes

```text
6. curl -L — follows the redirect; the Location is never read
7. a guessed param's 200-render read as "no open-redirect" — a weak-
   negative, not a class verdict — sweep the vocabulary
8. only `?next=` tried — the vocabulary is ~100 names
9. only `https://evil.com` tried — the bypass arms are the corpus
10. the encoded-only sweep — the RAW //, /\, @ forms missed
11. the blind all-arms sweep — the fingerprint names which arm family
```

## Mistake — the filter-shape mistakes

```text
12. a `Location: /` on ONE arm read as "closed" — one arm's failure isn't
    the falsifier; EVERY arm -> safe is
13. the fingerprint misread — a host-force treated as a substring-check —
    the wrong arm family tried
14. the check's parse assumed — the filter's urlparse reads `\@`/`%5c`
    differently than assumed — measure it
15. a netloc-check treated as a hostname-check — the netloc includes the
    userinfo/port; the hostname doesn't
```

## Mistake — the carrier mistakes

```text
16. the Location-only check — the meta/JS/Referer/stored carriers missed
17. a meta-refresh read as a server-side Location — the client-side twin
18. a location.hash read as a redirect — a fragment-nav, not a full redirect
19. a stored-redirect missed — the set-then-fire is two requests
20. a Referer-derived missed — the header isn't a param
```

## Mistake — the chain mistakes

```text
21. a standalone open-redirect reported as "the flag" when the challenge
    is the laundered-trust shape — the class confirm is hop-0
22. the OAuth chain claimed without the allowlisted-domain open-redirect
    — the redirect_uri launder needs a redirect ON the allowlisted domain
23. the SSRF chain claimed without checking the fetcher follows Location
    — a non-following fetcher is a chain-dead
24. the javascript: "confirm" without the browser-split check — Chrome
    blocks location.href='javascript:...' in some contexts
25. the bot-visit claimed without the bot actually visiting — the bot's
    access log is the impact evidence
```

## Mistake — the falsifier mistakes

```text
26. the uniform-safe Location unrecorded — the arms-tried list is the
    falsifier's evidence
27. a falsifier on the swept surface read as the whole class — the
    falsifier closes THE SWEPT SURFACE; an unswept endpoint/carrier
    is the reopen
28. a weak-negative escalated to a falsifier — a wrong-param isn't a
    class-close; a real-param's safe Location is
```

## Mistake — the discipline mistakes

```text
29. multiple params/arms in one probe — an unattributable Location
30. the second arm before the first's fingerprint — the fingerprint names
    the arms; blind-ordering wastes budget
31. a record without the verbatim Location — the post-probe gate fails
32. the chain-impact claimed without the downstream evidence — the code-
    on-canary is the impact, not "the chain would work"
```
