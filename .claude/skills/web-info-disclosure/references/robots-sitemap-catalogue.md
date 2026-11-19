# robots.txt and sitemap.xml — case catalogue

The two files meant for crawlers list the paths the author didn't want indexed — a free route map including admin, backup, and dev areas.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /robots.txt 200 with Disallow entries | hidden paths listed | probe each Disallow |
| 2 | /sitemap.xml lists URLs not linked in UI | unlinked routes | probe each |
| 3 | Disallow: /admin or /backup | the author hid it for a reason | highest-value probes |

## Falsifier

Falsifier — robots.txt is empty/default and sitemap.xml is absent or only lists public pages: no hidden-path disclosure here.

## Coverage notes

- A path in robots.txt that 404s may be stale — or may only answer POST/other verbs.
- Sitemap can list thousands of URLs — filter for admin/backup/api/auth patterns, don't walk all.
- robots.txt entries are hints, not guarantees — verify each.

## Cross-references

`exposed-artifacts.md` · `debug-endpoints.md`
