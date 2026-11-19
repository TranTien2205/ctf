# robots.txt and sitemap.xml — operational checklist

The two files meant for crawlers list the paths the author didn't want indexed — a free route map including admin, backup, and dev areas.

## Checklist

- [ ] Fetch /robots.txt — collect every Disallow and Sitemap line.
- [ ] Fetch /sitemap.xml (and sitemap_index.xml, sitemap-*.xml).
- [ ] Probe each listed path — a Disallow is a promise that the path exists.
- [ ] A Disallow'd path that 403s is still real — it may leak to a different verb or an internal hop.

## Abort conditions

- A path in robots.txt that 404s may be stale — or may only answer POST/other verbs.
- Sitemap can list thousands of URLs — filter for admin/backup/api/auth patterns, don't walk all.
- robots.txt entries are hints, not guarantees — verify each.

## Falsifier

Falsifier — robots.txt is empty/default and sitemap.xml is absent or only lists public pages: no hidden-path disclosure here.

## Cross-references

`exposed-artifacts.md` · `debug-endpoints.md`
