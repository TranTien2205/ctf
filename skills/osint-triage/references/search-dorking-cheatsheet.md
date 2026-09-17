# Search Dorking Cheatsheet

## Google/Bing Search Operators
```
site:domain.com                    Restrict to a specific site
-site:domain.com                    Exclude a specific site
filetype:pdf                        Restrict to a file type (pdf, xls, doc, sql, log)
intitle:"keyword"                   Keyword in page title
inurl:"keyword"                      Keyword in URL
intext:"exact phrase"                 Exact phrase in page body
"exact phrase"                        Exact phrase match anywhere
site:domain.com filetype:pdf          Combine operators
cache:domain.com                      View cached version (deprecated on Google,
                                       use Wayback Machine instead)
related:domain.com                     Find related sites
```

## People/Identity Dorking
```
"Full Name" "City"
"Full Name" site:linkedin.com
"Full Name" ("email" OR "contact")
"Full Name" resume filetype:pdf
"username" -site:knownplatform.com     Find the username elsewhere
```

## Organization/Infrastructure Dorking
```
site:target.com filetype:xls OR filetype:xlsx    Exposed spreadsheets
site:target.com filetype:sql                       Exposed database dumps
site:target.com inurl:admin                          Admin panels
site:target.com intitle:"index of"                    Open directory listings
site:pastebin.com "target.com"                         Leaked data mentions
site:github.com "target.com" password                    Leaked credentials in repos
```

## Social Media Specific
```
# LinkedIn
site:linkedin.com/in "Company Name"

# Twitter/X (via search engine since native search is limited historically)
site:twitter.com "keyword" "username"

# GitHub
site:github.com "email@domain.com"
site:github.com "target-domain.com" "api_key"
```

## Shodan/Censys Dorking (Infrastructure OSINT)
```
# Shodan
org:"Target Organization"
hostname:target.com
ssl:"target.com"
port:22 org:"Target Organization"

# Censys
services.tls.certificates.leaf_data.subject.common_name: "target.com"
```

## GitHub Code Search Dorking
```
"target.com" password
"target.com" api_key
"target-domain" secret
org:target-github-org filename:.env
```

## Wayback Machine / Archive Dorking
```
http://web.archive.org/web/*/target.com/*     All archived snapshots
# Use the CDX API for programmatic historical URL enumeration
curl "http://web.archive.org/cdx/search/cdx?url=target.com*&output=json"
```

## Combining for Efficiency
```
site:target.com (filetype:pdf OR filetype:doc OR filetype:xls) intext:confidential
"Full Name" (site:linkedin.com OR site:twitter.com OR site:github.com)
```

## Caveats
- Search engines change/restrict dork operator support over time; verify
  operators still function before relying on them
- Cached/archived content may be outdated — always note the access/capture
  date when citing as evidence
