# IDE and CI config exposure

.idea/, .vscode/, .gitlab-ci.yml, .travis.yml, .github/workflows/, docker-compose.yml: build-time secrets and internal layout.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.idea/workspace.xml or /.vscode/settings.json | IDE files | read for paths/tasks |
| /.gitlab-ci.yml or /.travis.yml | CI config | deploy targets, scripts, secret names |
| /docker-compose.yml or /Dockerfile | container layout | paths, env names, internal hosts |
| /.github/workflows/*.yml | Actions config | secrets usage, internal infra |

## Steps

1. Probe the bounded list: .idea/workspace.xml .vscode/ .gitlab-ci.yml .travis.yml docker-compose.yml Dockerfile .github/workflows/.
2. CI files name which secrets exist (variable names) even when values are masked.
3. docker-compose/Dockerfile reveals internal service names, ports, mounts — the topology.
4. Each named path/host is a later probe target.

## Falsifier

Falsifier — none of the build-time files are served: the channel is closed.

## Traps

- CI files often list secret NAMES not values — still an inventory of what to hunt.
- docker-compose usually reveals internal hostnames the app depends on.
- .idea can contain run configurations with credentials.

## Commands

```bash
for p in /.gitlab-ci.yml /docker-compose.yml /Dockerfile /.idea/workspace.xml; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `source-disclosure.md`
