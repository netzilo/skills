---
id: '53'
title: Netzilo Server on OpenShift (on-premises) — Helm charts
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 50147
sections:
- id: '1'
  title: What gets deployed
  chars: 2639
- id: '2'
  title: What you need before starting
  chars: 3272
- id: '3'
  title: Choose the path
  chars: 506
- id: '4'
  title: Images
  chars: 1956
- id: '5'
  title: Cluster prerequisites
  chars: 4769
- id: '6'
  title: Install with Helm
  chars: 23184
- id: '7'
  title: Install with the Terraform module
  chars: 2410
- id: '8'
  title: Verify — every gate must pass
  chars: 2933
- id: '9'
  title: Day-2
  chars: 1302
- id: '10'
  title: Pitfalls and remedies
  chars: 5472
- id: '11'
  title: Reporting template
  chars: 609
---
# Netzilo Server on OpenShift (on-premises) — Helm charts

**Audience:** an AI operator installing **Netzilo Server** on a customer's own
**Red Hat OpenShift** cluster (4.x, on-premises or any infrastructure where OpenShift
runs), from the **Netzilo container images** and the **Netzilo Helm charts** the customer
gives you as a local directory. Nothing in this procedure downloads a chart; the images
come from the customer's registry or from Netzilo's public registry.

**Contract:** the same as every install (`01-server-install.md`): never invent input
values, echo the full set back (passwords masked) and get an explicit "yes" before
running anything, and report success only when every gate in §8 passes. A step that
fails is diagnosed with §10 before anything is re-run.

**Two ways, one result.** §6 installs with `helm` and `oc`/`kubectl` only. When the
customer also gives you the **Netzilo OpenShift Terraform module**, §7 does the same in
one `terraform apply`; it installs exactly the same charts with the same values. Read
§1–§5 either way: they are what both paths assume.

---

## 1. What gets deployed

Everything runs in one namespace (`netzilo` below), plus `ingress-nginx` in its own.

| Component | Chart (from the directory you are given) | Runs under SCC | Exposed |
|---|---|---|---|
| Management (REST `/api`, gRPC), with its AI-data retention CronJob | `net-management` | `restricted-v2` | through the ingress: `https://<domain>/api/`, `/management.ManagementService/`, `/ws-proxy/management` |
| Signal | `net-signal` | `restricted-v2` | through the ingress: `/signalexchange.SignalExchange/`, `/ws-proxy/signal` |
| Dashboard | `net-dashboard` | **`anyuid`** (its image runs nginx as root) | through the ingress: `https://<domain>/` |
| Zitadel (identity provider) | `net-zitadel` | `restricted-v2` | through the ingress: `/oauth/v2/`, `/oidc/v1/`, `/ui/`, `/.well-known/openid-configuration`, its APIs |
| First-install bootstrap (two Jobs) | `net-bootstrap` (installed twice) | `restricted-v2` | nothing |
| AI Assistant worker | `net-support-worker` | `restricted-v2` | inside the cluster only |
| Clientless-access gateway | `net-gateway` | `restricted-v2` | `<domain>:8443` — the **same address** as the ingress (§5.1) |
| TURN relay | `coturn` | `restricted-v2` | `<turn_domain>:3478` TCP+UDP, `:5349` (TURNS) — its own address |
| Published applications (optional) | `net-reverse-proxy` | `restricted-v2` | through the ingress: `https://*.<apps_domain>/` |
| Ingress controller | upstream `ingress-nginx` 4.15.1 | `nonroot-v2` | `<domain>:443`, `:80` |
| Postgres (`netzilo` and `zitadel` databases) | CloudNativePG `Cluster` (operator 1.30), or the customer's server | `restricted-v2` | inside the cluster |
| Redis | a small Deployment (§6.5), or the customer's server | `restricted-v2` | inside the cluster |

Each Netzilo chart directory holds `values.yaml` (Netzilo's own cloud settings) **and
`values-openshift.yaml`**, the OpenShift overlay. Every `helm` command in §6 passes the
overlay first and the install's own values file second; without the overlay the pods are
refused by OpenShift (§10).

**One replica of each Netzilo component.** Management, Signal, Zitadel, the gateway, the
reverse proxy and the relay each run as a single pod. Management and Signal keep each
connected device's session in the pod that serves it, so a second replica breaks
devices that land on different pods. Do not raise `replicas`, do not add a
HorizontalPodAutoscaler. Resilience comes from OpenShift restarting the pod, a Postgres
with replicas (§6.4 `instances`) and backups (§9.3).

**Not included:** monitoring (use OpenShift's own), Netzilo's documentation site, the AI
Gateway (`27-ai-gateway.md`).

## 2. What you need before starting

### 2.1 Inputs — ask the customer for each

| Input | Example | Notes |
|---|---|---|
| Domain | `netzilo.example.com` | the dashboard, the APIs, Zitadel and the gateway, one name |
| TURN name | `turn.netzilo.example.com` | its own DNS record and address |
| Applications domain (optional) | `apps.example.com` | only for published applications (`44-published-applications.md`) |
| TLS certificate + key (PEM, with chain) | `fullchain.pem`, `privkey.pem` | must cover the domain **and** the TURN name: `*.netzilo.example.com` plus `netzilo.example.com` |
| Applications certificate + key | `*.apps.example.com` | only with an applications domain |
| Issuing CA (PEM) | `internal-ca.pem` | required when the certificate comes from an internal CA (§10, "x509: certificate signed by unknown authority") |
| Administrator e-mail, first and last name | `admin@example.com`, Ada, Admin | the first sign-in; a password is generated (§6.1) |
| How the cluster exposes services | MetalLB pool with two addresses, or an external load balancer in front of the nodes | §5.1 |
| Postgres | in the cluster (CloudNativePG), or the customer's server: host, port, sslmode, an administrative user and password | §6.4 |
| Redis | in the cluster, or the customer's: `host:port`, password, TLS | §6.5 |
| Registry | `registry.example.com:5000/netzilo`, with a pull secret if it needs one | §4 |
| Charts directory | `/opt/netzilo/charts` | the Netzilo charts, unpacked |
| Upstream charts directory | `/opt/netzilo/upstream` | `ingress-nginx-4.15.1.tgz`, `cloudnative-pg-0.29.1.tgz`, `metallb-0.16.2.tgz` (the last two only when §5 installs them) |
| Netzilo version | `latest` or a tag | the tag of every Netzilo image |
| StorageClass | the cluster default, or a name | for Postgres, Redis and the reverse proxy |

Echo the set back with passwords masked and get a "yes".

### 2.2 Gate 0 — the cluster and the tools

```bash
oc whoami && oc auth can-i '*' '*' --all-namespaces      # cluster-admin: "yes"
oc version                                                # OpenShift 4.x
helm version                                              # 3.13 or later
oc get clusterrole system:openshift:scc:anyuid system:openshift:scc:nonroot-v2 system:openshift:scc:privileged
oc get storageclass                                       # one marked (default), or the customer names one
ls "$CHARTS"   # net-bootstrap net-dashboard net-gateway net-management net-reverse-proxy net-signal net-support-worker net-zitadel coturn
ls "$CHARTS"/*/values-openshift.yaml | wc -l              # 8 (net-bootstrap has none)
```

`kubectl` works everywhere `oc` is written below, except `oc adm policy`, whose YAML
equivalent is given. Every check must pass; stop and report the one that does not.

### 2.3 DNS records the customer creates

| Name | Points to |
|---|---|
| `<domain>` | the ingress address (§5.1) |
| `*.<apps_domain>` | the same ingress address (only with published applications) |
| `<turn_domain>` | the TURN address |

The customer's DNS must answer `AAAA` queries for these names with an empty answer
(`NOERROR`), never `NXDOMAIN`: Alpine-based clients and tools treat an `NXDOMAIN` on
`AAAA` as "the name does not exist" even when the `A` record is there.

## 3. Choose the path

| | §6 Helm | §7 Terraform module |
|---|---|---|
| You have | the charts, `helm`, `oc` | the charts, the module, `terraform` 1.5+ |
| Secrets | generated by you into a local file (§6.1) | generated by Terraform, kept in its state (a Secret in the cluster) |
| Re-run | `helm upgrade --install` with the same files | `terraform apply` |
| Choose when | the module is not provided, or the customer wants each step visible | the module is provided: fewer chances to mistype a value |

## 4. Images

Every pod pulls one of these. With a registry mirror, each reference becomes
`<registry>/<the reference without its registry host>`: `ghcr.io/netzilo/net-management:latest`
→ `registry.example.com:5000/netzilo/netzilo/net-management:latest` for
`<registry>` = `registry.example.com:5000/netzilo`.

| Image | Used by |
|---|---|
| `ghcr.io/netzilo/net-management:<version>` | Management |
| `ghcr.io/netzilo/net-signal:<version>` | Signal |
| `ghcr.io/netzilo/net-dashboard:<version>` | Dashboard |
| `ghcr.io/netzilo/net-gateway:<version>` | Gateway |
| `ghcr.io/netzilo/net-reverse-proxy:<version>` | Reverse proxy |
| `ghcr.io/netzilo/net-support-worker:<version>` | AI Assistant worker |
| `ghcr.io/netzilo/zitadel-build:<version>` | Zitadel, the bootstrap's Zitadel steps |
| `docker.io/coturn/coturn:4.6.3-r2` | TURN |
| `docker.io/library/postgres:16.15` | the bootstrap's database step, the AI-data retention CronJob |
| `docker.io/library/redis:7.4.12` | Redis (in-cluster) |
| `registry.access.redhat.com/ubi9/python-312:9.9` | the bootstrap's script |
| `ghcr.io/cloudnative-pg/cloudnative-pg:1.30.1` | CloudNativePG operator (when §5.2 installs it) |
| `ghcr.io/cloudnative-pg/postgresql:16.15-minimal-trixie` | Postgres instances |
| `registry.k8s.io/ingress-nginx/controller:v1.15.1` | ingress controller |
| `registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.6.9` | ingress admission webhook |
| `quay.io/metallb/controller:v0.16.2`, `quay.io/metallb/speaker:v0.16.2` | MetalLB (when §5.1 installs it) |

The Netzilo images on `ghcr.io/netzilo` are public (anonymous pulls). They are built for
`linux/amd64`. Copy them to a mirror with `oc image mirror <src> <dst>` or
`skopeo copy docker://<src> docker://<dst>`. A registry that needs credentials: create a
`kubernetes.io/dockerconfigjson` Secret named `netzilo-pull` in each namespace (§6.2) and
add `imagePullSecrets: [{name: netzilo-pull}]` to every values file in §6.

## 5. Cluster prerequisites

### 5.1 How the domain and TURN are reached

The gateway listens on `8443` of **the same address** as the ingress (`443`/`80`):
browsers are sent to `<domain>:8443` by default. The gateway takes TLS connections
directly (no PROXY protocol), so it cannot sit behind the ingress controller; the two
Services share one address instead. TURN has an address of its own.

**MetalLB (the usual on-prem choice).** Install the **MetalLB Operator** from OperatorHub
(Red Hat's supported way) and create its `MetalLB` resource; or, without OperatorHub,
install it from the chart archive:

```bash
export UPSTREAM_CHARTS=/opt/netzilo/upstream     # the upstream charts directory (§2.1)
oc create namespace metallb-system
oc label namespace metallb-system pod-security.kubernetes.io/enforce=privileged pod-security.kubernetes.io/audit=privileged pod-security.kubernetes.io/warn=privileged --overwrite
oc adm policy add-scc-to-user privileged -z metallb-speaker -n metallb-system      # announces from the host network
oc adm policy add-scc-to-user nonroot-v2 -z metallb-controller -n metallb-system
helm upgrade --install metallb "$UPSTREAM_CHARTS/metallb-0.16.2.tgz" -n metallb-system --wait --timeout 10m \
  --set speaker.frr.enabled=false --set frrk8s.enabled=false
#  with a mirror add: --set controller.image.repository=<registry>/metallb/controller --set speaker.image.repository=<registry>/metallb/speaker
```

Then the pool, the same with either install. **`autoAssign: false` is required:** without
it a LoadBalancer Service that does not ask for an address (OpenShift's own router can
be one) takes the first free address of the pool, and the Netzilo Services then fail
with "address also in use".

```bash
oc apply -f - <<EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata: { name: netzilo, namespace: metallb-system }
spec:
  autoAssign: false
  addresses: [ "10.0.0.200-10.0.0.201" ]       # the customer's two addresses
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata: { name: netzilo, namespace: metallb-system }
spec: { ipAddressPools: [ netzilo ] }
EOF
```

The ingress and the gateway Services carry `metallb.io/address-pool: netzilo`,
`metallb.io/allow-shared-ip: netzilo-ingress` and `metallb.io/loadBalancerIPs:
<ingress address>`, TURN carries the pool and its own address. MetalLB shares an
address only between Services with the same key **and `externalTrafficPolicy:
Cluster`**; with `Local` the second Service never gets the address. The consequence:
the ingress and the gateway see the node's address as the client's, so posture checks by
the browser's network range or location judge the node, not the user. A customer who
needs the real client address there gives the gateway its own address and DNS name and
sets each account's clientless proxy address to it (`43-clientless-access-gateway.md`).

**Another load-balancer implementation** (a vendor controller): use its own annotations
in place of the MetalLB ones in §6 (the module's `load_balancer_annotations`).

**An external load balancer in front of the nodes (F5, HAProxy, NetScaler):** set
`SERVICE_TYPE=NodePort` in §6. After the install, `oc get svc -n ingress-nginx
ingress-nginx-controller` and `oc get svc -n netzilo net-gateway-service coturn` show the
node ports; the load balancer forwards `<domain>`: `443`, `80` and `8443` to the
ingress's `https`, `http` and the gateway's node ports on every node, and `<turn_domain>`:
`3478` TCP **and UDP** and `5349` TCP to TURN's. A UDP virtual server must pass the
relay's answers back (an nginx `stream` block with `proxy_responses 0` drops them, and
TURN over UDP then hangs).

### 5.2 Postgres operator (in-cluster Postgres only)

Install **CloudNativePG** from OperatorHub (certified operator), or from the archive. The
chart's operator runs as user `10001`, which `restricted-v2` refuses; the values must
remove that user, and because Helm **merges** values with the chart's defaults, that
means setting it to `null`, not leaving it out:

```bash
export UPSTREAM_CHARTS=/opt/netzilo/upstream     # the upstream charts directory (§2.1)
oc create namespace cnpg-system
cat > cnpg-values.yaml <<EOF
containerSecurityContext: { runAsUser: null, runAsGroup: null, allowPrivilegeEscalation: false, readOnlyRootFilesystem: true, capabilities: { drop: ["ALL"] } }
podSecurityContext: { runAsNonRoot: true, seccompProfile: { type: RuntimeDefault } }
EOF
#  with a mirror add to cnpg-values.yaml: image: { repository: <registry>/cloudnative-pg/cloudnative-pg, tag: "1.30.1" }
helm upgrade --install cnpg "$UPSTREAM_CHARTS/cloudnative-pg-0.29.1.tgz" -n cnpg-system -f cnpg-values.yaml --wait --timeout 10m
```

The operator detects OpenShift and lets the SCC pick the Postgres pods' user.

## 6. Install with Helm

Run the steps in one shell, in order. The first block sets what every later block reads;
adjust it to the customer's answers from §2.1.

```bash
export NS=netzilo ING_NS=ingress-nginx
export DOMAIN=netzilo.example.com TURN_DOMAIN=turn.netzilo.example.com
export APPS_DOMAIN=                          # empty: no published applications
export TLS_CERT=fullchain.pem TLS_KEY=privkey.pem
export APPS_TLS_CERT= APPS_TLS_KEY=
export CA_BUNDLE=                            # the issuing CA's PEM when it is internal
export ADMIN_EMAIL=admin@example.com ADMIN_FIRST_NAME=Ada ADMIN_LAST_NAME=Admin
export SERVICE_TYPE=LoadBalancer             # or NodePort (§5.1)
export METALLB_POOL=netzilo INGRESS_IP=10.0.0.200 TURN_IP=10.0.0.201
export REGISTRY=                             # empty: the public registries
export NETZILO_VERSION=latest
export PKG_BASE_URL=https://pkg.netzilo.com  # or an internal mirror of the client downloads
export PG_SIZE=20Gi
export CHARTS=/opt/netzilo/charts UPSTREAM_CHARTS=/opt/netzilo/upstream
img()  { [ -n "$REGISTRY" ] && echo "$REGISTRY/${1#*/}" || echo "$1"; }   # §4's rewrite
repo() { echo "${1%:*}"; }
tag()  { echo "${1##*:}"; }
W=$PWD/netzilo-install; mkdir -p "$W"; chmod 700 "$W"
```

With `SERVICE_TYPE=NodePort`, or a load balancer other than MetalLB, leave the three
`metallb.io/...` annotation lines out of the ingress, gateway and TURN values below.

### 6.1 Secrets

Generated once and kept in `secrets.env`, readable by you only. **Keep this file** (in
the customer's vault): it holds the Zitadel masterkey, without which a database backup
cannot be used, and the first administrator's password. Never print it.

```bash
if [ ! -f "$W/secrets.env" ]; then
  umask 077
  r() { openssl rand -base64 48 | tr -d '=+/\n' | head -c "$1"; }
  cat > "$W/secrets.env" <<EOF
TURN_PASSWORD=$(r 43)
DATASTORE_KEY=$(openssl rand -base64 32)
INTERNAL_API_TOKEN=nzl_$(r 34)
SUPPORT_WORKER_TOKEN=$(r 40)
ZITADEL_MASTERKEY=$(r 32)
ZITADEL_DB_PASSWORD=$(r 32)
MSP_KEY=nzl_msp_$(r 40)
ADMIN_PASSWORD=$(r 20)Aa1-
PG_SUPERUSER_PASSWORD=$(r 32)
PG_NETZILO_PASSWORD=$(r 32)
REDIS_PASSWORD=$(r 32)
EOF
fi
source "$W/secrets.env"
```

`ZITADEL_MASTERKEY` is exactly 32 characters. `ADMIN_PASSWORD` meets Zitadel's default
policy (upper, lower, digit, symbol); the administrator must change it at the first
sign-in. `MSP_KEY` makes every tenant Enterprise (no edition limits). With the customer's
own Postgres, set `PG_SUPERUSER_PASSWORD` to its administrative user's password; with
the customer's own Redis, `REDIS_PASSWORD` to its password.

### 6.2 Namespace, certificates, the dashboard's SCC

```bash
oc create namespace "$NS" --dry-run=client -o yaml | oc apply -f -
oc -n "$NS" create secret tls netzilo-tls --cert="$TLS_CERT" --key="$TLS_KEY" --dry-run=client -o yaml | oc apply -f -
[ -n "$APPS_DOMAIN" ] && oc -n "$NS" create secret tls netzilo-apps-tls --cert="$APPS_TLS_CERT" --key="$APPS_TLS_KEY" --dry-run=client -o yaml | oc apply -f -
[ -n "$CA_BUNDLE" ] && oc -n "$NS" create configmap netzilo-ca-bundle --from-file=ca.pem="$CA_BUNDLE" --dry-run=client -o yaml | oc apply -f -
oc apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata: { name: net-dashboard, namespace: $NS }
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: net-dashboard-scc-anyuid, namespace: $NS }
roleRef: { apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: "system:openshift:scc:anyuid" }
subjects: [ { kind: ServiceAccount, name: net-dashboard, namespace: $NS } ]
EOF
```

The RoleBinding is what `oc adm policy add-scc-to-user anyuid -z net-dashboard -n
netzilo` creates. A pull secret, when the registry needs one:
`oc -n "$NS" create secret generic netzilo-pull --type=kubernetes.io/dockerconfigjson
--from-file=.dockerconfigjson=pull-secret.json` (and the same in `ingress-nginx`).

### 6.3 Ingress controller

ingress-nginx terminates TLS for the domain with the customer's certificate and carries
Management's, Signal's and Zitadel's gRPC to them. The WebSocket fallbacks use
`configuration-snippet` annotations, so snippets must be allowed at risk level
`Critical`.

```bash
oc create namespace "$ING_NS" --dry-run=client -o yaml | oc apply -f -
for sa in ingress-nginx ingress-nginx-admission; do oc apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: $sa-scc-nonroot-v2, namespace: $ING_NS }
roleRef: { apiGroup: rbac.authorization.k8s.io, kind: ClusterRole, name: "system:openshift:scc:nonroot-v2" }
subjects: [ { kind: ServiceAccount, name: $sa, namespace: $ING_NS } ]
EOF
done
CTRL=$(img registry.k8s.io/ingress-nginx/controller:v1.15.1)
CERTGEN=$(img registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.6.9)
cat > "$W/ingress-nginx.yaml" <<EOF
controller:
  image: { registry: "$(dirname "$(dirname "$(repo "$CTRL")")")", image: "ingress-nginx/controller", tag: "$(tag "$CTRL")", digest: "", digestChroot: "" }
  ingressClass: nginx
  ingressClassResource: { name: nginx, enabled: true, default: false }
  allowSnippetAnnotations: true
  config:
    allow-snippet-annotations: "true"
    annotations-risk-level: Critical
    proxy-body-size: 1m
    server-tokens: "false"
    ssl-protocols: TLSv1.2 TLSv1.3
    use-gzip: "true"
  extraArgs: { default-ssl-certificate: "$NS/netzilo-tls" }
  service:
    type: $SERVICE_TYPE
    externalTrafficPolicy: Cluster
    annotations:
      metallb.io/address-pool: "$METALLB_POOL"
      metallb.io/allow-shared-ip: netzilo-ingress
      metallb.io/loadBalancerIPs: "$INGRESS_IP"
  admissionWebhooks:
    patch:
      image: { registry: "$(dirname "$(dirname "$(repo "$CERTGEN")")")", image: "ingress-nginx/kube-webhook-certgen", tag: "$(tag "$CERTGEN")", digest: "" }
EOF
helm upgrade --install ingress-nginx "$UPSTREAM_CHARTS/ingress-nginx-4.15.1.tgz" -n "$ING_NS" -f "$W/ingress-nginx.yaml" --wait --timeout 10m
INGRESS_CLUSTER_IP=$(oc -n "$ING_NS" get svc ingress-nginx-controller -o jsonpath='{.spec.clusterIP}')
```

The chart pins images by digest; `digest: ""` is required with a mirror, whose copies
can have other digests. `INGRESS_CLUSTER_IP` is used in §6.7: Management calls its
identity provider at `https://<domain>` and reaches it through this address instead of
going out to the load balancer and back (§10, "hairpin").

### 6.4 Postgres

**In the cluster (CloudNativePG):** the cluster's bootstrap creates the `netzilo`
database owned by `netzilo`, which Management connects as; Zitadel's init creates its
own database and user with the superuser.

```bash
oc -n "$NS" create secret generic netzilo-pg-superuser --type=kubernetes.io/basic-auth --from-literal=username=postgres --from-literal=password="$PG_SUPERUSER_PASSWORD" --dry-run=client -o yaml | oc apply -f -
oc -n "$NS" create secret generic netzilo-pg-netzilo --type=kubernetes.io/basic-auth --from-literal=username=netzilo --from-literal=password="$PG_NETZILO_PASSWORD" --dry-run=client -o yaml | oc apply -f -
oc apply -f - <<EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata: { name: netzilo-pg, namespace: $NS }
spec:
  instances: 1
  imageName: $(img ghcr.io/cloudnative-pg/postgresql:16.15-minimal-trixie)
  enableSuperuserAccess: true
  superuserSecret: { name: netzilo-pg-superuser }
  bootstrap:
    initdb: { database: netzilo, owner: netzilo, secret: { name: netzilo-pg-netzilo } }
  postgresql:
    parameters: { max_connections: "300" }
  storage: { size: $PG_SIZE }
EOF
oc -n "$NS" wait cluster/netzilo-pg --for=condition=Ready --timeout=15m
export PG_HOST=netzilo-pg-rw.$NS.svc PG_PORT=5432 PG_SSLMODE=require PG_ADMIN_USER=postgres
export PG_MGMT_USER=netzilo PG_MGMT_PASSWORD=$PG_NETZILO_PASSWORD
```

`instances: 3` adds replicas with automatic failover. `storageClass: <name>` under
`storage` picks a class other than the default.

**The customer's own Postgres (12 or later):** skip the block above and set
`PG_HOST`, `PG_PORT`, `PG_SSLMODE` (`require` unless the customer says otherwise),
`PG_ADMIN_USER` and `PG_SUPERUSER_PASSWORD` (its password) to theirs, and
`PG_MGMT_USER=$PG_ADMIN_USER PG_MGMT_PASSWORD=$PG_SUPERUSER_PASSWORD`. The administrative
user must be able to create databases and roles; the bootstrap creates `netzilo` when it
is missing and Zitadel's init creates `zitadel`. In `max_connections`, leave room for
about 220 connections (Management up to 200, Zitadel 20).

### 6.5 Redis

**In the cluster:**

```bash
oc -n "$NS" create secret generic netzilo-redis --from-literal=password="$REDIS_PASSWORD" --dry-run=client -o yaml | oc apply -f -
oc apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: netzilo-redis, namespace: $NS }
spec: { accessModes: [ReadWriteOnce], resources: { requests: { storage: 2Gi } } }
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: netzilo-redis, namespace: $NS }
spec:
  replicas: 1
  strategy: { type: Recreate }
  selector: { matchLabels: { app.kubernetes.io/name: netzilo-redis } }
  template:
    metadata: { labels: { app.kubernetes.io/name: netzilo-redis } }
    spec:
      securityContext: { runAsNonRoot: true, seccompProfile: { type: RuntimeDefault } }
      containers:
        - name: redis
          image: $(img docker.io/library/redis:7.4.12)
          args: ["redis-server", "--requirepass", "\$(REDIS_PASSWORD)", "--appendonly", "yes", "--dir", "/data"]
          env:
            - { name: REDIS_PASSWORD, valueFrom: { secretKeyRef: { name: netzilo-redis, key: password } } }
            - { name: REDISCLI_AUTH, valueFrom: { secretKeyRef: { name: netzilo-redis, key: password } } }
          ports: [ { name: redis, containerPort: 6379 } ]
          readinessProbe: { exec: { command: ["redis-cli", "ping"] } }
          securityContext: { allowPrivilegeEscalation: false, capabilities: { drop: ["ALL"] } }
          volumeMounts: [ { name: data, mountPath: /data } ]
      volumes: [ { name: data, persistentVolumeClaim: { claimName: netzilo-redis } } ]
---
apiVersion: v1
kind: Service
metadata: { name: netzilo-redis, namespace: $NS }
spec: { selector: { app.kubernetes.io/name: netzilo-redis }, ports: [ { name: redis, port: 6379, targetPort: redis } ] }
EOF
oc -n "$NS" rollout status deploy/netzilo-redis --timeout=10m
export REDIS_ADDR=netzilo-redis.$NS.svc:6379 REDIS_TLS=false
```

**The customer's own Redis:** set `REDIS_ADDR=<host>:<port>`, `REDIS_PASSWORD` and
`REDIS_TLS=true` when it serves TLS.

### 6.6 Zitadel and the first-install bootstrap

Three releases, in this order; each waits for the previous:

1. **`netzilo-zitadel-setup`** (chart `net-bootstrap`, `phase=zitadel-setup`): creates the
   `netzilo` database when missing, Zitadel's database and user (`zitadel init`) and its
   instance (`zitadel setup`), and keeps the PAT of Zitadel's machine user in the
   `netzilo-zitadel-pat` Secret. The PAT is valid for **one hour**.
2. **`net-zitadel`**: Zitadel itself.
3. **`netzilo-bootstrap`** (chart `net-bootstrap`, `phase=configure`): creates the
   `NETZILO` project, the `Dashboard` and `Cli` applications, Netzilo's Zitadel actions,
   the `netzilo-service-account` (Management's access to Zitadel) and the administrator;
   deletes Zitadel's own default administrator; writes the result to the **`netzilo-idp`
   Secret** (keys `dashboardClientId`, `cliClientId`, `idpClientId`, `idpClientSecret`,
   `orgId`, `projectId`, `adminEmail`); strips the PAT user's roles and deletes the PAT.

The bootstrap's Jobs are Helm hooks: Helm waits for them, and an upgrade runs them again,
which finds the work done and changes nothing. Zitadel's environment is one file,
`zitadel-env.yaml`, given to `net-zitadel` and to both bootstrap releases.

```bash
ZITADEL=$(img ghcr.io/netzilo/zitadel-build:$NETZILO_VERSION)
cat > "$W/zitadel-env.yaml" <<EOF
extraEnv:
  - { name: ZITADEL_LOG_LEVEL, value: "info" }
  - { name: ZITADEL_DATABASE_POSTGRES_HOST, value: "$PG_HOST" }
  - { name: ZITADEL_DATABASE_POSTGRES_PORT, value: "$PG_PORT" }
  - { name: ZITADEL_DATABASE_POSTGRES_DATABASE, value: "zitadel" }
  - { name: ZITADEL_DATABASE_POSTGRES_USER_USERNAME, value: "zitadel" }
  - { name: ZITADEL_DATABASE_POSTGRES_USER_SSL_MODE, value: "$PG_SSLMODE" }
  - { name: ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS, value: "20" }
  - { name: ZITADEL_DATABASE_POSTGRES_MAXIDLECONNS, value: "20" }
  - { name: ZITADEL_DATABASE_POSTGRES_MAXCONNLIFETIME, value: "30m" }
  - { name: ZITADEL_DATABASE_POSTGRES_MAXCONNIDLETIME, value: "5m" }
  - { name: ZITADEL_EXTERNALSECURE, value: "true" }
  - { name: ZITADEL_TLS_ENABLED, value: "false" }
  - { name: ZITADEL_EXTERNALPORT, value: "443" }
  - { name: ZITADEL_EXTERNALDOMAIN, value: "$DOMAIN" }
  - { name: ZITADEL_LOGSTORE_ACCESS_STDOUT_ENABLED, value: "true" }
  - { name: ZITADEL_LOGSTORE_EXECUTION_STDOUT_ENABLED, value: "true" }
  - { name: ZITADEL_SYSTEMDEFAULTS_MULTIFACTORS_OTP_ISSUER, value: "Netzilo" }
  - { name: ZITADEL_CACHES_CONNECTORS_REDIS_ENABLED, value: "true" }
  - { name: ZITADEL_CACHES_CONNECTORS_REDIS_ADDR, value: "$REDIS_ADDR" }
  - { name: ZITADEL_CACHES_CONNECTORS_REDIS_ENABLETLS, value: "$REDIS_TLS" }
  - { name: ZITADEL_CACHES_INSTANCE_CONNECTOR, value: "redis" }
  - { name: ZITADEL_CACHES_MILESTONES_CONNECTOR, value: "redis" }
  - { name: ZITADEL_DEFAULTINSTANCE_LOGINPOLICY_DEFAULTREDIRECTURI, value: "https://$DOMAIN/dashboard" }
  - { name: GOMAXPROCS, value: "2" }
EOF
cat > "$W/bootstrap.yaml" <<EOF
domain: $DOMAIN
image:
  tools: $(img registry.access.redhat.com/ubi9/python-312:9.9)
  zitadel: $ZITADEL
  postgres: $(img docker.io/library/postgres:16.15)
postgres: { host: $PG_HOST, port: $PG_PORT, sslmode: $PG_SSLMODE, adminUser: $PG_ADMIN_USER }
zitadelURL: http://net-zitadel-service.$NS.svc:8080
admin: { email: "$ADMIN_EMAIL", firstName: "$ADMIN_FIRST_NAME", lastName: "$ADMIN_LAST_NAME", passwordChangeRequired: true }
secrets:
  postgresAdminPassword: "$PG_SUPERUSER_PASSWORD"
  zitadelMasterkey: "$ZITADEL_MASTERKEY"
  zitadelDbPassword: "$ZITADEL_DB_PASSWORD"
  redisPassword: "$REDIS_PASSWORD"
  adminPassword: "$ADMIN_PASSWORD"
EOF
chmod 600 "$W"/*.yaml
helm upgrade --install netzilo-zitadel-setup "$CHARTS/net-bootstrap" -n "$NS" -f "$W/zitadel-env.yaml" -f "$W/bootstrap.yaml" --set phase=zitadel-setup --timeout 30m

ZPATHS=""
for p in /zitadel.admin.v1.AdminService/ /zitadel.auth.v1.AuthService/ /zitadel.management.v1.ManagementService/ /zitadel.system.v1.SystemService/ /zitadel.user.v2.UserService/ /zitadel.user.v1.UserService/ /zitadel.org.v2.OrganizationService/ /.well-known/openid-configuration; do
  ZPATHS+="        - { path: $p, pathType: ImplementationSpecific, backend: { service: { name: net-zitadel-service, port: { number: 8080 } } } }"$'\n'
done
for p in /admin/v1/ /auth/v1/ /management/v1/ /system/v1/ /assets/v1/ /ui/ /oidc/v1/ /saml/v2/ /oauth/v2/ /openapi/ /debug/ /device /v2/; do
  ZPATHS+="        - { path: $p, pathType: Prefix, backend: { service: { name: net-zitadel-service, port: { number: 8080 } } } }"$'\n'
done
cat > "$W/zitadel.yaml" <<EOF
image: { repository: $(repo "$ZITADEL"), tag: $(tag "$ZITADEL") }
secret:
  secrets:
    ZITADEL_MASTERKEY: "$ZITADEL_MASTERKEY"
    ZITADEL_DATABASE_POSTGRES_USER_PASSWORD: "$ZITADEL_DB_PASSWORD"
    ZITADEL_CACHES_CONNECTORS_REDIS_PASSWORD: "$REDIS_PASSWORD"
ingress:
  tls: [ { secretName: netzilo-tls, hosts: ["$DOMAIN"] } ]
  hosts:
    - host: $DOMAIN
      paths:
$ZPATHS
EOF
chmod 600 "$W/zitadel.yaml"
helm upgrade --install net-zitadel "$CHARTS/net-zitadel" -n "$NS" -f "$CHARTS/net-zitadel/values-openshift.yaml" -f "$W/zitadel-env.yaml" -f "$W/zitadel.yaml" --wait --timeout 15m
helm upgrade --install netzilo-bootstrap "$CHARTS/net-bootstrap" -n "$NS" -f "$W/zitadel-env.yaml" -f "$W/bootstrap.yaml" --set phase=configure --timeout 20m

idp() { oc -n "$NS" get secret netzilo-idp -o jsonpath="{.data.$1}" | base64 -d; }
DASHBOARD_CLIENT_ID=$(idp dashboardClientId); CLI_CLIENT_ID=$(idp cliClientId)
IDP_CLIENT_ID=$(idp idpClientId); IDP_CLIENT_SECRET=$(idp idpClientSecret)
```

The bootstrap's log: `oc -n netzilo logs job/netzilo-bootstrap` ends with `Deleted
bootstrap user zitadel-admin.`, `Stored the IdP settings in secret netzilo-idp.` and
`Done.`

### 6.7 Netzilo services

```bash
nz() { local i; i=$(img "ghcr.io/netzilo/$1:$NETZILO_VERSION"); echo "{ repository: $(repo "$i"), tag: $(tag "$i") }"; }
MGMT_URL=http://net-management-service.$NS.svc:80

cat > "$W/support-worker.yaml" <<EOF
image: $(nz net-support-worker)
secret: { secrets: { SUPPORT_WORKER_TOKEN: "$SUPPORT_WORKER_TOKEN" } }
EOF
helm upgrade --install net-support-worker "$CHARTS/net-support-worker" -n "$NS" -f "$CHARTS/net-support-worker/values-openshift.yaml" -f "$W/support-worker.yaml" --wait --timeout 10m

cat > "$W/management.yaml" <<EOF
image: $(nz net-management)
resources: { requests: { cpu: 250m, memory: 512Mi }, limits: { cpu: "2", memory: 4Gi } }
config:
  turnPassword: "$TURN_PASSWORD"
  dataStoreEncryptionKey: "$DATASTORE_KEY"
  internalApiToken: "$INTERNAL_API_TOKEN"
  idpClientSecret: "$IDP_CLIENT_SECRET"
  redisPassword: "$REDIS_PASSWORD"
onprem:
  domain: $DOMAIN
  turnDomain: $TURN_DOMAIN
  dashboardClientId: "$DASHBOARD_CLIENT_ID"
  cliClientId: "$CLI_CLIENT_ID"
  idpClientId: "$IDP_CLIENT_ID"
  redisAddr: $REDIS_ADDR
  redisTLS: $REDIS_TLS
  supportWorkerURL: http://net-support-worker-service.$NS.svc:8080
  managementURL: $MGMT_URL
secret:
  secrets:
    NETBIRD_STORE_ENGINE_POSTGRES_DSN: "host=$PG_HOST user=$PG_MGMT_USER password=$PG_MGMT_PASSWORD dbname=netzilo port=$PG_PORT sslmode=$PG_SSLMODE"
    NB_SUPPORT_WORKER_TOKEN: "$SUPPORT_WORKER_TOKEN"
    NB_SUPPORT_MANAGEMENT_URL: $MGMT_URL
    NETZILO_MSP_KEY: "$MSP_KEY"
ingress:
  tls: [ { secretName: netzilo-tls, hosts: ["$DOMAIN"] } ]
  hosts:
    - host: $DOMAIN
      paths:
        - { path: /management.ManagementService/, pathType: ImplementationSpecific, backend: { service: { name: net-management-service, port: { number: 80 } } } }
        - { path: /api/, pathType: Prefix, backend: { service: { name: net-management-service, port: { number: 80 } } } }
wsProxyIngress:
  tls: [ { secretName: netzilo-tls, hosts: ["$DOMAIN"] } ]
  hosts: ["$DOMAIN"]
hostAliases: [ { ip: "$INGRESS_CLUSTER_IP", hostnames: ["$DOMAIN"] } ]
EOF
if [ -n "$CA_BUNDLE" ]; then cat >> "$W/management.yaml" <<EOF
extraVolumes:
  - { name: data, emptyDir: {} }
  - { name: ca-bundle, configMap: { name: netzilo-ca-bundle } }
extraVolumeMounts:
  - { name: data, mountPath: /var/lib/netzilo }
  - { name: ca-bundle, mountPath: /etc/ssl/certs/netzilo-ca.pem, subPath: ca.pem, readOnly: true }
EOF
fi
chmod 600 "$W/management.yaml"
helm upgrade --install net-management "$CHARTS/net-management" -n "$NS" -f "$CHARTS/net-management/values-openshift.yaml" -f "$W/management.yaml" --wait --timeout 15m

cat > "$W/signal.yaml" <<EOF
image: $(nz net-signal)
ingress:
  tls: [ { secretName: netzilo-tls, hosts: ["$DOMAIN"] } ]
  hosts:
    - host: $DOMAIN
      paths:
        - { path: /signalexchange.SignalExchange/, pathType: ImplementationSpecific, backend: { service: { name: net-signal-service, port: { number: 10000 } } } }
wsProxyIngress:
  tls: [ { secretName: netzilo-tls, hosts: ["$DOMAIN"] } ]
  hosts: ["$DOMAIN"]
EOF
helm upgrade --install net-signal "$CHARTS/net-signal" -n "$NS" -f "$CHARTS/net-signal/values-openshift.yaml" -f "$W/signal.yaml" --wait --timeout 10m

cat > "$W/dashboard.yaml" <<EOF
image: $(nz net-dashboard)
extraEnv:
  - { name: AUTH_AUTHORITY, value: "https://$DOMAIN" }
  - { name: AUTH_CLIENT_ID, value: "$DASHBOARD_CLIENT_ID" }
  - { name: AUTH_AUDIENCE, value: "$DASHBOARD_CLIENT_ID" }
  - { name: AUTH_SUPPORTED_SCOPES, value: "openid profile email offline_access" }
  - { name: AUTH_REDIRECT_URI, value: "/nb-auth" }
  - { name: AUTH_SILENT_REDIRECT_URI, value: "/nb-silent-auth" }
  - { name: USE_AUTH0, value: "false" }
  - { name: NETBIRD_MGMT_API_ENDPOINT, value: "https://$DOMAIN" }
  - { name: NETBIRD_MGMT_GRPC_API_ENDPOINT, value: "https://$DOMAIN" }
  - { name: NETZILO_PKG_BASE_URL, value: "$PKG_BASE_URL" }
  - { name: NGINX_SSL_PORT, value: "443" }
  - { name: LETSENCRYPT_DOMAIN, value: "none" }
secret: { secrets: { NETZILO_MSP_KEY: "$MSP_KEY" } }
ingress:
  tls: [ { secretName: netzilo-tls, hosts: ["$DOMAIN"] } ]
  hosts:
    - host: $DOMAIN
      paths:
        - { path: /, pathType: Prefix, backend: { service: { name: net-dashboard-service, port: { number: 80 } } } }
EOF
chmod 600 "$W/dashboard.yaml"
helm upgrade --install net-dashboard "$CHARTS/net-dashboard" -n "$NS" -f "$CHARTS/net-dashboard/values-openshift.yaml" -f "$W/dashboard.yaml" --wait --timeout 10m

cat > "$W/gateway.yaml" <<EOF
image: $(nz net-gateway)
managementURL: $MGMT_URL
tls: { secretName: netzilo-tls }
service:
  type: $SERVICE_TYPE
  externalTrafficPolicy: Cluster
  annotations:
    metallb.io/address-pool: "$METALLB_POOL"
    metallb.io/allow-shared-ip: netzilo-ingress
    metallb.io/loadBalancerIPs: "$INGRESS_IP"
EOF
helm upgrade --install net-gateway "$CHARTS/net-gateway" -n "$NS" -f "$CHARTS/net-gateway/values-openshift.yaml" -f "$W/gateway.yaml" --wait --timeout 10m

COTURN=$(img docker.io/coturn/coturn:4.6.3-r2)
cat > "$W/coturn.yaml" <<EOF
image: { repository: $(repo "$COTURN"), tag: $(tag "$COTURN"), pullPolicy: IfNotPresent }
realm: $TURN_DOMAIN
secret: { secrets: { username: self, password: "$TURN_PASSWORD" } }
certificate: { existingSecret: netzilo-tls }
service:
  type: $SERVICE_TYPE
  externalTrafficPolicy: Cluster
  annotations:
    metallb.io/address-pool: "$METALLB_POOL"
    metallb.io/loadBalancerIPs: "$TURN_IP"
EOF
chmod 600 "$W/coturn.yaml"
helm upgrade --install coturn "$CHARTS/coturn" -n "$NS" -f "$CHARTS/coturn/values-openshift.yaml" -f "$W/coturn.yaml" --wait --timeout 10m

if [ -n "$APPS_DOMAIN" ]; then
cat > "$W/reverse-proxy.yaml" <<EOF
image: $(nz net-reverse-proxy)
managementURL: $MGMT_URL
domain: $APPS_DOMAIN
workplaceURL: https://$DOMAIN
certificate: { create: false, secretName: netzilo-apps-tls }
EOF
helm upgrade --install net-reverse-proxy "$CHARTS/net-reverse-proxy" -n "$NS" -f "$CHARTS/net-reverse-proxy/values-openshift.yaml" -f "$W/reverse-proxy.yaml" --wait --timeout 10m
fi
```

What the values mean, where they are not obvious:

- **`onprem.*` in Management** selects the self-contained `management.json` the overlay
  points at (one domain, in-cluster Zitadel, Redis and worker). TURN is announced as
  `stun:<turn_domain>:3478`, `turn:<turn_domain>:3478` (UDP) and
  `turns:<turn_domain>:5349` (TCP); Signal as `<domain>:443`.
- **The overlays** set what OpenShift needs and the cloud settings do not: no fixed user
  IDs anywhere (`restricted-v2` assigns one from the namespace's range), the
  `net.ipv4.ip_unprivileged_port_start=0` sysctl on Management and Signal (both listen on
  `:80` as an arbitrary non-root user), a writable data directory for Management, the
  dashboard's `anyuid` service account, the customer's certificate for TURN, and no
  cloud-specific annotations, identities or key vault.
- **`hostAliases`** makes `<domain>` resolve to the ingress controller's ClusterIP inside
  Management's pod only.
- **The CA bundle** is mounted into `/etc/ssl/certs`, which Management's TLS reads in
  addition to the public CAs.

## 7. Install with the Terraform module

When the customer gives you the module, it does §5 (optionally), §6 and the secrets in
one apply. In its `envs/onprem` directory:

```bash
export KUBE_CONFIG_PATH=~/.kube/config         # the state backend's kubeconfig (oc login first)
cp terraform.tfvars.example terraform.tfvars   # then edit it with §2.1's answers
terraform init
terraform plan                                 # read it back to the customer before applying
terraform apply
terraform output -raw admin_password           # the first sign-in (changed at once)
terraform output dns_records                   # LoadBalancer mode: the A records
terraform output node_ports                    # NodePort mode: what the external load balancer forwards to
```

| Variable | Meaning |
|---|---|
| `domain`, `turn_domain`, `apps_domain` | §2.1; `turn_domain` defaults to `turn.<domain>` |
| `tls_cert_file`, `tls_key_file`, `apps_tls_*`, `ca_bundle_file` | §2.1 files |
| `admin_email`, `admin_first_name`, `admin_last_name`, `admin_password` | an empty password is generated and must be changed at the first sign-in |
| `service_type` | `LoadBalancer` or `NodePort` (§5.1) |
| `ingress_ip`, `turn_ip`, `metallb_addresses`, `install_metallb` | MetalLB; `metallb_addresses` creates the pool (with `autoAssign: false`); `install_metallb` installs MetalLB from its chart when the Operator is not used |
| `load_balancer_annotations` | annotations for another load-balancer implementation |
| `install_ingress_nginx`, `ingress_namespace` | the ingress controller |
| `postgres_mode` (`operator`/`external`), `install_cnpg_operator`, `postgres_*` | §6.4 |
| `redis_mode` (`in-cluster`/`external`), `redis_*` | §6.5 |
| `netzilo_charts_dir`, `upstream_charts_dir` | the two chart directories (§2.1); set both, so nothing is downloaded |
| `image_registry`, `image_pull_secret_file`, `netzilo_version`, `image_overrides` | §4; `terraform output -raw image_mirror_list` prints every source/target pair |
| `msp_key`, `pkg_base_url`, `l3_url`, `storage_class`, `namespace` | as in §6 |

The state is a Secret in the cluster's `default` namespace (`tfstate-default-netzilo-onprem`)
and holds every generated secret: protect it like `secrets.env`. A second `terraform plan`
right after the apply must say `No changes`; anything else is §10's "plan wants to change
the namespace" or a value the customer edited by hand.

## 8. Verify — every gate must pass

```bash
oc get pods -n "$NS" -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,SCC:.metadata.annotations.openshift\\.io/scc
```

Gate 1 — every pod `Running` (the two bootstrap Jobs `Succeeded`); the SCC column shows
`anyuid` for the dashboard only and `restricted-v2` for every other Netzilo pod.

Gate 2 — the addresses: `oc get svc -A | grep -E 'LoadBalancer|NodePort'` shows the
ingress and `net-gateway-service` on the domain's address and `coturn` on the TURN
address (LoadBalancer mode).

Gate 3 — from a machine outside the cluster, with the customer's CA when it is internal
(`--cacert ca.pem`):

| Check | Expect |
|---|---|
| `curl -sS https://<domain>/` | the dashboard's HTML |
| `curl -s -o /dev/null -w '%{http_code}' http://<domain>/` | `308` |
| `curl -sS https://<domain>/.well-known/openid-configuration` | JSON with `"issuer":"https://<domain>"` |
| `curl -s -o /dev/null -w '%{http_code}' https://<domain>/api/users` | `401` |
| `curl -s --http2 -X POST -H 'content-type: application/grpc' --data-binary '' -D - -o /dev/null https://<domain>/management.ManagementService/GetServerKey` | a `content-type: application/grpc` header |
| the same against `/signalexchange.SignalExchange/Send` | `application/grpc` |
| `curl -s -o /dev/null -w '%{http_code}' --http1.1 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' --max-time 5 https://<domain>/ws-proxy/management` (and `/ws-proxy/signal`) | `101` |
| `openssl s_client -connect <domain>:8443 -servername <domain>` | the customer's certificate, `Verify return code: 0` |
| `curl -s --proxy https://<domain>:8443 -o /dev/null -w '%{http_code}' http://example.com/` | `407` (the gateway wants a signed-in browser) |
| `openssl s_client -connect <turn_domain>:5349` | `Verify return code: 0` |
| `turnutils_uclient -y -c -n 3 -u self -w <TURN_PASSWORD> <turn_domain>` (and with `-t` for TCP; it ships in the coturn image) | `Total lost packets 0` |
| with published applications: `curl -s -o /dev/null -w '%{http_code}' https://x.<apps_domain>/` | `404` from the reverse proxy |

Gate 4 — sign in at `https://<domain>` as the administrator with `ADMIN_PASSWORD`;
Zitadel asks for a new password (and offers 2-factor setup, which can be skipped); the
dashboard opens on its onboarding. The tenant is Enterprise:
`oc -n netzilo exec netzilo-pg-1 -c postgres -- psql -U postgres -d netzilo -Atc "select subscription from tenants"`
prints `Enterprise` (with the customer's Postgres, run the same query there).

Gate 5 — enrol one device with a setup key (`05-client-install-and-deploy.md`): it shows
connected in Peers. A second device connects to the first.

Gate 6 — Zitadel's administrators are only Netzilo's service account and the
administrator: in Zitadel's console (`https://<domain>/ui/console`), Instance → Members.

Report with §11.

## 9. Day-2

### 9.1 Upgrade

Change `NETZILO_VERSION` (and the mirror), then re-run §6.7's `helm upgrade --install`
commands with the **same** values files (`$W`), or `terraform apply` with the new
`netzilo_version`. `net-zitadel` and both bootstrap releases upgrade the same way; the
bootstrap's re-run is a no-op. Never delete `netzilo-idp` or regenerate `secrets.env`:
a new masterkey makes Zitadel's data unreadable and new client IDs log every user out.

### 9.2 Certificate renewal

Replace the `netzilo-tls` (and `netzilo-apps-tls`) Secret with the new files, as in §6.2.
The ingress picks it up at once, the gateway within 30 seconds; restart TURN
(`oc -n netzilo rollout restart deploy/coturn`) so it loads the new one.

### 9.3 Backups

Back up both databases, `netzilo` and `zitadel` (CloudNativePG: its `Backup`/
`ScheduledBackup` to object storage, or `pg_dump` of each), **and** `secrets.env` (or the
Terraform state). A restore without the same `ZITADEL_MASTERKEY` and
`DATASTORE_KEY` cannot sign anyone in and cannot read encrypted columns.

### 9.4 Uninstall

`helm uninstall` each release in reverse order of §6, `oc delete cluster netzilo-pg -n
netzilo` (deletes the database volumes), then the namespace; or `terraform destroy`. Both
are destructive: get an explicit "yes" first.

## 10. Pitfalls and remedies

| Symptom (exact text where there is one) | Cause | Remedy |
|---|---|---|
| `pods "…" is forbidden: unable to validate against any security context constraint: … runAsUser: Invalid value: 65532 (or 10001, 999, 65534): must be in the ranges: [1000…]` | a fixed user ID reached the pod: the chart's default merged with your values, or the overlay was not passed | pass `values-openshift.yaml` before your own file; for upstream charts set the fields to `null` (Helm merges maps — leaving a key out keeps the default) |
| `… fsGroup: Invalid value: []int64{65532}` | the same, for `fsGroup` | the same |
| Signal or Management: `listen tcp :80: bind: permission denied`, CrashLoopBackOff | the overlay's sysctl is missing | pass `values-openshift.yaml`; `oc get deploy net-signal -o jsonpath='{.spec.template.spec.securityContext}'` must show `net.ipv4.ip_unprivileged_port_start` |
| Dashboard pod refused by SCC, or `nginx: [emerg] … Permission denied` | its service account lacks `anyuid` | §6.2's RoleBinding; the overlay sets `serviceAccountName: net-dashboard` |
| A LoadBalancer Service stays `<pending>`; event `AllocationFailed … can't change sharing key … address also in use by openshift-ingress/router-default` | the pool auto-assigned the address to another Service | `autoAssign: false` on the pool (§5.1); the other Service releases the address |
| The gateway's Service stays `<pending>` while the ingress has the address | the two Services do not share the key, or one uses `externalTrafficPolicy: Local` | same `metallb.io/allow-shared-ip` value and `Cluster` on both |
| Management: `OpenID Provider Configuration Discovery has failed`, `failed to get login events from zitadel … dial tcp <address>:443: i/o timeout`; dashboard sign-in loops; API answers `403` to a valid session | pods cannot reliably reach the load balancer's own address (hairpin) | `hostAliases` to the ingress ClusterIP (§6.7); check: `oc -n netzilo exec deploy/net-management -- cat /etc/hosts` |
| Management: `x509: certificate signed by unknown authority` | the certificate's CA is internal and not mounted | `CA_BUNDLE` (§6.2, §6.7's `extraVolumes`) |
| Management: `GOAWAY` or the WebSocket checks return `404`/`400` | ingress-nginx rejected or ignored the `configuration-snippet` | `allow-snippet-annotations: "true"` and `annotations-risk-level: Critical` (§6.3) |
| `admission webhook "validate.nginx.ingress.kubernetes.io" denied the request: … risky annotation` | the same | the same |
| PVC `Pending`; pod event `did not have enough free storage` | the StorageClass has less free capacity than requested (LVM-based classes may keep a spare) | a smaller `PG_SIZE`/Redis size, another class, or more capacity |
| `netzilo-zitadel-setup` fails: `Postgres at … does not answer` | the database is unreachable or the admin password is wrong | `oc logs job/netzilo-zitadel-setup -c database`; fix the connection values and re-run the `helm upgrade --install` |
| `netzilo-zitadel-setup`: `Zitadel's instance exists but neither netzilo-idp nor netzilo-zitadel-pat does` | the `zitadel` database holds an install whose bootstrap never finished (or another Netzilo's) | drop the `zitadel` database (or point at an empty server) and run §6.6 again |
| `netzilo-bootstrap`: `HTTP 401` or `Zitadel not ready after 900s` | the PAT expired (more than an hour between the two bootstrap phases) or Zitadel is not reachable at `zitadelURL` | uninstall `netzilo-bootstrap`, `net-zitadel` and `netzilo-zitadel-setup`, drop the `zitadel` database, run §6.6 again |
| `netzilo-bootstrap`: `could not delete the bootstrap user zitadel-admin` | Zitadel refused the delete | read the message; the Job fails rather than leave Zitadel's default administrator; re-run after fixing |
| Helm: `Error: INSTALLATION FAILED: … timed out waiting for the condition` on a Job | the hook Job failed or is still running | `oc logs job/<release>`; the Job's last log line names the step |
| `ErrImagePull … manifest unknown` | the image is not in the mirror, or the tag differs | `image_mirror_list` / §4; `NETZILO_VERSION` matches the mirrored tag |
| Alpine-based clients: `Name does not resolve` although `nslookup` shows the `A` record | the DNS server answers `NXDOMAIN` for `AAAA` | an empty `AAAA` answer (`NOERROR`) |
| TURN over UDP hangs behind an external load balancer; TCP works | the UDP virtual server does not return the relay's answers | pass responses back (§5.1) |
| Terraform: every `plan` wants to change `annotations` on the namespaces | an older module without `ignore_changes`; applying it strips OpenShift's `openshift.io/sa.scc.*` annotations and breaks pod admission | update the module; never apply that change |
| Terraform: a local chart's change is not deployed | Helm only re-renders a local chart when its version or values change | bump the chart's `version` |
| Second replica of Management or Signal: devices on different pods cannot connect to each other | sessions are kept per pod | one replica (§1) |
| Dashboard console: `WebSocket connection to 'ws://localhost:41336/ws' failed`; `/nb-auth` answers `404` in the ingress log | normal: the dashboard looks for a local client, and the sign-in callback is handled in the browser | nothing |
| Management warns `TrustedPeers are configured to default value` and `TrustedHTTPProxies and TrustedHTTPProxiesCount both are configured` | the same settings as every self-hosted install | nothing |

## 11. Reporting template

```text
Netzilo on OpenShift — <domain>
Path: Helm (§6) | Terraform (§7)       Version: <tag>      Registry: <public | mirror>
Exposure: LoadBalancer (<ingress address>, <TURN address>) | NodePort behind <LB>
Postgres: CloudNativePG (<instances>) | external <host>      Redis: in-cluster | external <host>
Gates: 1 pods/SCC ✔  2 addresses ✔  3 endpoints ✔  4 sign-in + Enterprise ✔  5 device ✔  6 IdP members ✔
DNS records: <domain> → …, <turn_domain> → …, *.<apps_domain> → …
Kept by the customer: secrets.env (or the Terraform state) — masterkey and keys inside
Open items: …
```
