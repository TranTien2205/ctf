# Multi-step chains — disclosure to flag



## .env → JWT secret → session → flag
env-config-leaks → extract JWT_SECRET → web-auth-session forge → flag.

## .git → source → sink → flag
git-exposure → read recovered source → find the vulnerable route → its class → flag.

## .map → endpoint → SSRF → flag
source-maps → recovered route list → /internal/fetch → web-ssrf → flag.

## actuator/env → creds → login → flag
debug-endpoints → env creds → login → flag.

## backup.zip → DB dump → creds → flag
backup-archives → dump.sql → creds → login/db → flag.

## comment → path → config → key → flag
comment-leaks → named path → config file → key → its sink → flag.

Each chain step has a falsifier; a chain dies at the first step that falsifies.

## Falsifier

--

## Cross-references

`chaining.md`
