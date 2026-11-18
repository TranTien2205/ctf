# Second-Order — the delayed-read shapes

## The second-order model — the read happens later

The input is stored, the READ happens on a different request/time/
context — the second-order shapes.

## Shape 1 — the stored-path read

```
POST /upload → saves /uploads/x
GET /view?file=x → reads /uploads/x
```

The path is written by upload-1, read by view-2 — a stored-read —
`web-file-upload`+`file-read-primitives`.

## Shape 2 — the template-name stored

```
POST /templates → save name=x.php
GET /render?tpl=x.php → include x.php
```

The template-name is stored, the include happens on render — the
stored-include.

## Shape 3 — the avatar-path stored

```
POST /profile → avatar=../../etc/passwd
GET /profile/avatar → reads avatar-path → the stored-path-read
```

The avatar-path is stored, the read happens on view — the stored-
avatar-read.

## Shape 4 — the email-template path

```
POST /settings → email_template=/etc/passwd
GET /send-test-email → include /etc/passwd
```

The email-template path is stored, the include happens on send —
the stored-template-include.

## Shape 5 — the PDF-template path

```
POST /pdf-template → path=/etc/passwd
GET /export → reads /etc/passwd → renders → the stored-pdf-template
```

The PDF-template is stored, the read happens on export — the stored-
template-read.

## Shape 6 — the log-file-path stored

```
POST /config → log_path=/etc/passwd
GET /logs → reads log_path → the stored-log-read
```

The log-path is stored, the read happens on log-view — the stored-
log-read.

## Shape 7 — the locale-file stored

```
POST /settings → locale=../../etc/passwd
GET /page → include ../../etc/passwd → the stored-locale-include
```

The locale is stored, the include happens on render — the stored-
locale-include.

## Shape 8 — the theme-path stored

```
POST /settings → theme=../../etc/passwd
GET /page → include theme/../../etc/passwd → the stored-theme-include
```

The theme-path is stored, the include happens on render — the stored-
theme-include.

## Shape 9 — the `include`-inside-include — the second-order include

```
?file=tpl.php → tpl.php includes ../../etc/passwd
```

The tpl.php's own include resolves a stored-path — the nested-include.

## Shape 10 — the serialized-path — the deser-chain read

```
POST /save → serialized-path=/etc/passwd
GET /load → unserialize → read /etc/passwd
```

The path is serialized-stored, the read happens on deserialize — the
deser-chain-read — `web-deserialization`.

## Shape 11 — the cron-path — the deferred-read

```
POST /cron → file=/etc/passwd
cron runs → reads /etc/passwd → output to /var/log/cron.log
GET /logs → reads cron.log → the deferred-read
```

The cron-path is stored, the read happens on cron-execution — the
deferred-read.

## Shape 12 — the webhook-path — the event-read

```
POST /webhook → callback=/etc/passwd
event fires → reads callback → the event-read
```

The webhook-path is stored, the read happens on event — the event-read.

## Shape 13 — the import-path — the import-read

```
POST /import → path=/etc/passwd
GET /import-status → reads /etc/passwd → the import-read
```

The import-path is stored, the read happens on import-process — the
import-read.

## Shape 14 — the restore-path — the restore-read

```
POST /backup → creates backup.zip
POST /restore → path=/etc/passwd → the restore writes it back
GET /view?file=/restored/etc/passwd → reads → the restore-read
```

The restore-path is stored, the read happens on restore — the restore-
read.

## Shape 15 — the theme-upload+include — the upload+render chain

```
POST /theme → uploads theme.php
GET /render?theme=uploaded-theme.php → include → the upload-include
```

The theme-file is uploaded, the include happens on render — the
upload+include chain.

## Shape 16 — the profile-pic→include — the upload+view chain

```
POST /avatar → uploads x.jpg (with PHP code inside)
GET /view?avatar=x.jpg → include → exec
```

The avatar is uploaded, the include happens on view — the upload+view
chain.

## Shape 17 — the download-list→read — the deferred-read

```
POST /queue → url=file:///etc/passwd
worker fetches → /etc/passwd → the deferred-fetch
```

The fetch-URL is queued, the read happens on the worker — the deferred-
fetch-read.

## Shape 18 — the scheduled-report — the deferred-report-read

```
POST /report → template=/etc/passwd
cron generates → the deferred-template-read
```

The report-template is stored, the read happens on schedule — the
deferred-template-read.

## Shape 19 — the template-render-async — the async-render-read

```
POST /render → tpl=/etc/passwd → returns job-id
GET /status/<job-id> → reads the rendered-file → the async-render
```

The render-template is queued, the read happens on status — the
async-render-read.

## Shape 20 — the `include` inside `eval` — the nested-exec-read

```
include $f where f is itself an eval'd expression
```

The nested-exec-read — a file-read inside an eval-context — the
exec-read chain.

## The "the read is deferred" — the timing-map

Second-order = the read happens on a different request — the probe
doesn't see it — the `read_loop`-style sweep needs the second request
to observe — the deferred-read is the timing-map.
