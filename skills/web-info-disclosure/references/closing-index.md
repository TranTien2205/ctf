# Closing index — by question

## "Where do I start?"
`workflow.md` → `bounded-sweep.md` → `catchall-falsifier.md` (baseline first).

## "What might be exposed?"
`detection-matrix.md` → `exposed-artifacts.md` → the per-channel files.

## "Found .git / .env / an archive / a map / debug page"
`git-exposure.md` `env-config-leaks.md` `env-file-variants.md`
`backup-archives.md` `sql-dump-read.md` `source-maps.md`
`debug-endpoints.md` `framework-debug.md` `spring-actuator-deep.md`
`django-debug.md` `laravel-debug.md` `werkzeug-debug.md` `phpinfo-read.md`

## "403 on something real"
`alternate-verbs.md` `host-header-probes.md` `response-anatomy.md`
`error-timing.md`

## "Found a route/host name"
`robots-sitemap.md` `internal-vhosts.md` `api-docs-exposure.md`
`graphql-introspection.md` `oauth-wellknown.md` `redirect-leaks.md`
`comment-leaks.md`

## "Ops surface"
`status-pages.md` `apache-nginx-status.md` `prometheus-metrics.md`
`health-endpoints.md` `log-exposure.md` `header-disclosure.md`
`header-leaks-deep.md`

## "Loose files / keys / manifests"
`source-disclosure.md` `static-leftovers.md` `swp-and-temp.md`
`ds-store-parse.md` `pem-key-files.md` `manifest-files.md`
`ide-and-ci-files.md` `static-config-files.md` `secrets-in-js.md`
`version-control-metadata.md` `cloud-metadata.md` `well-known-and-meta.md`
`sourcemap-sibling.md` `wayback-and-cache.md` `graphql-and-ws-endpoints.md`

## "Now what — chain it"
`chaining.md` `multi-step-chains.md` `evidence.md` `falsifiers.md`
`negative-results.md` `operator-notes.md` `anti-patterns.md`
`troubleshoot.md` `worked-examples.md` `case-studies.md`

## Tools
`tools-git-dumper.md` `tools-bundle-miner.md` `tools-http-probe.md`
`tools-read-loop.md` `tools-id-sweep.md`
