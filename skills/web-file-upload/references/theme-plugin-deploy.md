# Theme/Plugin/Extension Upload — the "install this package" primitive

## The shape — a feature that accepts code-packages

CMS/theme/plugin/extension upload: WordPress themes/plugins, Discourse
components, Grafana plugins, Jenkins `.hpi`, custom "module" installs —
the endpoint takes a zip/package and loads it as code.

```
POST /wp-admin/update.php?action=upload-plugin
POST /admin/themes/install
POST /plugins/install
```

The upload isn't a file that gets parsed — it's an artifact the platform
executes on install.

## WordPress plugin/theme — the canonical shape

`upload-plugin`/`upload-theme` — a zip containing php files + metadata:

```
x.php:
<?php
/*
Plugin Name: X
*/
// any code here runs when activated
```

Theme:

```
x-theme/style.css      — required metadata
x-theme/functions.php  — runs on theme load
x-theme/shell.php      — accessible as a page template
```

The plugin/theme's php runs on activation — the upload IS the exec, no
polyglot needed. Needs admin creds or an unauthenticated upload theme
endpoint.

## The "upload a theme/plugin" surface — which fields reach exec

- `functions.php`/`index.php` inside the theme zip → php exec on view
- `header.php`/`page-*.php` templates → rendered php
- plugin `main file` → runs at activation, privileged
- a `.css` with `<?php` inside the theme? — only if the theme renders it
  as php — generally not

## Jenkins `.hpi` / `.jpi` — the plugin-package shape

Groovy init scripts, jelly views — a crafted `.hpi` loads a class =
exec on install.

## Discourse/Grafana/etc — platform-specific manifests

- Discourse theme components — `.scss`/`.hbs` — XSS not RCE usually
- Grafana plugin — a signed plugin zip — signature check? unsigned
  plugins blocked unless `allow_loading_unsigned_plugins`
- module systems that exec the module's init — same idea

## The "plugin install" vs "file upload" distinction — which endpoint

| Endpoint type | File's role |
|---|---|
| `upload.php` storing in `/uploads/` | file lives as data — exec needs serve/include |
| `install.php`/`update.php` running an installer | file IS code — exec on activation |
| `import.php` parsing the file | parser is the sink — `second-order-processing.md` |

The install endpoint executes the artifact; the storage endpoint stores
it — different bugs.

## Metadata that does the exec — `functions.php` isn't the only path

- `composer.json` `scripts` — composer install-time hooks
- `package.json` `scripts` — npm hooks (`node-specific.md`)
- theme `functions.php` on load
- plugin init/`activate` hook — wordpress calls `register_activation_hook`
- `__construct`/`init`/`bootstrap` method the loader calls

The package's own metadata provides the exec hook — the uploader just
needs it to be loaded.

## Signing/validation — what blocks the malicious package

- signature/manifest checks → `signature-bypass`-style tricks (only if the
  manifest is validated loosely)
- theme-review checks (WP's `Theme_Check`) — usually advisory not blocking
- private extension allowlists — usually a path issue, not signature

## Falsifiers

- no install/deploy endpoint exists — only plain file storage
- installer requires signing/validation that rejects anything but a
  signed artifact

## Output to record

- the install endpoint + the artifact format it accepts + the exec hook
  inside the package that runs
