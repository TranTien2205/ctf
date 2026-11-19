# robots.txt and sitemap.xml — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /robots.txt 200 with Disallow entries | hidden paths listed | probe each Disallow |
| /sitemap.xml lists URLs not linked in UI | unlinked routes | probe each |
| Disallow: /admin or /backup | the author hid it for a reason | highest-value probes |

## Falsifier

Falsifier — robots.txt is empty/default and sitemap.xml is absent or only lists public pages: no hidden-path disclosure here.
