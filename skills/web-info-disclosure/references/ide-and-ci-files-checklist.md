# IDE and CI config exposure — checklist

.idea/, .vscode/, .gitlab-ci.yml, .travis.yml, .github/workflows/, docker-compose.yml: build-time secrets and internal layout.

## Checklist

- [ ] Probe the bounded list: .idea/workspace.xml .vscode/ .gitlab-ci.yml .travis.yml docker-compose.yml Dockerfile .github/workflows/.
- [ ] CI files name which secrets exist (variable names) even when values are masked.
- [ ] docker-compose/Dockerfile reveals internal service names, ports, mounts — the topology.
- [ ] Each named path/host is a later probe target.

## Abort conditions

- CI files often list secret NAMES not values — still an inventory of what to hunt.
- docker-compose usually reveals internal hostnames the app depends on.
- .idea can contain run configurations with credentials.

## Falsifier

Falsifier — none of the build-time files are served: the channel is closed.
