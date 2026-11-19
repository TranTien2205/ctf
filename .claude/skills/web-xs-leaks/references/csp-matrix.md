# CSP matrix — the Content-Security-Policy gates per channel

Each CSP directive, which channel it blocks, and which survives.

---

## 1. script-src — the JS gate

```text
'script-src none'     → NO attacker JS → the sealed shape is forced
'script-src self'     → same-origin scripts only — your cross-origin
                        page's JS still runs on YOUR origin (the
                        classic shape)
'script-src unsafe-inline' → inline scripts allowed — your JS runs
```

## 2. style-src — the CSS gate

```text
'style-src unsafe-inline' → inline styles allowed → the CSS oracle
                            works — a custom property + a bg-image
'style-src self'          → same-origin stylesheets only — a stored
                            stylesheet on the target works
'style-src none'          → no styles → the CSS channel is dead
```

## 3. font-src — the font gate

```text
'font-src self *'      → a host wildcard on fonts → the external
                         font host is the exfil → the @font-face
                         unicode-range channel works
'font-src self'        → same-origin fonts only — an external font
                         is blocked → the @font-face exfil is dead
'font-src none'        → no fonts → the font channel is dead
```

## 4. img-src — the image gate

```text
'img-src self'         → same-origin images only → a bg-image exfil
                         (a custom property → a url()) is blocked
'img-src *'            → any image → a bg-image exfil works
'img-src data:'        → a data: image → a null-origin carrier
```

## 5. default-src — the fallback

```text
'default-src unsafe-inline' → a broad hole — check each directive
                              for what it does NOT block — a style/
                              font hole is the channel
'default-src none'          → a strict base — check each explicit
                              directive for its hole
```

## 6. connect-src — the fetch/XHR gate

```text
'connect-src *'       → any fetch — a fetch-based exfil works
'connect-src self'    → same-origin fetches only — a write-back
                        to the target works; an external exfil fails
```

## 7. The per-directive channel-survival matrix

```text
directive             blocks                    survives
script-src none       all JS                    CSS/server-state
style-src unsafe-inline nothing                  the CSS oracle
style-src self        external stylesheets      a stored stylesheet
style-src none        all styles                a server-state channel
font-src self *       nothing                   the @font-face exfil
font-src self         external fonts            a bg-image exfil (if img-src *)
font-src none         all fonts                 a CSS-selector oracle (bg-image)
img-src self          external bg-images        a font-face exfil
img-src *             nothing                   a bg-image exfil
connect-src *         nothing                   a fetch exfil
connect-src self      external fetches          a write-back
```

## 8. The channel-per-CSP selection

```text
'script-src none' + 'style-src unsafe-inline' + 'font-src self *'
  → the @font-face unicode-range channel (the HTB Stylish shape)
'script-src none' + 'style-src self'
  → a stored stylesheet's CSS oracle (a same-origin carrier)
'script-src none' + 'img-src *'
  → a bg-image CSS-selector oracle
'script-src unsafe-inline' + a /report
  → the classic shape (your JS runs)
```

## 9. The CSP-check — which directives block which channel

```bash
# the CSP — each directive's hole
curl -sI "$BASE/" | grep -i 'content-security-policy'
#   or grep the source
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src|default-src|connect-src' <src> | head -20
```

## 10. The sealed-shape CSP signature — the forced case

```text
'script-src none' + no style-src/font-src hole → the declarative
channel is dead → a server-state channel (a counter/recency/token)
is the only oracle → a server-state-only sealed shape.
```

## 11. The 'unsafe-inline' misread — the style-survival

```text
assuming 'script-src none' blocks EVERYTHING — 'unsafe-inline' in
default-src/style-src still allows STYLES — the CSS oracle works.
read the CSP as a list of what's NOT allowed — a style/font hole
is the channel.
```

## 12. The font-src wildcard — the exfil that survives

```text
'img-src self' blocks a bg-image exfil; 'font-src self *' allows an
external font — the @font-face unicode-range channel works. check
WHICH directive has the hole — the font-src wildcard is the exfil.
```

## 13. The CSP-nonce — the inline-script gate

```text
'script-src nonce-XXX' — only scripts with the matching nonce run —
your injected inline script without the nonce doesn't run — a
nonce-blocking CSP forces a declarative/server-state channel.
```
