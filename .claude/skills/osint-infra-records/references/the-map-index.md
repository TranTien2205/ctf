# Infra-records reference map

- Route: the-workflow, the-txt, the-san, the-axfr, the-whois,
  the-crtsh, the-map-index
- Records: per-type modules (txt/spf/dkim/dmarc/mx/ns/soa/caa/
  srv/ptr/a/aaaa/cname/any/axfr)
- Sources: per-source modules (dig/host/nslookup/dns_query/crtsh/
  whois/passive/archive/cert/shodan)
- Discipline: the-wildcard, the-ttl, the-tool, the-fallback,
  the-falsifier, the-evidence, the-boundary, the-traps,
  the-checklist, the-detection

## The generated matrix

- record-question files: each record type × each question shape.
- src-source files: each source × each question shape.
- t-* files: query syntax, authoritative queries, record chains,
  reverse DNS, cert reading, issuer, crtsh detail, AXFR detail,
  DNSSEC/NSEC, wildcard detection, diffing, sibling confirmation,
  the operator, record priority.
Each carries deep/checklist/map/index/recap/ref/route companions.

## Reading order

- New: the-workflow → the-txt → the-san → the-map-index.
- A specific record type → its per-type module.
- A specific question → the matching record-question module.
- A source → the matching src-* module.

## The quick reference

- Where is the flag? → the-txt, the-worked-txt
- What hosts exist? → the-san, the-axfr, the-crtsh
- Who runs it? → the-whois, the-ns-detail, the-soa-detail

- t-* techniques: query syntax, authoritative, chains, cert, crtsh, axfr, nsec, wildcard, diff, sibling-conf, operator, priority.

## The bottom line

TXT, SANs, whois, AXFR — the four coverage steps; the matrices map the rest of the space.
