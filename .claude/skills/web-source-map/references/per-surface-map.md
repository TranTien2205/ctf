# Per-surface map — the bundle surfaces and their yields, mapped

## The surface index

| Surface | Where | Mines for | File |
|---|---|---|---|
| route table | `path:`/`Route`/`loadChildren` | client routes + gates | `route-table.md`, `route-guard.md` |
| fetch/axios | call sites | endpoints + contract | `endpoint-inventory.md` |
| config | `config.js`/`process.env`/`__NEXT_DATA__` | keys, flags, hosts | `config-mining.md`, `per-prefix.md` |
| feature flag | `feature.`/`flags.`/`isAdmin` | the gated surface | `flag-mining.md` |
| auth | `token`/`Authorization`/`localStorage` | credentials + format | `authenticated-bundle.md` |
| endpoint-string | `"/..."` literals | non-call-site endpoints | `extraction.md` |
| comment | `sourcesContent` comments | dev notes/flag | `comment-mining.md` |
| manifest | `_buildManifest`/`asset-manifest`/`sw.js` | the asset/route list | `service-worker-mining.md` |
| env-inline | `process.env`/`DefinePlugin`/`import.meta.env` | inlined config | `config-mining.md` |
| structure | `sources` file names | the app layout | `structure-mining.md` |
| param | `?x=`/`{x:`/`append`/`body` | injection points | `param-surface.md`, `per-param.md` |
| GraphQL | `/graphql`/query strings | the schema hints | `graphql-surface.md` |
| sink | recovered-source sinks | the vuln's class | `sink-mining.md`, `per-sink.md` |
| adjacent | `.git`/`.env`/backups | the bigger leak | `adjacent-disclosure.md` |

## The surface → yield map

| Surface | Primary yield | Route |
|---|---|---|
| config | a credential/host | `web-auth-session`/`web-ssrf` |
| fetch | a hidden endpoint | its class |
| flag | a client-gated surface | `web-logic-flaw` |
| auth | a token/format | `web-auth-session` |
| manifest | a lazy/admin chunk | mine it |
| comment | a flag/secret | `pre-flag`/verify |
| sink | the vuln | its class |
| structure | hosted source paths | `file-read` |
| adjacent | `.git`/`.env` | `web-info-disclosure` |

## The surface-density note

The highest-density surfaces per byte: `config.js`/`env.js` (secrets),
a `.map` `sourcesContent` (everything), a page/lazy chunk (hidden
endpoints), the manifest (the complete inventory). Mine those first.
