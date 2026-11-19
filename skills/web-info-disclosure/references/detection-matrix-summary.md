# Detection matrix — which channel is open — summary

One table: the probe, the positive answer, the file that owns it.

## Signal → route

- /.git/HEAD = 'ref:' → git-exposure
- /.env* = KEY=VALUE → env-config-leaks
- archive 200 + magic bytes → backup-archives
- sourceMappingURL or .map → source-maps
- actuator/__debug__/Werkzeug → debug-endpoints / framework-debug
- stack trace / verbose error → error-pages
- X-Powered-By / Server-Timing → header-disclosure
- Disallow entries → robots-sitemap
- Index of / → directory-listing
- swagger/openapi spec → api-docs-exposure
- keys in JS bundle → secrets-in-js
- server-status/phpinfo/metrics → status-pages
- access/error log served → log-exposure
- source file as text → source-disclosure
- .svn/.hg metadata → version-control-metadata
- comment hints → comment-leaks
- .DS_Store/.swp/Thumbs.db → static-leftovers
- metadata/internal surface → cloud-metadata

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.
