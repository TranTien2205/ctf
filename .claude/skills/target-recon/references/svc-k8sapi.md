# Service recon: k8sapi

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Kubernetes API 6443/8443/10250: /version JSON,
/api/v1/namespaces (401 vs 200 tells auth posture),
kubelet :10250 /pods (unauthenticated kubelet = pod list =
workload map). Service-account tokens in mounted paths are a
later-stage note.
## Pivot

Signal harvested -> out-*; route named -> that skill.
