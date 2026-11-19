# IDE and CI config exposure — case catalogue

.idea/, .vscode/, .gitlab-ci.yml, .travis.yml, .github/workflows/, docker-compose.yml: build-time secrets and internal layout.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.idea/workspace.xml or /.vscode/settings.json | IDE files | read for paths/tasks |
| 2 | /.gitlab-ci.yml or /.travis.yml | CI config | deploy targets, scripts, secret names |
| 3 | /docker-compose.yml or /Dockerfile | container layout | paths, env names, internal hosts |
| 4 | /.github/workflows/*.yml | Actions config | secrets usage, internal infra |

## Falsifier

Falsifier — none of the build-time files are served: the channel is closed.
