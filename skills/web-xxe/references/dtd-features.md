# DTD Features — the full grammar for reference

## The complete internal-subset grammar

```xml
<!DOCTYPE root [
  <!ELEMENT root (#PCDATA|a|b)*>
  <!ELEMENT a EMPTY>
  <!ATTLIST a x CDATA #IMPLIED>
  <!ENTITY x "value">
  <!ENTITY x SYSTEM "uri">
  <!ENTITY x PUBLIC "-//X//EN" "uri">
  <!ENTITY % p "value">
  <!ENTITY % p SYSTEM "uri">
  <!ENTITY % p PUBLIC "-//X//EN" "uri">
  <!ENTITY u SYSTEM "uri" NDATA notation>
  <!NOTATION n SYSTEM "uri">
  <!NOTATION n PUBLIC "-//X//EN">
  <!NOTATION n PUBLIC "-//X//EN" "uri">
  <?pi-target data?>
  <!-- comment -->
  %p;
]>
```

## ELEMENT declarations — the content-model

```xml
<!ELEMENT r EMPTY>                  — no content
<!ELEMENT r ANY>                    — anything
<!ELEMENT r (#PCDATA)>              — text only
<!ELEMENT r (a)>                    — one child a
<!ELEMENT r (a|b)>                  — a or b
<!ELEMENT r (a,b)>                  — a then b
<!ELEMENT r (a|b)*>                 — zero+ of a/b
<!ELEMENT r (a|b)+>                 — one+ of a/b
<!ELEMENT r (a|b)?>                 — optional a/b
<!ELEMENT r (#PCDATA|a|b)*>         — mixed text+children
```

## ATTLIST declarations — the attribute-model

```xml
<!ATTLIST r a CDATA #IMPLIED>       — text attr, optional
<!ATTLIST r a CDATA #REQUIRED>      — required
<!ATTLIST r a CDATA #FIXED "v">     — fixed value
<!ATTLIST r a CDATA "default">      — default value
<!ATTLIST r a ID #IMPLIED>          — unique id
<!ATTLIST r a IDREF #IMPLIED>       — ref to an ID
<!ATTLIST r a IDREFS #IMPLIED>
<!ATTLIST r a ENTITY #IMPLIED>      — unparsed entity name
<!ATTLIST r a ENTITIES #IMPLIED>    — space-sep entity names
<!ATTLIST r a NMTOKEN #IMPLIED>     — name-token
<!ATTLIST r a NMTOKENS #IMPLIED>
<!ATTLIST r a (v1|v2|v3) "v1">      — enumerated
<!ATTLIST r a NOTATION (n1|n2) #IMPLIED>
<!ATTLIST r xml:space (default|preserve) "preserve">
<!ATTLIST r xml:lang NMTOKEN "en">
```

The `#FIXED`/`"default"`/`CDATA "..."` forms inject a default value —
the entity-in-default trick.

## ENTITY declarations — the full forms

```xml
<!ENTITY x "v">                            — internal general
<!ENTITY x SYSTEM "uri">                   — external general
<!ENTITY x PUBLIC "-//X//EN" "uri">        — public-id general
<!ENTITY % p "v">                          — internal param
<!ENTITY % p SYSTEM "uri">                 — external param
<!ENTITY % p PUBLIC "-//X//EN" "uri">      — public-id param
<!ENTITY u SYSTEM "uri" NDATA n>           — unparsed
<!ENTITY u PUBLIC "-//X//EN" "uri" NDATA n>
```

## NOTATION declarations — the SYSTEM-fetch

```xml
<!NOTATION n SYSTEM "file:///etc/passwd">
<!NOTATION n PUBLIC "-//X//EN" "http://YOU/x">
<!NOTATION n PUBLIC "-//X//EN">
```

The system-id URI — a fetch in declaring parsers.

## Processing instructions

```xml
<?xml-stylesheet type="text/xsl" href="uri"?>
<?xml-stylesheet type="text/css" href="uri"?>
<?xml-model href="uri" type="application/xml"?>
<?xml-model href="uri" type="application/relax-ng-compact-syntax"?>
<?oxygen RNGSchema="uri"?>
<?cocoon ...?>
<?php ...?>              — inside a parsed doc — some PHP-XML handlers
<?xml-dtd ...?>
```

## Conditional sections — external-DTD only

```xml
<![INCLUDE[
  <!ENTITY x SYSTEM "file:///flag">
]]>
<![IGNORE[
  <!ENTITY y "dead">
]]>
<![%param;[
  ...
]]>
```

Inside the internal subset — a parse error. Inside an external DTD —
`%param;` evaluates to `INCLUDE`/`IGNORE` to toggle a block — the
conditional-DTD trick.

## Comments

```xml
<!-- comment -- can't contain "--" -->
```

`--` inside a comment is illegal — a comment containing `--` errors —
fingerprint.

## The character-reference forms

```xml
&#60;      — '<' decimal
&#x3C;     — '<' hex
&#38;      — '&'
&#37;      — '%'
&#34;      — '"'
&#39;      — '\''
```

Inside entity VALUES — the char-refs decode at value-expansion —
`&#37;` builds a `%` inside a value — the engine for nested-entity
construction.

## The "the DTD's own syntax is the fingerprint" — the strictness

- `<!ENTITY x "v">` requires the exact `ENTITY` keyword — `Entity`/
  `entity` won't parse — case-sensitive
- `<!DOCTYPE` must be uppercase
- `<!ENTITY`/`ELEMENT`/`ATTLIST`/`NOTATION`/`DOCTYPE` all uppercase
- whitespace between tokens is free — newlines/tabs legal
- `<!ELEMENT r (#PCDATA)>` — the `#` is part of the keyword

## The "the internal subset ends at `]>`" — the boundary

`<!DOCTYPE r [ ... ]>` — the `]`+`>` closes the subset — a `]` inside
a value doesn't close it unless followed by `>` — the boundary rule.

## The "the DTD can declare the root's name" — `DOCTYPE name`

`<!DOCTYPE r [...]>` — `r` must match the root element's name for
validating parsers — non-validating ignore the mismatch — a config
fingerprint.
