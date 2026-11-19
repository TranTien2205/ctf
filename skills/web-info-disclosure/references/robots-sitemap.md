# robots.txt and sitemap.xml

The two files meant for crawlers list the paths the author didn't want indexed — a free route map including admin, backup, and dev areas.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /robots.txt 200 with Disallow entries | hidden paths listed | probe each Disallow |
| /sitemap.xml lists URLs not linked in UI | unlinked routes | probe each |
| Disallow: /admin or /backup | the author hid it for a reason | highest-value probes |

## Steps

1. Fetch /robots.txt — collect every Disallow and Sitemap line.
2. Fetch /sitemap.xml (and sitemap_index.xml, sitemap-*.xml).
3. Probe each listed path — a Disallow is a promise that the path exists.
4. A Disallow'd path that 403s is still real — it may leak to a different verb or an internal hop.

## Falsifier

Falsifier — robots.txt is empty/default and sitemap.xml is absent or only lists public pages: no hidden-path disclosure here.

## Traps

- A path in robots.txt that 404s may be stale — or may only answer POST/other verbs.
- Sitemap can list thousands of URLs — filter for admin/backup/api/auth patterns, don't walk all.
- robots.txt entries are hints, not guarantees — verify each.

## Commands

```bash
curl -s '$BASE/robots.txt'; curl -s '$BASE/sitemap.xml'
```

## Cross-references

`exposed-artifacts.md` · `debug-endpoints.md`
