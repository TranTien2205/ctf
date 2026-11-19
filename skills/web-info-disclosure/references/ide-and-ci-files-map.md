# IDE and CI config exposure — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.idea/workspace.xml or /.vscode/settings.json | IDE files | read for paths/tasks |
| /.gitlab-ci.yml or /.travis.yml | CI config | deploy targets, scripts, secret names |
| /docker-compose.yml or /Dockerfile | container layout | paths, env names, internal hosts |
| /.github/workflows/*.yml | Actions config | secrets usage, internal infra |

## Falsifier

Falsifier — none of the build-time files are served: the channel is closed.
