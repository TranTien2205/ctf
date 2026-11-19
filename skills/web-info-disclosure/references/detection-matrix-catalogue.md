# Detection matrix — which channel is open — case catalogue

One table: the probe, the positive answer, the file that owns it.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.git/HEAD = 'ref:' | git exposed | git-exposure |
| 2 | /.env* = KEY=VALUE | config leak | env-config-leaks |
| 3 | archive 200 + magic bytes | backup exposed | backup-archives |
| 4 | sourceMappingURL or .map | source maps | source-maps |
| 5 | actuator/__debug__/Werkzeug | debug surface | debug-endpoints / framework-debug |
| 6 | stack trace / verbose error | error disclosure | error-pages |
| 7 | X-Powered-By / Server-Timing | header leak | header-disclosure |
| 8 | Disallow entries | hidden paths | robots-sitemap |
| 9 | Index of / | autoindex | directory-listing |
| 10 | swagger/openapi spec | API map | api-docs-exposure |
| 11 | keys in JS bundle | secrets-in-js | secrets-in-js |
| 12 | server-status/phpinfo/metrics | ops surface | status-pages |
| 13 | access/error log served | log exposure | log-exposure |
| 14 | source file as text | source disclosure | source-disclosure |
| 15 | .svn/.hg metadata | VCS metadata | version-control-metadata |
| 16 | comment hints | comment leak | comment-leaks |
| 17 | .DS_Store/.swp/Thumbs.db | OS leftovers | static-leftovers |
| 18 | metadata/internal surface | cloud boundary | cloud-metadata |

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.

## Coverage notes

- Status is not the discriminator — content is.
- Each channel has its own falsifier; a closed channel doesn't close the class.

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
