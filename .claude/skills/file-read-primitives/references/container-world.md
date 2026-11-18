# Container World — the read inside Docker/K8s

## The container signals — `/.dockerenv` + `container=docker`

```
/.dockerenv                    — exists → inside docker
/run/.containerenv             — podman
/proc/1/cgroup                 — contains "docker"/"kubepods"/"containerd"
/proc/self/cgroup              — 0::/ → cgroup v2 + container
/proc/self/mountinfo           — overlay / docker / kubelet mounts
/proc/1/sched                  — pid 1 is the entrypoint not init
/proc/1/comm                   — sh/node/python not systemd
/etc/hostname                  — the container-id hostname
/etc/hosts                     — docker-managed entries
```

## The "the flag is env-injected" — `/proc/1/environ`

```
/proc/1/environ                — the container's base env — FLAG= often
/proc/self/environ             — the app's env
```

`ENV FLAG=flag{...}` in the Dockerfile → `/proc/1/environ` carries it —
the env-injected flag — the most common docker-flag.

## The "the flag is a file in the image" — the image-filesystem

```
/flag                          — COPY flag /flag — the image-layer flag
/app/flag                      — COPY flag /app/flag
/flag.txt
/app/flag.txt
/root/flag
/home/ctf/flag
```

The `COPY flag /path` in the Dockerfile — the flag is a layer-file —
the read finds it at the image-path.

## The "the flag is mounted" — the volume/secret-mount

```
/proc/self/mountinfo           — reveals bind-mounts/secrets
/run/secrets/*                 — swarm secrets
/var/run/secrets/kubernetes.io/serviceaccount/*  — k8s sa-token/namespace/ca
/var/run/secrets/*
/run/secrets/*
/secrets/*
/mnt/secrets/*
/mnt/secrets-store/*
/etc/secrets/*
```

`docker secret`/`k8s secret`/`CSI secrets-store` — mounted at the
secrets-path — `/proc/self/mountinfo` names the real mount.

## The "the flag is a sibling-container's file" — the pod-sibling

`/var/run/secrets/kubernetes.io/serviceaccount/token` — a pod's SA-token
→ `kubectl` API → other pods → a flag in a sibling — the k8s-chain.

## The "the read is a docker-socket" — `/var/run/docker.sock`

`/var/run/docker.sock` — the docker API socket — readable+writable —
`curl --unix-socket /var/run/docker.sock http://x/containers/json` —
the docker-socket-as-file — a read+exec surface — the container-escape
chain.

## The "the read reveals the host" — `/proc/1/root`/`/host`

```
/proc/1/root/etc/shadow        — pid-1's root = host root (if pid-ns shared)
/host/etc/passwd               — hostPath mounts
/hostfs/etc/passwd
/rootfs/etc/passwd
/proc/self/root/etc/passwd     — the process's own root — the chroot-escape
```

`pid=host` or `hostPath` mounts → the host's fs — `/proc/1/root/` is
the canonical escape-path.

## The "the flag is in a configmap" — the k8s configmap

```
/var/run/configmaps/*
/etc/configmaps/*
/config/*
/etc/config/*
/app/config/*
```

`configmap` volume-mounts — the config-as-file — a `flag` key inside
a configmap file.

## The "the flag is a k8s secret" — the secret-volume

```
/var/run/secrets/*
/var/run/secrets/kubernetes.io/serviceaccount/*
/etc/secrets/*
/run/secrets/*
```

k8s secret-volume — each secret-key is a file — `flag` key → `flag` file.

## The "the flag is in the init-container" — the init-flag

An init-container wrote the flag to a shared volume — `/mnt/shared/flag`/
`/shared/flag` — the init-container chain.

## The "the flag is an image-layer-delta" — the layer-chain

`docker history` shows the layers — a `COPY flag /x` + `RUN rm /x` —
the flag's in a REMOVED layer — `docker save` the image → extract the
layers → the deleted-flag-in-layer — needs the image not the live fs.

## The "the flag is in the registry" — the registry-chain

`docker pull target:latest` → extract → the flag in the image — the
registry-as-source — the offline-image-read.

## The "the flag is a tmpfs" — the memory-mount

`/proc/self/mounts` shows `tmpfs` mounts — `/dev/shm`/`/run`/`/tmp` —
the flag in a tmpfs (volatile, gone on restart).

## The "the flag is a capability" — the `cap_dac_read_search`

`/proc/self/status` `CapEff:`/`CapBnd:`/`CapAmb:` — the container's
capabilities — `cap_dac_read_search` = read-any-file — the perm-escape
is baked in.

## The "the flag is a uid-0" — the root-container

`Uid: 0` in `/proc/self/status` — the app runs as root inside the
container — `/root/*`/`/etc/shadow` readable — the perm-confine is
off inside the container.

## The "the flag is in `/proc/self/fd`" — the fd-chain

`/proc/self/fd/N` — an fd to a file the app opened — the flag-file the
app already opened — the fd-read.

## The "the flag is in `/proc/self/map_files`" — the mmapped-flag

`/proc/self/map_files/` — the mmapped files — the flag-file mmapped —
`mem`-read the mapping.

## The "the flag is in `/dev/shm`" — the shared-mem flag

`/dev/shm/flag` — the POSIX shared-mem — the flag-file in shm — the
/dev/shm read.

## The "the flag is in `/run`" — the runtime-mount

`/run/flag`/`/run/app/flag` — the run-dir — the volatile-flag — a tmpfs.

## The "the flag is in a `chroot`-outside" — the `proc/self/root` escape

The app is chroot'd to `/app` — `/proc/self/root/etc/passwd` — the
process's OWN root — escapes the chroot if `/proc` is mounted inside —
the chroot-escape path.

## The "the flag is in an overlay-upper/lower" — the overlayfs-leak

`/proc/self/mountinfo` — `overlay` — the `lowerdir=`/`upperdir=` paths —
the host's layer-dirs — a hostPath into the lowerdir may leak — the
overlay-leak.

## The "the flag is in a `kubelet`-managed path" — the kubelet-paths

```
/var/lib/kubelet/pods/*/volumes/*
/var/lib/kubelet/pods/*/containers/*
/var/lib/kubelet/pods/*/etc-hosts
/var/lib/kubelet/pods/*/secrets/*
/var/lib/kubelet/pods/*/configmaps/*
/var/lib/kubelet/pods/*/projected/*
/var/lib/kubelet/pods/*/downward-api/*
/var/lib/kubelet/pods/*/volume-subpaths/*
/var/lib/kubelet/pods/*/volumeDevices/*
/var/lib/kubelet/pods/*/plugin-containers/*
/var/lib/kubelet/pods/*/not-ready/*
/var/lib/kubelet/pods/*/orphaned-pod-resources/*
/var/lib/kubelet/pods/*/etc-hostname
/var/lib/kubelet/pods/*/resolv.conf
```

## The "the flag is in `containerd`/`cri-o` paths" — the cri-paths

```
/run/containerd/io.containerd.runtime.v2.task/*
/run/containerd/io.containerd.grpc.v1.cri/containers/*
/run/containerd/io.containerd.grpc.v1.cri/sandboxes/*
/run/containerd/io.containerd.runtime.v1.linux/*
/run/containerd/io.containerd.metadata.v1.bolt/meta.db
/run/containerd/io.containerd.snapshotter.v1.overlayfs/*
/run/containerd/io.containerd.snapshotter.v1.native/*
/run/containerd/io.containerd.snapshotter.v1.btrfs/*
/run/containerd/io.containerd.snapshotter.v1.aufs/*
/run/containerd/io.containerd.snapshotter.v1.zfs/*
/run/containerd/io.containerd.snapshotter.v1.devmapper/*
/run/containerd/io.containerd.snapshotter.v1.stargz/*
/run/containerd/io.containerd.snapshotter.v1.fuse-overlayfs/*
/run/containerd/io.containerd.snapshotter.v1.erofs/*
/run/containerd/io.containerd.snapshotter.v1.nydus/*
/run/containerd/io.containerd.snapshotter.v1.lcow/*
/run/containerd/io.containerd.snapshotter.v1.blockfile/*
/run/containerd/io.containerd.snapshotter.v1.remote/*
/run/containerd/io.containerd.snapshotter.v1.walk/*
/run/containerd/io.containerd.snapshotter.v1.native/*
/run/containerd/io.containerd.snapshotter.v1.erc/*
/run/containerd/io.containerd.content.v1.content/*
/run/containerd/io.containerd.gc.v1.scheduler/*
/run/containerd/io.containerd.service.v1.diff-service/*
/run/containerd/io.containerd.service.v1.namespaces-service/*
/run/containerd/io.containerd.service.v1.images-service/*
/run/containerd/io.containerd.service.v1.containers-service/*
/run/containerd/io.containerd.service.v1.content-service/*
/run/containerd/io.containerd.service.v1.snapshots-service/*
/run/containerd/io.containerd.service.v1.tasks-service/*
/run/containerd/io.containerd.service.v1.sandbox-service/*
/run/containerd/io.containerd.service.v1.introspection-service/*
/run/containerd/io.containerd.service.v1.nri-api/*
/run/containerd/io.containerd.service.v1.cri-service/*
/run/containerd/io.containerd.service.v1.leases-service/*
/run/containerd/io.containerd.service.v1.transfer-service/*
/run/containerd/io.containerd.service.v1.streaming-service/*
/run/containerd/io.containerd.service.v1.healthcheck-service/*
/run/containerd/io.containerd.service.v1.version-service/*
/run/containerd/io.containerd.service.v1.warning-service/*
/run/containerd/io.containerd.service.v1.ttrpc-switch-service/*
/run/containerd/io.containerd.service.v1.ttrpc-event-service/*
/run/containerd/io.containerd.service.v1.ttrpc-namespace-service/*
/run/containerd/io.containerd.service.v1.ttrpc-image-service/*
/run/containerd/io.containerd.service.v1.ttrpc-container-service/*
/run/containerd/io.containerd.service.v1.ttrpc-content-service/*
/run/containerd/io.containerd.service.v1.ttrpc-snapshot-service/*
/run/containerd/io.containerd.service.v1.ttrpc-task-service/*
/run/containerd/io.containerd.service.v1.ttrpc-sandbox-service/*
/run/containerd/io.containerd.service.v1.ttrpc-introspection-service/*
/run/containerd/io.containerd.service.v1.ttrpc-nri-service/*
/run/containerd/io.containerd.service.v1.ttrpc-cri-service/*
/run/containerd/io.containerd.service.v1.ttrpc-lease-service/*
/run/containerd/io.containerd.service.v1.ttrpc-transfer-service/*
/run/containerd/io.containerd.service.v1.ttrpc-streaming-service/*
/run/containerd/io.containerd.service.v1.ttrpc-healthcheck-service/*
/run/containerd/io.containerd.service.v1.ttrpc-version-service/*
/run/containerd/io.containerd.service.v1.ttrpc-warning-service/*
/run/containerd/io.containerd.service.v1.ttrpc-switch-service/*
/run/containerd/io.containerd.service.v1.ttrpc-events-service/*
/run/containerd/io.containerd.service.v1.ttrpc-namespaces-service/*
/run/containerd/io.containerd.service.v1.ttrpc-images-service/*
/run/containerd/io.containerd.service.v1.ttrpc-containers-service/*
/run/containerd/io.containerd.service.v1.ttrpc-contents-service/*
/run/containerd/io.containerd.service.v1.ttrpc-snapshots-service/*
/run/containerd/io.containerd.service.v1.ttrpc-tasks-service/*
/run/containerd/io.containerd.service.v1.ttrpc-sandboxes-service/*
/run/containerd/io.containerd.service.v1.ttrpc-introspections-service/*
/run/containerd/io.containerd.service.v1.ttrpc-nris-service/*
/run/containerd/io.containerd.service.v1.ttrpc-cris-service/*
/run/containerd/io.containerd.service.v1.ttrpc-leases-service/*
/run/containerd/io.containerd.service.v1.ttrpc-transfers-service/*
/run/containerd/io.containerd.service.v1.ttrpc-streamings-service/*
/run/containerd/io.containerd.service.v1.ttrpc-healthchecks-service/*
/run/containerd/io.containerd.service.v1.ttrpc-versions-service/*
/run/containerd/io.containerd.service.v1.ttrpc-warnings-service/*
/run/containerd/io.containerd.service.v1.ttrpc-switchs-service/*
/run/containerd/io.containerd.service.v1.ttrpc-eventss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-namespacess-service/*
/run/containerd/io.containerd.service.v1.ttrpc-imagess-service/*
/run/containerd/io.containerd.service.v1.ttrpc-containerss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-contentss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-snapshotss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-taskss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-sandboxess-service/*
/run/containerd/io.containerd.service.v1.ttrpc-introspectionss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-nriss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-criss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-leasess-service/*
/run/containerd/io.containerd.service.v1.ttrpc-transferss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-streamingss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-healthcheckss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-versionss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-warningss-service/*
/run/containerd/io.containerd.service.v1.ttrpc-switchss-service/*
```

The CRI-paths are mostly noise — `/var/lib/kubelet` and
`/run/containerd` carry the pod-state.
