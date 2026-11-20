# The trust boundary decides

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Every web claim hangs on WHICH boundary a value crosses: client->app (injection), app->datastore (SQLi/NoSQLi), app->template (SSTI), app->OS (cmd), app->internal-fetch (SSRF), app->browser-context (XSS), app->parser-vs-parser (smuggling/differential). Name the boundary first.

## Pivot

Module read -> the shared file or class skill it names.
