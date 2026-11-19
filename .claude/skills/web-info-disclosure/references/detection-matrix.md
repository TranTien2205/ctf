# Detection matrix — which channel is open

One table: the probe, the positive answer, the file that owns it.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.git/HEAD = 'ref:' | git exposed | git-exposure |
| /.env* = KEY=VALUE | config leak | env-config-leaks |
| archive 200 + magic bytes | backup exposed | backup-archives |
| sourceMappingURL or .map | source maps | source-maps |
| actuator/__debug__/Werkzeug | debug surface | debug-endpoints / framework-debug |
| stack trace / verbose error | error disclosure | error-pages |
| X-Powered-By / Server-Timing | header leak | header-disclosure |
| Disallow entries | hidden paths | robots-sitemap |
| Index of / | autoindex | directory-listing |
| swagger/openapi spec | API map | api-docs-exposure |
| keys in JS bundle | secrets-in-js | secrets-in-js |
| server-status/phpinfo/metrics | ops surface | status-pages |
| access/error log served | log exposure | log-exposure |
| source file as text | source disclosure | source-disclosure |
| .svn/.hg metadata | VCS metadata | version-control-metadata |
| comment hints | comment leak | comment-leaks |
| .DS_Store/.swp/Thumbs.db | OS leftovers | static-leftovers |
| metadata/internal surface | cloud boundary | cloud-metadata |

## Steps

1. Baseline the catch-all before ANY of these reads.
2. Run the bounded list once; read every response body.
3. Route each hit to its owning file.

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.

## Traps

- Status is not the discriminator — content is.
- Each channel has its own falsifier; a closed channel doesn't close the class.

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
