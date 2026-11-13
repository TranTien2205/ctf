# Information disclosure

**When:** verbose errors, debug routes, backup files, `.git`, comments,
directory listings, stack traces, version banners, API keys in JS.

`probe_disclosure(base)` requests the usual leak paths (`.git/HEAD`, `.env`, source maps, debug endpoints) in one pass. A placeholder is not a credential: `password=changeme` does not grade.

## High-yield checks (few requests, read the content)

- `robots.txt` + `sitemap.xml` (fingerprint already pulls these)
- `.git/HEAD`, `.git/config` -> `refs`, remotes; git object recovery is a
  known chain - record the HEAD file contents as proof of exposure
- `.env`, `.env.bak`, `config.php~`, `web.config`, `.DS_Store`
- `/server-status`, `/actuator`, `/actuator/env`, `/actuator/heapdump`
  (Spring), `/debug`, `/_debug`, `/elmah.axd`, `/trace`, `/metrics`,
  `/phpinfo.php`, `/console` (Werkzeug), `/.well-known/`
- Directory listing: trailing-slash dirs with `Index of`
- Backup of a found page: `page.php.bak`, `page.php~`, `page.php.swp`,
  `page.old`, `index.html.bak`

## Verbose-error oracle

Force errors deliberately: bad types, huge values, `'` in paths, missing
required params, wrong methods. Read WHAT leaks: stack trace, framework,
file paths, query fragments, internal IPs - each is a recon gift and, when
sensitive enough (paths+versions+code), a low-medium finding itself.

## Front-end leaks (js_recon candidates)

API keys in JS: verify what they unlock (a publishable Stripe `pk_` is NOT
a finding; a `sk_`/AWS key is critical). Source maps: `*.js.map` -> full
original source - medium when it exposes endpoints+logic.

## Response-header hygiene

`Server`, `X-Powered-By`, `X-AspNet-Version`, `X-Generator` exact-version
banners: info finding at most - mention in report, do not inflate.

## Falsifier

Endpoints 404 uniformly with a generic page; no artifacts recoverable;
errors are clean.

## Severity guide

Credentials/keys/private data recovered: high-critical. `.git`/source or
heap dump: high. Stack traces with paths+versions: low-medium. Version
banner: info.
