---
id: '02'
title: Netzilo Server — Day-2 Operations Runbook
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 65125
sections:
- id: '1'
  title: Know which layout you are on
  chars: 2140
- id: '2'
  title: Service inventory and health
  chars: 4520
- id: '3'
  title: Start / stop / restart
  chars: 832
- id: '4'
  title: Upgrading
  chars: 12734
- id: '5'
  title: Configuration changes
  chars: 2332
- id: '6'
  title: Backup
  chars: 15758
- id: '7'
  title: Restore
  chars: 8686
- id: '8'
  title: TLS certificates
  chars: 2862
- id: '9'
  title: Changing the server domain
  chars: 965
- id: '10'
  title: Re-running the installer — DESTRUCTIVE
  chars: 1203
- id: '11'
  title: Firewall reference
  chars: 2516
- id: '12'
  title: Marketplace-specific items
  chars: 2828
- id: '13'
  title: Capacity and sizing
  chars: 880
- id: '14'
  title: Decommission
  chars: 566
- id: '15'
  title: Quick reference
  chars: 816
- id: '16'
  title: Answers to the architecture questions customers ask
  chars: 1918
- id: '17'
  title: Migrating the database engine
  chars: 1191
- id: '18'
  title: Keeping the geolocation database current
  chars: 620
- id: '19'
  title: Certificate noise that is not a fault
  chars: 662
---
# Netzilo Server — Day-2 Operations Runbook

**Audience:** an AI operator administering a customer's self-hosted **Netzilo Server**
(on-prem installer, AWS Marketplace AMI, or Azure Marketplace managed application).
This document covers everything after installation: inspecting, upgrading, backing up,
restoring, rotating certificates, tuning, and decommissioning.

Some procedures below (backup, restore, certificate switching, rollback) are not
provided as vendor scripts; they follow from the shipped configuration and should be
executed step by step as written. Several sections also point out hardening the shipped
configuration does not include (log rotation, Redis exposure, backups); raise these with
the customer proactively.

Before any destructive step (an upgrade §4, a restore §7, §9, §10, §14, §17, anything
with `down --volumes`, `rm`, or a re-run of the installer) you MUST pass the backup gate
(§6.3: a complete, checksum-verified backup less than an hour old), state exactly what
will be lost, and get the customer's explicit "yes". No passing gate, no destructive
step.

---

## 1. Know which layout you are on

There are two on-disk layouts. Determine the layout first; every command depends on it.

| Delivery path | Compose directory (`$C`) | State files | Extra services |
|---|---|---|---|
| **On-prem installer** (`curl … install-netzilo.sh \| sudo bash`) | `/opt/netzilo` | `/opt/netzilo/CREDENTIALS`, `/opt/netzilo/netzilo-state.env` | none |
| **AWS AMI / Azure image** | `/opt/netzilo/run` | `/opt/netzilo/CREDENTIALS`, `/opt/netzilo/netzilo-state.env`, `/opt/netzilo/metering.env`, `/opt/netzilo/.provisioned` | `netzilo-firstboot.service`, `netzilo-first-login.service`, `netzilo-metering.timer` |

Detect it:

```bash
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
echo "compose dir: $C"; ls -la "$C"
```

Every `docker compose` command in this document must be run from `$C` (or with
`-f $C/docker-compose.yml`). The public README's `cd /opt/netzilo && docker compose …`
only works on the on-prem layout; on marketplace images it fails with "no configuration
file provided".

Files in `$C` and what they hold:

| File | Purpose | Secrets inside |
|---|---|---|
| `docker-compose.yml` | 9 services, images, volumes, management env/command | Postgres admin password, `NETZILO_MSP_KEY`, `SUPPORT_WORKER_TOKEN` |
| `Caddyfile` | reverse proxy + TLS; all routes for dashboard, API, gRPC, Zitadel | — |
| `management.json` | management server config | `DataStoreEncryptionKey`, `InternalAPIToken`, IdP client secret, TURN password, `SupportConfig.WorkerToken` |
| `zitadel.env` | Zitadel runtime config | **`ZITADEL_MASTERKEY`** (irreplaceable), DB passwords |
| `dashboard.env` | dashboard runtime config (auth, package mirror) | `NETZILO_MSP_KEY` |
| `turnserver.conf` | coturn | TURN static credential |
| `.env` | plain-text copy of admin username/password | admin password |
| `machinekey/` | bootstrap service-account PAT (expired 30 min after install; harmless) | — |
| `certs/` | only in `provided`/`selfsigned` TLS modes: `fullchain.pem`, `privkey.pem` | private key |

Treat `$C` as a secrets directory (it is `root`-owned; keep it that way).

---

## 2. Service inventory and health

```bash
cd "$C" && sudo docker compose ps
```

Expected: 9 containers — `caddy`, `coturn`, `dashboard`, `management`, `signal`,
`zitadel`, `support-worker` (healthy), `postgres` (healthy), `redis` (healthy). Only
`db` (`postgres`), `redis` and `support-worker` report health — the first two from compose
healthchecks, the worker from the `HEALTHCHECK` in its image; the others show plain `Up`.

| Container | Image | Listens | Role |
|---|---|---|---|
| `caddy` | `caddy:latest` | host `80`, `443` | TLS termination, routes all HTTP/gRPC to the others |
| `dashboard` | `ghcr.io/netzilo/net-dashboard` | internal `:80` | admin UI |
| `management` | `ghcr.io/netzilo/net-management` | internal `:80` (HTTP API + gRPC, h2c) | control plane |
| `signal` | `ghcr.io/netzilo/net-signal` | internal `:10000` (gRPC h2c) | peer signaling |
| `zitadel` | `ghcr.io/netzilo/zitadel-build` | internal `:8080` | identity provider (OIDC) |
| `coturn` | `coturn/coturn:latest` | **host network**: `3478` tcp/udp, `5349` tcp/udp, relay `49152–65535/udp` | STUN/TURN relay |
| `postgres` | `postgres:16` | internal `5432` | databases `netzilo` (management) and `zitadel` |
| `redis` | `redis:latest` | **published on host `6379`, no password** | management store cache + Zitadel caches |
| `support-worker` | `ghcr.io/netzilo/net-support-worker` | internal `:8080`, **no ingress** | AI Assistant agent: management calls it with the shared token, it calls management back at `http://management:80`, and reaches the owner-configured AI provider outbound; stateless, runbooks baked into the image |

Redis on marketplace deploys is shielded by the cloud security group/NSG (6379 is not
opened there). On an on-prem host with no host firewall port 6379 is reachable
from the network; Docker-published ports bypass `ufw`. Fix: in `docker-compose.yml`
change `- "6379:6379"` to `- "127.0.0.1:6379:6379"` and `docker compose up -d redis`, or
block 6379 at the perimeter.

### 2.1 End-to-end health gates (run from anywhere that resolves the domain)

```bash
D=<domain>
curl -sS -o /dev/null -w "dashboard  -> HTTP %{http_code}\n" "https://$D/"
curl -sS -o /dev/null -w "oidc       -> HTTP %{http_code}\n" "https://$D/.well-known/openid-configuration"
curl -sS "https://$D/.well-known/openid-configuration" | grep -o '"issuer":"[^"]*"'
curl -sS "https://$D/" | grep -oiE '<title>[^<]*</title>'          # expect <title>Netzilo</title>
echo | openssl s_client -connect "$D:443" -servername "$D" 2>/dev/null | openssl x509 -noout -issuer -dates
curl -sS -o /dev/null -w "mgmt api   -> HTTP %{http_code}\n" "https://$D/api/users"   # 401 = alive, auth required
```

| Gate | Expected |
|---|---|
| dashboard | `200` |
| OIDC discovery | `200`, `"issuer":"https://<domain>"` |
| TLS | issuer Let's Encrypt (or your CA in `provided` mode); `notAfter` in the future |
| management API unauthenticated | `401` (proves Caddy → management path works) |
| `docker compose ps` | 9 Up, postgres+redis+support-worker healthy |

Zitadel health from the host (Caddy proxies `/debug/*` to Zitadel):

```bash
curl -sS -o /dev/null -w "zitadel healthz -> %{http_code}\n" "https://$D/debug/healthz"
curl -sS -o /dev/null -w "zitadel ready   -> %{http_code}\n" "https://$D/debug/ready"
```

### 2.2 Logs

```bash
cd "$C"
sudo docker compose logs --tail=200 management
sudo docker compose logs --tail=200 zitadel
sudo docker compose logs --tail=100 caddy
sudo docker compose logs --tail=100 signal coturn dashboard
sudo docker compose logs -f            # follow everything
```

Marketplace-image host logs: `/var/log/netzilo-firstboot.log`,
`journalctl -u netzilo-firstboot`, `journalctl -u netzilo-first-login`,
`/var/log/netzilo-metering.log`.

**No log rotation is configured.** Zitadel runs at `debug` log level and Caddy has
`debug` enabled; Docker's default json-file driver grows unbounded. Check
`sudo du -sh /var/lib/docker/containers/*/` periodically. Fix (safe, no data impact):
add to `/etc/docker/daemon.json`

```json
{ "log-driver": "json-file", "log-opts": { "max-size": "50m", "max-file": "5" } }
```

then `sudo systemctl restart docker && cd "$C" && sudo docker compose up -d`
(the daemon setting applies to containers created afterwards; `up -d --force-recreate`
applies it to the existing ones — this restarts the stack, ~1 minute of downtime).
Alternatively lower Zitadel verbosity: edit `ZITADEL_LOG_LEVEL=debug` → `info` in
`$C/zitadel.env` and `sudo docker compose up -d --force-recreate zitadel`.

---

## 3. Start / stop / restart

```bash
cd "$C"
sudo docker compose restart            # restart all (keeps containers; LE certs kept)
sudo docker compose restart management # one service
sudo docker compose stop               # stop everything (data kept)
sudo docker compose up -d              # start again
```

After a host reboot the stack comes back automatically (`restart: unless-stopped`, and
`always` for `zitadel` and `db`). Nothing needs to be run.

Avoid `docker compose down` unless needed: it removes containers. Data volumes survive
`down`, but Caddy's Let's Encrypt storage lives in the caddy container's **anonymous**
volume, so after `down` + `up` Caddy re-issues the certificate on the next
HTTPS request (usually fine; matters if you are near Let's Encrypt rate limits —
5 duplicate certificates per week).

---

## 4. Upgrading

**Read this whole section before pulling anything.** An upgrade is the one routine
operation that can lose data or cause an outage on a healthy server, and both are
avoidable. The rules that keep it safe are short: back up first, record what is running,
change one component at a time, verify before the next, and never let third-party images
float.

### 4.0 What an upgrade can and cannot avoid

The server is a single host. The component being replaced stops for the seconds it takes
Docker to swap the container and for the new version to start. Zero downtime for that one
component is not achievable; what **is** achievable is no data loss, no dropped tunnels,
and no impact on components you did not touch.

**Data is safe by construction, provided you never remove volumes.** Every piece of
state lives in a named volume or a bind-mounted file, and neither `docker compose up -d`
nor `docker compose down` touches them.

| State | Where it lives | Survives container recreate |
|---|---|---|
| Netzilo database (internal mode) | named volume `…netzilo_db_data` | yes |
| Management data | named volume `…netzilo_management` | yes |
| Identity provider certificates | named volume `…netzilo_zitadel_certs` | yes |
| Cache | named volume `…netzilo_redis_data` | yes, and disposable (§4.6) |
| `management.json`, `Caddyfile`, `turnserver.conf`, `machinekey/` | files next to the compose file | yes |

Compose prefixes each volume with the project name (`netzilo_` on-premises, `run_` on
images); `sudo docker volume ls | grep netzilo_` shows the real names.

The three things that **do** destroy data: `docker compose down -v` or `docker volume rm`,
re-running the installer (§10), and a database restore over a newer schema. Nothing in
this section does any of them.

**What users experience while each component restarts.** Restart only what you are
upgrading; everything else keeps running untouched.

| Component restarting | Effect while it is down | Effect on tunnels |
|---|---|---|
| management | Dashboard and API unavailable; no policy or peer updates delivered | none; established tunnels keep passing traffic |
| signal | New peer-to-peer connections cannot be negotiated | none for connections already up |
| dashboard | Web UI unavailable | none |
| zitadel | Logins fail; existing sessions continue until their tokens expire | none |
| coturn | Relayed sessions drop and re-establish once it is back | only relayed peers, briefly |
| redis | Management waits for the cache to report healthy, then rebuilds it from the database | none |
| db | Everything that depends on it waits | none |

Schedule management and zitadel restarts for a quiet period. Dashboard and signal can be
done any time.

### 4.1 Pre-flight, every time

Skip none of these. Each one exists because omitting it has caused a support case.

**1. Find the compose file and confirm the stack is healthy before you change it.** An
upgrade never fixes a stack that is already broken; it hides the cause.

```bash
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
cd "$C" && sudo docker compose ps
```

Every service `Up`, database and cache `healthy`. Then run the §2.1 gates. If anything
fails, stop and fix it first (`03-server-troubleshooting.md`).

**2. Record exactly what is running.** This is your rollback anchor. Tags such as
`latest` move; a digest does not.

```bash
STAMP=$(date -u +%Y%m%dT%H%MZ)
for s in management signal dashboard zitadel caddy coturn redis db; do
  id=$(sudo docker compose images -q "$s" 2>/dev/null)
  [ -n "$id" ] && printf "%-10s %s\n" "$s" "$(sudo docker image inspect --format '{{index .RepoDigests 0}}' "$id")"
done | sudo tee "/opt/netzilo/pre-upgrade-$STAMP.txt"
```

Keep that file. Rollback (§4.7) is "put these lines back".

**3. Back up, and pass the backup gate.** Run `sudo /usr/local/sbin/netzilo-backup.sh`
(§6.2); it must end with `BACKUP OK`. Then run the backup gate (§6.3). If either fails,
stop here: do not pull, do not recreate anything. On an external database also take a
provider snapshot; the migrations that a new management version runs at start happen on
that database too, and its account must be allowed to change the schema.

**4. Check disk space.** New images are pulled alongside the old ones.

```bash
df -h /var/lib/docker
```

Under a few gigabytes free, prune unused images first (§4.8), or the pull fails halfway.

**5. Know what `latest` means here.** On an on-premises install the four Netzilo images
are referenced by the moving tag `latest`, which advances only when Netzilo publishes a
new build. A pull that reports the image is already up to date means there is nothing
newer. That is a correct result, not a failure. On marketplace images every image is
pinned to a digest and a pull changes nothing until you edit the reference (§4.5).

### 4.2 Update one component

This is the procedure to use when asked to update management, the dashboard, signal or
the identity provider. Pull and recreate only the named service; leave everything else
alone.

```bash
S=management                      # or: signal | dashboard | zitadel
sudo docker compose pull "$S"
sudo docker compose up -d --no-deps "$S"
sudo docker compose logs -f --since 2m "$S"
```

`--no-deps` prevents Compose from touching the services this one depends on. Watch the log
until the start line appears, then verify.

| Component | Log line that means it is up | Verify |
|---|---|---|
| management | `management server version <v>` then `running HTTP server and gRPC server on the same port` | `curl -sS -o /dev/null -w '%{http_code}\n' https://<domain>/api/users` returns `401`; a client shows `Management: Connected` |
| zitadel | takes noticeably longer than the others; it runs its setup steps on every start | `curl -sS -o /dev/null -w '%{http_code}\n' https://<domain>/debug/ready` returns `200`; sign in to the dashboard |
| signal | `running signal server` | `docker compose ps signal` is `Up`; a client shows `Signal: Connected` |
| dashboard | container `Up` | `curl -sS -o /dev/null -w '%{http_code}\n' https://<domain>/` returns `200` and the page title is Netzilo |

**Management applies its schema migration during that start.** It is automatic and cannot
be switched off. A failure appears in the log as `auto migrate:` followed by the reason,
and the container will restart in a loop. Do not retry the pull; go to §4.7.

**The identity provider's migrations are forward-only.** Once zitadel has started cleanly
on a newer image, do not put the older image back. Roll back other components if needed
and leave zitadel where it is.

**Management and the dashboard should be updated together, in that order.** There is no
version check between them, so a mismatch fails silently as odd dashboard behaviour rather
than as an error. Update management, verify, then update the dashboard from the same
publish.

### 4.3 Update the whole Netzilo stack

Same procedure, one component at a time, in this order, verifying after each:

1. zitadel
2. management
3. dashboard
4. signal
5. support-worker

The identity provider goes first because everything authenticates through it. Signal and
the support worker go last because they are independent and stateless; a worker restart
only interrupts an Assistant turn that is in flight.

```bash
for S in zitadel management dashboard signal support-worker; do
  sudo docker compose pull "$S" && sudo docker compose up -d --no-deps "$S"
  echo "== $S recreated; verify before continuing =="; read -r
done
```

**Do not run a bare `docker compose pull` followed by `docker compose up -d` on an
on-premises host.** It also pulls the proxy, the relay and the cache at their upstream
`latest` tags and recreates any of them whose image moved. A major-version change in any
of those is an outage you did not intend. Pin them first (§4.6), or always name the
services you mean.

### 4.4 Pin what you verified

Once a component is verified, pin it to the digest now running so the next pull cannot
move it unintentionally, and so the compose file itself documents the known-good state.

```bash
S=management; IMG=ghcr.io/netzilo/net-management     # signal: net-signal, dashboard: net-dashboard, zitadel: zitadel-build
NEW=$(sudo docker image inspect --format '{{index .RepoDigests 0}}' "$(sudo docker compose images -q $S)")
BAK="docker-compose.yml.$(date -u +%Y%m%dT%H%MZ).bak"; sudo cp docker-compose.yml "$BAK"
sudo sed -E "s#^([[:space:]]*image:[[:space:]]*)${IMG//./\\.}[@:].*#\1$NEW#" "$BAK" | sudo tee docker-compose.yml >/dev/null
grep -n "$IMG" docker-compose.yml
```

`docker compose up -d` afterwards changes nothing, because the running container already
has that image. To move again later, set the reference back to the tag Netzilo names, or
to `latest`, and repeat §4.2. Keep pre-upgrade files and the pinned compose file together;
between them they describe every state the server has been in.

### 4.5 Marketplace images (AWS, Azure)

Every image in the baked compose file is pinned to a digest, including the database,
cache, proxy and relay. Pulling changes nothing until you change a reference.

1. Pre-flight (§4.1), including the digest record and the backup.
2. Edit the reference for the component you are updating from `<image>@sha256:…` to the
   tag Netzilo names for the release, or to `latest`.
3. Pull and recreate that one service (§4.2), verify, then pin it again (§4.4).

Leave the third-party image references exactly as they are.

### 4.6 Third-party images: proxy, relay, cache, database

These are not part of a Netzilo release and a Netzilo update should not move them.

- **On an on-premises install they float at upstream `latest`.** Before the first upgrade
  you perform, pin all three using §4.4 with the image names `caddy`, `coturn/coturn` and
  `redis`. From then on they move only when you decide.
- **The cache is disposable.** Management rebuilds it from the database at every start,
  logging `starting cache warmup` and `cache warmup completed`. If a cache image change
  ever leaves the cache container unable to start on its existing data, stopping it,
  removing its `…netzilo_redis_data` volume and starting it again loses nothing.
- **The database tag names its major version.** Never change it to a newer major as an
  upgrade step. A major version move is a dump, a new cluster and a restore (§6, §7), done
  as its own maintenance.
- **A proxy or relay major version can change configuration syntax.** The files they read
  are bind-mounted and not regenerated, so an incompatible version fails at start with a
  configuration error in its log. Roll the image back (§4.7); do not edit the
  configuration to chase a version you did not intend to run.

### 4.7 Rollback

Rollback is per component and uses the digest you recorded in §4.1.

```bash
S=management; IMG=ghcr.io/netzilo/net-management
OLD=$(grep "^$S " /opt/netzilo/pre-upgrade-<STAMP>.txt | awk '{print $2}')
BAK="docker-compose.yml.$(date -u +%Y%m%dT%H%MZ).bak"; sudo cp docker-compose.yml "$BAK"
sudo sed -E "s#^([[:space:]]*image:[[:space:]]*)${IMG//./\\.}[@:].*#\1$OLD#" "$BAK" | sudo tee docker-compose.yml >/dev/null
sudo docker compose up -d --no-deps "$S"
```

The previous image is still on the host, so this needs no network.

Two cases need more than that:

- **Management migrated the schema and the old version cannot read it.** Restore the
  database dump taken in pre-flight (§7.1) **and** the old image together. Restoring the
  image alone leaves it crash-looping on `auto migrate:`; restoring the dump alone leaves
  the new image re-applying the migration.
- **Zitadel started cleanly on the new image.** Leave it. Its migrations are forward-only
  and putting the old image back is what breaks logins.

The full failure walk-through is `03-server-troubleshooting.md` §8.

### 4.8 Clean up

Only after the rollback window has passed and you would not want the old image back:

```bash
sudo docker image prune -f
```

This removes images no container references. The digests in your pre-upgrade file remain
pullable from the registry if ever needed.

### 4.9 Things an upgrade does not do

- It does not change `management.json`, the `Caddyfile`, `turnserver.conf` or the
  identity provider's keys. They are files on the host and the new version reads them as
  they are. If a version needs a setting that is missing, it says so in its log at start.
- It does not require clients to be upgraded. There is no protocol version gate; clients
  keep working across a server upgrade (§16).
- It does not renew or reissue certificates, change the domain, or alter the plan.
- It is **not** achieved by re-running the installer. That wipes the server (§10).

---

## 5. Configuration changes

General rule: edit the file in `$C`, then recreate only the affected container:

```bash
cd "$C" && sudo docker compose up -d --force-recreate <service>
```

| Change | Edit | Recreate |
|---|---|---|
| Package/download mirror shown in the dashboard | `dashboard.env` → `NETZILO_PKG_BASE_URL=https://mirror.example.com` (must mirror the `/download/...` and `/debian/` layout) | `dashboard` |
| Management log level | `docker-compose.yml` management `command:` → `"--log-level", "debug"`; revert to `info` afterwards (`03-server-troubleshooting.md` §11) | `management` |
| Zitadel log level | `zitadel.env` → `ZITADEL_LOG_LEVEL=info` | `zitadel` |
| TURN relay port range | `turnserver.conf` `min-port`/`max-port` (and open the same UDP range) | `coturn` |
| TURN behind 1:1 NAT (cloud) | `turnserver.conf` add `external-ip=<public-ip>/<private-ip>` | `coturn` |
| Zitadel DB pool | `zitadel.env` `ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS` etc. | `zitadel` |
| Management DB pool | `docker-compose.yml` management env `NETBIRD_DB_MAX_OPEN_CONNS` (200) / `NETBIRD_DB_MAX_IDLE_CONNS` (100) | `management` |
| Bind Redis to loopback | `docker-compose.yml` redis `ports: - "127.0.0.1:6379:6379"` | `redis` |

**Do not** edit `management.json` OIDC/issuer fields, `zitadel.env` domain fields or
`Caddyfile` site names to "move" the server to a new domain — see §8.

The bundled Postgres has `max_connections=100`; Zitadel uses up to 20 and management up
to 200 configured — under heavy load management can exhaust connections. If
you see `too many clients already` in management logs, lower
`NETBIRD_DB_MAX_OPEN_CONNS` to 60 and `NETBIRD_DB_MAX_IDLE_CONNS` to 30, or raise
Postgres `max_connections` via `command: ["postgres", "-c", "max_connections=300"]` on
the `db` service (needs ~2× RAM headroom).

Management server startup flags in use (from `docker-compose.yml` `command:`):
`--port 80 --log-file console --log-level info --disable-anonymous-metrics=true
--single-account-mode-domain=netzilo.network --dns-domain=netzilo.network
--idp-sign-key-refresh-enabled --disable-single-account-mode --user-delete-from-idp`.
`--user-delete-from-idp` means deleting a user in the Netzilo dashboard also deletes the
Zitadel user. Tell customers this before they delete users they may want to keep in the IdP.

---

## 6. Backup

**Nothing in the product performs backups.** Set this up for every customer. A backup
**fails closed**: it either captures every artifact a restore needs and says so, or it
exits non-zero and is marked failed. A backup that is not marked complete is not a
backup; never proceed with a destructive operation on the strength of one.

### 6.1 What a restore needs

| Artifact | Required? | Why |
|---|---|---|
| `netzilo` database dump | **Required** | accounts, peers, groups, policies, routes, setup keys, users |
| `zitadel` database dump | **Required** | identities, passwords, OIDC applications, instance configuration |
| Database roles (`globals.sql`, bundled database) | **Required** | the identity provider's login role and its password |
| Management data volume (`/var/lib/netzilo` in the container) | **Required** | management data directory |
| `docker-compose.yml` | **Required** | image references, database admin password, `NETZILO_MSP_KEY`, worker token, `extra_hosts` |
| `management.json` | **Required** | `DataStoreEncryptionKey` (setup keys and tokens are encrypted with it), IdP client secret, TURN password, worker token |
| `zitadel.env` | **Required** | **`ZITADEL_MASTERKEY`** (without it the identity database is unreadable), database credentials |
| `dashboard.env`, `Caddyfile`, `turnserver.conf` | **Required** | dashboard, proxy and relay configuration; all bound to the domain |
| `certs/fullchain.pem`, `certs/privkey.pem` | **Required** in `provided`/`selfsigned` TLS mode | the certificate and key Caddy and coturn serve; not present in Let's Encrypt mode |
| `/opt/netzilo/netzilo-state.env` | **Required** in external-database mode; optional otherwise | install state; holds the external database connection details the backup uses |
| `/opt/netzilo/CREDENTIALS`, `$C/.env` | Optional | admin username and initial password; not needed to restore |
| `$C/machinekey/` | Optional | bootstrap token that expired 30 minutes after install |
| `/opt/netzilo/metering.env`, `/opt/netzilo/.provisioned` (images) | Optional | metering settings; `.provisioned` stops first boot from installing over a restored image host |
| Let's Encrypt certificates | Not captured | re-issued automatically on the first HTTPS request after restore |
| Redis | Not captured | a cache; rebuilt from the database at start |

Compose prefixes volume names with the project (directory) name, so the volumes appear
as `netzilo_netzilo_management` (on-premises) or `run_netzilo_management` (images). Find
the real names with `sudo docker volume ls | grep netzilo_`; the script below resolves
the management volume from the running container, so it does not depend on the name.

### 6.2 The backup script

Install it once (run as root). The heredoc is quoted, so nothing in it is expanded while
it is written:

```bash
sudo tee /usr/local/sbin/netzilo-backup.sh >/dev/null <<'EOF'
#!/usr/bin/env bash
# Netzilo Server backup. Fails closed: non-zero exit, a .FAILED directory, and no
# "complete=true" line unless every required artifact was captured and verified.
set -Eeuo pipefail
umask 077

ROOT=${NETZILO_BACKUP_ROOT:-/var/backups/netzilo}
STATE=/opt/netzilo/netzilo-state.env
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
TS=$(date -u +%Y%m%dT%H%M%SZ)
B="$ROOT/$TS"
install -d -m 700 "$ROOT" "$B"

fail() { echo "BACKUP FAILED: $*" >&2; exit 1; }
trap 'rc=$?; if [ "$rc" -ne 0 ]; then echo "exit $rc" > "$B/FAILED"; mv "$B" "$B.FAILED" 2>/dev/null || true; echo "BACKUP FAILED: $B.FAILED" >&2; fi' EXIT
st() { sed -n "s/^$1=//p" "$STATE" 2>/dev/null | head -n 1 || true; }

cd "$C"

# 1. Required configuration must exist and be non-empty.
REQUIRED="docker-compose.yml Caddyfile management.json zitadel.env dashboard.env turnserver.conf"
if grep -q 'auto_https off' Caddyfile; then REQUIRED="$REQUIRED certs/fullchain.pem certs/privkey.pem"; fi
for f in $REQUIRED; do [ -s "$C/$f" ] || fail "required file missing or empty: $C/$f"; done
MISSING_OPTIONAL=""
for f in "$C/.env" "$C/machinekey" /opt/netzilo/CREDENTIALS "$STATE" /opt/netzilo/metering.env /opt/netzilo/.provisioned; do
  [ -e "$f" ] || MISSING_OPTIONAL="$MISSING_OPTIONAL $f"
done

# 2. Database client: bundled container or external server.
if grep -q 'container_name: postgres' docker-compose.yml; then
  MODE=container
  PGU=$(sed -n 's/^[[:space:]]*- POSTGRES_USER=//p' docker-compose.yml | head -n 1); PGU=${PGU:-postgres}
  pgc() { docker exec -i -e PGUSER="$PGU" postgres "$@"; }
else
  MODE=external
  [ -s "$STATE" ] || fail "external database mode needs $STATE"
  PGIMG=$(st IMAGE_POSTGRES); PGIMG=${PGIMG:-postgres:16}
  export PGPASSWORD; PGPASSWORD=$(st DB_ADMIN_PASSWORD)
  [ -n "$PGPASSWORD" ] || fail "DB_ADMIN_PASSWORD not found in $STATE"
  pgc() { docker run --rm -i -e PGPASSWORD -e PGHOST="$(st DB_HOST)" -e PGPORT="$(st DB_PORT)" \
            -e PGUSER="$(st DB_ADMIN_USER)" -e PGSSLMODE="$(st DB_SSLMODE)" "$PGIMG" "$@"; }
fi
DB_VERSION=$(pgc psql -X -d postgres -tAc 'SHOW server_version')
PGDUMP_VERSION=$(pgc pg_dump --version)

# 3. Database dumps, each proven readable.
for db in netzilo zitadel; do
  pgc pg_dump -Fc -d "$db" > "$B/$db.dump"
  [ -s "$B/$db.dump" ] || fail "$db.dump is empty"
  pgc pg_restore --list < "$B/$db.dump" > /dev/null || fail "$db.dump is not a readable archive"
done
ZROLE=$(sed -n 's/^ZITADEL_DATABASE_POSTGRES_USER_USERNAME=//p' zitadel.env | head -n 1)
if [ "$MODE" = container ]; then
  pgc pg_dumpall --globals-only > "$B/globals.sql"
  grep -q "CREATE ROLE $ZROLE;" "$B/globals.sql" || fail "globals.sql does not contain role $ZROLE"
elif ! pgc pg_dumpall --globals-only --no-role-passwords > "$B/globals.sql" 2>/dev/null; then
  rm -f "$B/globals.sql"; MISSING_OPTIONAL="$MISSING_OPTIONAL globals.sql(external)"
fi

# 4. Management data volume, resolved from the container's mount.
MV=$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/var/lib/netzilo"}}{{.Name}}{{end}}{{end}}' management)
[ -n "$MV" ] || fail "cannot find the management data volume"
MP=$(docker volume inspect -f '{{.Mountpoint}}' "$MV")
tar -C "$MP" -czf "$B/management-data.tgz" .

# 5. Configuration and state: all of /opt/netzilo, then prove the required members are in it.
tar -C / -czf "$B/config.tgz" opt/netzilo
for f in $REQUIRED; do
  tar -tzf "$B/config.tgz" "${C#/}/$f" > /dev/null 2>&1 || fail "config.tgz lacks ${C#/}/$f"
done

# 6. What was running: service, image reference, registry digest, local image id.
SERVICES=$(docker compose config --services)
for s in $SERVICES; do
  cid=$(docker compose ps -a -q "$s")
  if [ -z "$cid" ]; then echo "$s not-created - -"; continue; fi
  iid=$(docker inspect -f '{{.Image}}' "$cid")
  echo "$s $(docker inspect -f '{{.Config.Image}}' "$cid") $(docker image inspect -f '{{if .RepoDigests}}{{index .RepoDigests 0}}{{else}}local-only{{end}}' "$iid") $iid"
done > "$B/images.txt"

# 7. Checksums, manifest, and the completeness flag written last.
cd "$B"
FILES="netzilo.dump zitadel.dump management-data.tgz config.tgz images.txt"
if [ -f globals.sql ]; then FILES="$FILES globals.sql"; fi
sha256sum $FILES > SHA256SUMS
{
  echo "format=netzilo-backup-1"
  echo "created_utc=$TS"
  echo "host=$(hostname)"
  echo "compose_dir=$C"
  echo "domain=$(st NETBIRD_DOMAIN)"
  if grep -q 'auto_https off' "$C/Caddyfile"; then echo "tls_mode=provided-or-selfsigned"; else echo "tls_mode=letsencrypt"; fi
  echo "db_mode=$MODE"
  echo "db_engine=postgresql"
  echo "db_server_version=$DB_VERSION"
  echo "pg_dump=$PGDUMP_VERSION"
  echo "management_volume=$MV"
  echo "optional_missing=${MISSING_OPTIONAL:- none}"
} > MANIFEST
sha256sum -c --quiet SHA256SUMS
echo "complete=true" >> MANIFEST
chmod 600 "$B"/*
echo "BACKUP OK: $B"
EOF
sudo chmod 700 /usr/local/sbin/netzilo-backup.sh
sudo /usr/local/sbin/netzilo-backup.sh      # first run by hand; it must end with "BACKUP OK"
```

A good backup directory holds `netzilo.dump`, `zitadel.dump`, `globals.sql` (bundled
database), `management-data.tgz`, `config.tgz`, `images.txt`, `SHA256SUMS` and a
`MANIFEST` whose **last line is `complete=true`**. `MANIFEST` records the time, domain,
TLS mode, database engine and server version, `pg_dump` version and any optional file
that was absent; `images.txt` records every service's image reference and digest.
Neither file contains secrets. Everything else in the directory does: it holds the
identity master key and every credential of the server. Keep it `root`-only (the script
creates it `0700`, files `0600`).

The two database dumps are each internally consistent but taken a few seconds apart.
For a strictly matched pair (before a major change), stop `management` and `zitadel`
for the duration of the backup and start them afterwards; this is a short outage for the
dashboard and logins, not for tunnels.

**External database** (`NETZILO_DB_MODE=external`, e.g. RDS or Azure Flexible Server):
the same script dumps both databases over the network using the connection details in
`netzilo-state.env`. Also take a snapshot with the cloud provider and write its
identifier next to the backup; the provider snapshot is the primary copy there. Managed
services usually refuse to export role passwords, so `globals.sql` is recorded as
optional in this mode; the identity provider's login role and its password are in
`zitadel.env` and must be recreated from there on a new server (§7.3).

### 6.3 Schedule, off-host copy, and the backup gate

Daily at 02:30, keeping 14 days. Old backups are pruned **only after a successful run**,
so a run of failures never deletes the last good backup:

```bash
sudo tee /etc/cron.d/netzilo-backup >/dev/null <<'EOF'
30 2 * * * root /usr/local/sbin/netzilo-backup.sh >>/var/log/netzilo-backup.log 2>&1 && find /var/backups/netzilo -mindepth 1 -maxdepth 1 -mtime +14 -exec rm -rf {} +
EOF
```

A failing cron job is silent. Have the customer's monitoring alert on the exit status or
on the log's last line not being `BACKUP OK`.

Copy each complete backup directory off the host to storage that is encrypted at rest and
restricted like the server itself, and verify the copy there with
`sha256sum -c SHA256SUMS`. A backup on the same disk as the server does not survive the
loss of the server.

**The backup gate.** Run this immediately before any destructive operation (upgrade §4,
restore §7, domain change §9, installer re-run §10, decommission §14, database engine
migration §17). It passes only for a complete, checksum-verified backup less than an hour
old:

```bash
L=$(sudo find /var/backups/netzilo -mindepth 1 -maxdepth 1 -type d ! -name '*.FAILED' | sort | tail -n 1)
if [ -n "$L" ] && [ "$(sudo tail -n 1 "$L/MANIFEST")" = complete=true ] \
   && sudo sh -c 'cd "$1" && sha256sum -c --quiet SHA256SUMS' _ "$L" \
   && [ -n "$(sudo find "$L" -maxdepth 0 -mmin -60)" ]; then
  echo "BACKUP GATE PASSED: $L"
else
  echo "BACKUP GATE FAILED: run /usr/local/sbin/netzilo-backup.sh and fix what it reports"
fi
```

If the gate fails, stop. Do not start the destructive step until a fresh run ends with
`BACKUP OK` and the gate passes.

### 6.4 Proving a backup restores

There are three levels of proof, and only the last one shows that the deployment can be
recovered.

1. **Readable.** The script checks every dump with `pg_restore --list` and every file
   against `SHA256SUMS`. This proves the archives are intact. It does **not** prove they
   restore, and it says nothing about the keys in the configuration.
2. **Data restores.** Restore both dumps into a throwaway database server that has no
   network and is deleted afterwards. This proves the dumps load without errors:

   ```bash
   sudo B=/var/backups/netzilo/<TS> bash -s <<'EOF'
   set -Eeuo pipefail
   cd "$B"
   [ "$(tail -n 1 MANIFEST)" = complete=true ] || { echo "REFUSING: not a complete backup"; exit 1; }
   sha256sum -c --quiet SHA256SUMS
   IMG=$(awk '$1=="db"{print $2}' images.txt); IMG=${IMG:-postgres:16}
   N=netzilo-restore-test
   docker rm -f "$N" >/dev/null 2>&1 || true
   trap 'docker rm -f "$N" >/dev/null 2>&1 || true' EXIT
   docker run -d --name "$N" --network none -e POSTGRES_HOST_AUTH_METHOD=trust "$IMG" >/dev/null
   for i in $(seq 1 60); do docker logs "$N" 2>&1 | grep -q 'init process complete' && break; sleep 2; done
   for i in $(seq 1 30); do docker exec "$N" pg_isready -U postgres -q && break; sleep 2; done
   docker exec "$N" pg_isready -U postgres -q
   if [ -f globals.sql ]; then
     grep -vx 'CREATE ROLE postgres;' globals.sql | docker exec -i "$N" psql -X -q -v ON_ERROR_STOP=1 -U postgres -d postgres
   fi
   docker exec -i "$N" pg_restore -U postgres --create --exit-on-error -d postgres < netzilo.dump
   docker exec -i "$N" pg_restore -U postgres --create --exit-on-error -d postgres < zitadel.dump
   for t in accounts users peers; do
     echo "$t: $(docker exec "$N" psql -X -U postgres -d netzilo -tAc "SELECT count(*) FROM $t")"
   done
   echo "DATA RESTORE TEST PASSED"
   EOF
   ```

   Compare the counts with the live server
   (`sudo docker exec postgres psql -U postgres -d netzilo -tAc "SELECT count(*) FROM peers"`);
   they should match as of the backup time.
3. **Deployment restores: the isolated restore rehearsal.** This is the requirement for
   calling a customer **disaster-recovery ready**. Do it once after the backup is set up,
   after any change of layout, TLS mode or database major version, and at least
   quarterly. Record the date, the backup used, the result and how long the restore took.

   1. Build a throwaway host of the same OS and size. Give it **no public DNS name** and a
      firewall that admits only the operator's address on `22` and `443`. No client
      and no part of the internet may reach it. Do not change the production DNS record.
   2. Copy one complete backup to it and follow §7.2 steps 2–5, with these changes to the
      rehearsal copy only, made before step 5 starts anything:
      - **Name resolution:** in `docker-compose.yml` set every `extra_hosts` entry for the
        domain to `'<domain>:172.20.0.1'` (instead of the address in §7.2 step 4) so the
        rehearsal stack talks to itself and never to production.
      - **Certificate:** Let's Encrypt cannot issue because the domain does not point
        here. Create a short-lived self-signed certificate, switch to provided mode
        (§8.3), and trust it on the host (the containers read the host's CA bundle):

        ```bash
        D=<domain>; sudo install -d -m 700 "$C/certs"
        sudo openssl req -x509 -newkey rsa:2048 -nodes -days 7 -subj "/CN=$D" \
          -addext "subjectAltName=DNS:$D" -keyout "$C/certs/privkey.pem" -out "$C/certs/fullchain.pem"
        sudo chmod 600 "$C/certs/privkey.pem"
        sudo cp "$C/certs/fullchain.pem" /usr/local/share/ca-certificates/netzilo-rehearsal.crt
        sudo update-ca-certificates
        ```
      - **Metering:** on a marketplace image run
        `sudo systemctl disable --now netzilo-metering.timer` before starting, so the
        rehearsal never reports usage.
   3. Start the stack and run the §2.1 gates from the operator's machine with
      `curl --resolve <domain>:443:<rehearsal-ip> --cacert fullchain.pem …`, then map the
      domain to the rehearsal address in that machine's hosts file and sign in.
   4. It passes only when all of these hold: every gate green; an admin signs in; the
      Zitadel log has no `unable to decrypt key` (the master key matches); peer, user,
      group and policy counts match the backup; and a setup key that existed before the
      backup is listed in the dashboard (the data encryption key matches).
   5. Destroy the rehearsal host and its disks, and remove the hosts-file entry. The
      host held every production secret.

---

## 7. Restore

Rules for every restore:

- Use only a backup whose `MANIFEST` ends with `complete=true` and whose `SHA256SUMS`
  verifies. The scripts below refuse anything else.
- Run the restore as one script with `set -Eeuo pipefail`: it stops at the first failing
  command and **never starts the stack after a failure**.
- Keep what you are replacing. The same-host restore renames the current databases
  instead of dropping them, so a failed restore can be undone.
- Tell the customer what will be lost (every change since the backup was taken) and get
  an explicit "yes" first.

### 7.1 Same host, data corruption or bad upgrade

Needs free disk space for a second copy of both databases (`df -h /var/lib/docker`).
After a bad upgrade, first put the old image references back in `docker-compose.yml`
(§4.7, without its final `up` line), then run the restore: its last step starts the
stack on whatever images the compose file names.

```bash
sudo B=/var/backups/netzilo/<TS> bash -s <<'EOF'
set -Eeuo pipefail
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
cd "$B"
[ "$(tail -n 1 MANIFEST)" = complete=true ] || { echo "REFUSING: $B is not a complete backup"; exit 1; }
sha256sum -c --quiet SHA256SUMS || { echo "REFUSING: checksum mismatch in $B"; exit 1; }
grep -qx 'db_mode=container' MANIFEST || { echo "REFUSING: external database; use 7.3"; exit 1; }
cd "$C"
PGU=$(sed -n 's/^[[:space:]]*- POSTGRES_USER=//p' docker-compose.yml | head -n 1); PGU=${PGU:-postgres}
OLD=prerestore_$(date -u +%Y%m%dT%H%M%SZ)
trap 'rc=$?; [ "$rc" -eq 0 ] || echo "RESTORE FAILED (exit $rc). Stack left STOPPED. Do not start it; follow the recovery steps in 7.1. Suffix: $OLD" >&2' EXIT
sql() { docker exec -i postgres psql -X -q -v ON_ERROR_STOP=1 -U "$PGU" -d postgres "$@"; }

docker compose stop $(docker compose config --services | grep -vxE 'db|redis')
docker compose up -d db redis
for i in $(seq 1 60); do docker exec postgres pg_isready -U "$PGU" -q && break; sleep 2; done
docker exec postgres pg_isready -U "$PGU" -q

sql -c "ALTER DATABASE netzilo RENAME TO netzilo_$OLD"
sql -c "ALTER DATABASE zitadel RENAME TO zitadel_$OLD"
docker exec -i postgres pg_restore -U "$PGU" --create --exit-on-error -d postgres < "$B/netzilo.dump"
docker exec -i postgres pg_restore -U "$PGU" --create --exit-on-error -d postgres < "$B/zitadel.dump"
docker compose exec -T redis redis-cli FLUSHALL        # the cache describes the replaced data
echo "RESTORED. Previous databases kept as netzilo_$OLD and zitadel_$OLD"
docker compose up -d
EOF
```

Then run the §2.1 gates and sign in. Once the customer confirms the restored state, drop
the kept copies to reclaim space:
`sudo docker exec postgres psql -U postgres -c 'DROP DATABASE netzilo_<suffix>' -c 'DROP DATABASE zitadel_<suffix>'`.

**Recovery when the script reports `RESTORE FAILED`.** The stack is stopped and the
original databases are intact under the `_<suffix>` names printed. Put back whichever
were renamed, then start:

```bash
cd "$C"
sudo docker exec postgres psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres \
  -c 'DROP DATABASE IF EXISTS netzilo' -c 'ALTER DATABASE netzilo_<suffix> RENAME TO netzilo'
sudo docker exec postgres psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres \
  -c 'DROP DATABASE IF EXISTS zitadel' -c 'ALTER DATABASE zitadel_<suffix> RENAME TO zitadel'
sudo docker compose up -d
```

Run only the lines for databases that were actually renamed (list them with
`sudo docker exec postgres psql -U postgres -lqt | cut -d'|' -f1`).

### 7.2 New host (disaster recovery)

Constraints that cannot be worked around:

- The **domain must be the same**. It is embedded in Zitadel's instance/OIDC config
  (in the DB), `management.json`, `Caddyfile`, `zitadel.env`, `dashboard.env`,
  `turnserver.conf`. Point the DNS `A` record at the new host.
- `ZITADEL_MASTERKEY` and `DataStoreEncryptionKey` must be the originals (they are in
  `config.tgz`).

Procedure:

1. Build the host (same OS, same or larger size) and install Docker
   (`docker-ce`, `docker-compose-plugin`). Open the firewall (§11). If the host is a new
   marketplace instance, its first boot has already installed an empty server: stop and
   remove it (`cd /opt/netzilo/run && sudo docker compose down --volumes`; it holds no
   data yet, but confirm that with the customer before running it).
2. Copy the backup directory to the host and verify it:
   `cd <backup> && [ "$(tail -n 1 MANIFEST)" = complete=true ] && sha256sum -c SHA256SUMS`.
   Stop if either check fails.
3. Restore the configuration: `sudo tar -C / -xzf config.tgz` (restores `/opt/netzilo`
   with all configuration, secrets and, on images, `.provisioned`). Then set `C` (§1).
4. Adjust for the new host, in `$C/docker-compose.yml`:
   - `extra_hosts` entries for the domain name the **old** host's address; change them
     to the new host's public address (or `172.20.0.1` when that address is private).
   - Pin every image to the digest recorded in `images.txt`, so the restore runs the
     versions the data was written by. Upgrade afterwards with §4.

     ```bash
     cd "$C"
     sudo cp docker-compose.yml "docker-compose.yml.$(date -u +%Y%m%dT%H%M%SZ).bak"
     while read -r s ref dig iid; do
       case "$dig" in *@sha256:*) ;; *) continue ;; esac
       sudo awk -v r="$ref" -v d="$dig" '$1=="image:" && $2==r { $0 = substr($0, 1, index($0, r) - 1) d } { print }' \
         docker-compose.yml | sudo tee docker-compose.yml.new >/dev/null
       sudo mv docker-compose.yml.new docker-compose.yml
     done < <backup>/images.txt
     grep -n 'image:' docker-compose.yml
     ```

     Air-gapped: `docker load` the same images first.
5. Restore the data, as one fail-stop script:

   ```bash
   sudo B=<backup> bash -s <<'EOF'
   set -Eeuo pipefail
   if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
   cd "$C"
   trap 'rc=$?; [ "$rc" -eq 0 ] || echo "RESTORE FAILED (exit $rc). Stack left STOPPED. Fix the cause, remove the volumes of this new install and start again from step 5." >&2' EXIT
   PGU=$(sed -n 's/^[[:space:]]*- POSTGRES_USER=//p' docker-compose.yml | head -n 1); PGU=${PGU:-postgres}
   sql() { docker exec -i postgres psql -X -q -v ON_ERROR_STOP=1 -U "$PGU" "$@"; }

   docker compose up -d db
   for i in $(seq 1 60); do docker exec postgres pg_isready -U "$PGU" -q && break; sleep 2; done
   docker exec postgres pg_isready -U "$PGU" -q
   # A new cluster holds only an empty "netzilo" database; refuse anything else.
   [ "$(sql -d netzilo -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")" = 0 ] \
     || { echo "REFUSING: the netzilo database on this host is not empty"; exit 1; }
   [ -z "$(sql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='zitadel'")" ] \
     || { echo "REFUSING: a zitadel database already exists on this host"; exit 1; }
   grep -vx "CREATE ROLE $PGU;" "$B/globals.sql" | sql -d postgres
   sql -d postgres -c 'DROP DATABASE netzilo'
   docker exec -i postgres pg_restore -U "$PGU" --create --exit-on-error -d postgres < "$B/netzilo.dump"
   docker exec -i postgres pg_restore -U "$PGU" --create --exit-on-error -d postgres < "$B/zitadel.dump"

   docker compose up --no-start --no-deps management
   MV=$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/var/lib/netzilo"}}{{.Name}}{{end}}{{end}}' management)
   [ -n "$MV" ] || { echo "cannot find the management data volume"; exit 1; }
   tar -C "$(docker volume inspect -f '{{.Mountpoint}}' "$MV")" -xzf "$B/management-data.tgz"
   echo "DATA RESTORED"
   docker compose up -d
   EOF
   ```
6. Run the §2.1 gates. Let's Encrypt re-issues on the first HTTPS request once DNS
   points here (allow ~60 s).
7. Existing clients reconnect automatically (same domain, same management identity).
   WireGuard keys are on the peers, not the server, so peer tunnels come back without
   re-enrolment.

**Do not re-run the installer to "recreate" a server** — see §10.

### 7.3 External database

Prefer the cloud provider's point-in-time restore of the two databases; it restores roles
and grants with them. To restore from the dumps instead, into an empty server: create
the identity provider's login role first, with the name and password from `zitadel.env`
(`ZITADEL_DATABASE_POSTGRES_USER_USERNAME` / `_PASSWORD`), then run
`pg_restore --create --exit-on-error -d postgres` for each dump with the connection
details from `netzilo-state.env`, and check each exit status before the next step. Restore
`config.tgz` and the management data volume as in §7.2, and start the stack only after
every step succeeded.

---

## 8. TLS certificates

Determine the mode: `grep -E "auto_https off|^\s*tls " "$C/Caddyfile"`.
No match → Let's Encrypt (automatic). `auto_https off` + `tls /data/caddy/certificates/…`
→ `provided` or `selfsigned`.

### 8.1 Let's Encrypt (default)

Fully automatic (Caddy renews at ~2/3 lifetime). Requirements that must stay true:
DNS `A` record → this host, inbound `80` and `443` open, outbound `443` to the internet.
Check: §2.1 TLS gate. If issuance keeps failing, `sudo docker compose logs caddy | grep -iE "acme|obtain|challenge|error"`.

Rate limits: 5 duplicate certs per domain per week. Repeated `docker compose down`/`up`
cycles can hit this (§3). If hit, wait a week or temporarily switch to `provided` mode
(§8.3) with a self-signed cert.

### 8.2 Rotating a provided certificate

Certificates are mounted from `$C/certs` (on-prem) or `/opt/netzilo/run/certs`
(images) into caddy at `/data/caddy/certificates/` and coturn at `/etc/coturn/certs/`.
Overwrite with the same file names — `fullchain.pem` (leaf + intermediates) and
`privkey.pem` — then:

```bash
cd "$C"
sudo openssl x509 -in certs/fullchain.pem -noout -subject -enddate
sudo openssl pkey -in certs/privkey.pem -pubout -outform DER | md5sum
sudo openssl x509 -in certs/fullchain.pem -pubkey -noout | openssl pkey -pubin -outform DER | md5sum   # must match
sudo docker exec caddy caddy reload --config /etc/caddy/Caddyfile
sudo docker compose restart coturn
```

Wildcard certificates (`*.example.com`) are fine and are required if the customer uses
tenant subdomains (the Caddyfile already includes a `*.<domain>:443` site block).

### 8.3 Switching Let's Encrypt → provided (or back)

1. Put `fullchain.pem` and `privkey.pem` into `$C/certs/` (mode 600, dir 700).
2. In `docker-compose.yml`, add to `caddy.volumes`: `- ./certs:/data/caddy/certificates/`
   and to `coturn.volumes`: `- ./certs:/etc/coturn/certs:ro`.
3. In `Caddyfile`: add `auto_https off` inside the global `{ … }` block, and add
   `tls /data/caddy/certificates/fullchain.pem /data/caddy/certificates/privkey.pem`
   as the first line inside **both** site blocks (`<domain>:443` and `*.<domain>:443`).
4. `sudo docker compose up -d --force-recreate caddy coturn`.

Reverse the edits to return to Let's Encrypt.

### 8.4 TURN over TLS

In Let's Encrypt mode no certificate is mounted into coturn, although
`turnserver.conf` references `/etc/coturn/certs/*.pem`. Effect: `turn:<domain>:3478`
(UDP) works; `turns:<domain>:5349` may fail TLS. Clients fall back between the two
relay URIs, so this is rarely user-visible. To fix, copy Caddy's current cert out and
mount it: `sudo docker cp caddy:/data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/<domain>/ ./certs-turn/`
then mount `./certs-turn` as `/etc/coturn/certs:ro` (rename to `fullchain.pem`/`privkey.pem`); repeat after each renewal (cron).

---

## 9. Changing the server domain

**Not supported in place.** The domain is baked into Zitadel's instance and OIDC apps
(database), `management.json`, `Caddyfile`, `zitadel.env`, `dashboard.env`,
`turnserver.conf`, `CREDENTIALS`, and on images `/etc/motd`. The only vendor-supported
path is a fresh installation under the new domain and re-enrolling peers.

If the customer insists on migrating, the honest answer is:

0. Take a backup of the old server and pass the backup gate (§6.3). Keep the old server
   running until the new one is verified.
1. Install a new server on the new domain (see `01-server-install.md`).
2. Recreate users (or connect the same external IdP), groups, policies, routes, DNS
   settings — the public API (`09-api-and-automation.md`) can export from the old server
   and import into the new one.
3. Re-enrol peers: `netzilo down && netzilo up --management-url https://<new-domain>`
   (or a new setup key for headless machines).

---

## 10. Re-running the installer — DESTRUCTIVE

The installer detects a previous installation **only by the presence of
`docker-compose.yml` or `zitadel.env` in its working directory**, and when it runs
non-interactively (the on-prem wrapper, AWS/Azure firstboot, or `NETZILO_ASSUME_YES=1`)
it **wipes the previous installation without asking**: `docker compose down -v`,
removes containers `caddy dashboard signal management coturn zitadel postgres redis`,
deletes the Netzilo volumes (`…netzilo_management`, `…netzilo_db_data`,
`…netzilo_redis_data`, `…netzilo_zitadel_certs`), and deletes all config files. **All users, peers, policies and
the admin account are lost.**

Therefore:

- Never re-run `install-netzilo.sh` / `install_netzilo.sh` on a working server to
  "repair" or "reconfigure" it.
- Never remove `/opt/netzilo/.provisioned` on a marketplace image and start
  `netzilo-firstboot.service` — same effect.
- If a re-install really is wanted (e.g. new domain), run the backup (§6.2), pass the
  backup gate (§6.3), copy that backup off the host, and get written confirmation. If the
  backup fails, do not re-install.

Reinstall on a clean host or after intentional teardown is fine.

---

## 11. Firewall reference

Inbound to the server. Management and signal are both served on 443 through Caddy; the
relay is coturn, on its own ports. coturn runs in host network mode, so a host firewall
(`ufw`, `firewalld`) applies to it as well as the cloud security group / NSG.

| Port | Proto | Status | Purpose and reason |
|---|---|---|---|
| 443 | TCP | **Required**, public | dashboard, API, management and signal gRPC, identity provider |
| 80 | TCP | **Required** with Let's Encrypt, public | ACME HTTP-01 validation and the redirect to HTTPS; with a provided certificate only the redirect uses it |
| 3478 | UDP | **Required**, public | STUN and TURN: the `stun:` and `turn:` addresses the server hands to every client |
| 49152–65535 | UDP | **Required for relayed connections**, public | coturn allocates each relayed session's address from this range and the other peer sends to it. A stateful firewall sometimes passes this traffic without the rule, because the relay's own outgoing packets open the flow, but that fails for peers behind symmetric NAT and when both peers are relayed; open it. The AWS and Azure templates do. If the range is changed in `turnserver.conf` (`min-port`/`max-port`), open the changed range |
| 5349 | TCP | **Required** for clients on networks that block UDP, public | TURN over TLS (`turns:…:5349?transport=tcp`), the fallback when UDP 3478 is blocked at a client site. It completes only when coturn has a certificate (§8.4) |
| 3478 | TCP | Optional | coturn listens, but the server advertises no TCP relay address on this port. The templates open it; closing it breaks nothing |
| 5349 | UDP | Optional | coturn listens (DTLS), but the server advertises no address that uses it. The templates open it; closing it breaks nothing |
| 22 | TCP | admin CIDR only | SSH |
| 6379 | TCP | **must not be public** | Redis |

Outbound: `443` to `ghcr.io`, Docker Hub, Let's Encrypt, `pkg.netzilo.com`
(dashboard download links are client-side; the server itself needs the registries), and —
for the AI Assistant — to the AI provider endpoint the owner connected, plus optionally
`github.com` for `support-worker` runbook refresh.

Clients need **no inbound** ports. They need outbound `443/tcp` to the server domain
(management and signal), outbound `3478/udp` to it (STUN/TURN), and outbound UDP (any)
for direct WireGuard. Without UDP they can still relay over TURN on `5349/tcp`, which
needs a certificate mounted into coturn (§8.4). The self-hosted relay is not on 443.

---

## 12. Marketplace-specific items

### 12.1 Where the admin credentials are

- All paths: `sudo cat /opt/netzilo/CREDENTIALS` (URL, username, password) — also shown
  in `/etc/motd` at SSH login on images.
- AWS: SSM SecureString `/netzilo/<stack-name>/admin-credentials`:
  `aws ssm get-parameter --with-decryption --name /netzilo/<stack>/admin-credentials --query Parameter.Value --output text`.
- Azure: the admin password was a required wizard input; nothing is published back.

### 12.2 Enterprise subscription activation

After the first dashboard login, `netzilo-first-login.service` (images) sets the tenant
to `Enterprise` (`UPDATE tenants SET subscription='Enterprise' …`) and disables itself.
On-prem installs have no such service; the on-prem stack runs in MSP mode instead
(`NETZILO_MSP_KEY` set in management and dashboard env), which the installer describes
as "Enterprise (unlimited users/peers, all features, no plans/billing UI)". If a
customer's on-prem dashboard shows plan limits or billing prompts, verify
`grep NETZILO_MSP_KEY "$C/docker-compose.yml" "$C/dashboard.env"` shows a non-empty value
in both; if not, contact support@netzilo.com.

Check the tenant row (read-only, safe):

```bash
docker exec postgres psql -U postgres -d netzilo -c "SELECT account_id, subscription, subscription_id FROM tenants;"
```

### 12.3 Metering (billing) — AWS/Azure only

Hourly `netzilo-metering.timer` runs `/opt/netzilo/metering.sh`, which counts
`SELECT COUNT(*) FROM users WHERE is_service_user=false` in the `netzilo` DB and
reports dimension `users` to AWS Marketplace Metering (`meter-usage`, product code
auto-detected from instance identity) or Azure Marketplace `usageEvent` (resource URI
auto-detected from the managed resource group's `managedBy`; plan `enterprise`).

```bash
sudo cat /opt/netzilo/metering.env             # METERING_ENABLED=1, CLOUD=aws|azure, DIMENSION=users
systemctl list-timers netzilo-metering.timer
sudo tail -n 50 /var/log/netzilo-metering.log  # look for "reported N to AWS/Azure"
sudo systemctl start netzilo-metering.service  # run now
```

Failure semantics: DB unreadable → service fails (retries next hour); API error →
`WARN … will retry next hour`. Do not disable metering on a pay-as-you-go listing —
it is the customer's contractual billing. On a contract (BYOL-style) listing
`METERING_ENABLED=0` is expected.

Billing count = named human users. Service users (API-only) are not billed.

### 12.4 Cloud NAT and TURN

Both cloud images sit behind 1:1 NAT (Elastic IP / Azure Public IP) but coturn is not
given `external-ip`. Relayed connections generally still work because both peers reach
the relay by its public address; if relayed peers cannot pass traffic, add
`external-ip=<public-ip>/<private-ip>` to `turnserver.conf` and
`docker compose restart coturn`.

---

## 13. Capacity and sizing

| | Minimum | Recommended |
|---|---|---|
| CPU / RAM | 2 vCPU / 4 GB | 2 vCPU / 8 GB (`t3.large`, `Standard_D2s_v5`) |
| Disk | 40 GB (images ship 30 GB root) | 40 GB SSD + monitor `/var/lib/docker` |
| Peers | "up to a few hundred" on the base size | scale to 4 vCPU / 16 GB (`t3.xlarge`, `Standard_D4s_v5`) beyond that |

Check disk: `df -h / && sudo du -sh /var/lib/docker/volumes/*netzilo_* /var/lib/docker/containers`.
Postgres and container logs are the growth drivers.

External Postgres (`NETZILO_DB_MODE=external`) is a first-install decision; migrating a
container DB to a managed DB later = §6 backup and backup gate → restore into the managed instance (§7.3) →
update DSNs in `docker-compose.yml` (management `NETBIRD_STORE_ENGINE_POSTGRES_DSN`) and
`zitadel.env` (`ZITADEL_DATABASE_POSTGRES_*`) → remove the `db` service → `up -d`.

---

## 14. Decommission

```bash
cd "$C"
sudo docker compose down --volumes
sudo rm -rf /opt/netzilo
# images only:
sudo systemctl disable --now netzilo-metering.timer netzilo-first-login.service 2>/dev/null
```

This deletes all data. Unless the customer has stated in writing that nothing is to be
kept, run the backup (§6.2), pass the backup gate (§6.3) and copy the backup off the host
first.
On AWS/Azure, deleting the stack / managed application removes the VM, but also stop
metering first if the listing is metered and the customer is terminating service.

---

## 15. Quick reference

```bash
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo )
cd "$C"
sudo docker compose ps                         # health
sudo docker compose logs --tail=200 management # logs
sudo /usr/local/sbin/netzilo-backup.sh         # backup (§6.2); must end "BACKUP OK"
# backup gate before anything destructive: §6.3
S=management; sudo docker compose pull "$S" && sudo docker compose up -d --no-deps "$S"   # upgrade one component (§4.2)
sudo test -s /opt/netzilo/CREDENTIALS && echo "admin login: /opt/netzilo/CREDENTIALS"   # read it only when handing over
```

Never: re-run the installer on a live server; change the domain in place; `down --volumes`
or any other destructive step without a passing backup gate (§6.3) and explicit customer
consent.

## 16. Answers to the architecture questions customers ask

**There is no high availability for the server.** Every delivery path builds a single
host running one database, one identity provider instance with one master key, and one
relay. There is no supported multi-node, clustered or load-balanced configuration.
Resilience comes from backup and restore to a new host, not from live failover. Say this
directly: the question is asked in most enterprise reviews and a vague answer invites a
follow-up. Routing-peer high availability is a different feature and is well supported.

**Kubernetes is not a customer deployment target.** The three shipped paths are the
on-premises installer, the AWS image and the Azure image. There is no published chart.
Clients can of course run in Kubernetes; the server cannot.

**Relay bandwidth is not capped.** The relay ships without per-session or per-user
bandwidth limits, so throughput is bounded only by the host's network and processor.
There is no setting to tune. Size the host for the expected relayed load.

**Clients do not have to be upgraded with the server.** There is no enforced protocol
version gate between client and server. The only thing that blocks an older client is a
minimum-version posture check the customer configured themselves.

**On marketplace images every container image is pinned to a digest**, including the
database, cache, proxy and relay, not only the Netzilo images. Seeing a digest instead of
a tag is expected and is not a sign of tampering. Pulling does not upgrade a
digest-pinned image; the reference has to be changed.

**Marketplace-metered deployments need outbound access to their marketplace metering
endpoint** in addition to the general outbound list. In an egress-restricted network,
metering fails quietly and retries hourly. The product keeps working; billing records do
not accumulate. Add the endpoint to the allow list.

## 17. Migrating the database engine

Moving between the embedded file store, the single-file database and an external
PostgreSQL server is a supported operation with its own command, not something to do by
copying files.

Approach it in this order:

1. **Back up first and pass the backup gate** (§6.2, §6.3). The migration is not
   reversible by simply pointing the configuration back.
2. **Stop accepting changes.** Run it in a maintenance window; a migration under load can
   leave the source and destination inconsistent.
3. **Use the management binary's own migration command** inside the container to move
   between the embedded store and the single-file database. It supports both directions,
   which is your rollback.
4. **Moving to external PostgreSQL** is a data-transfer step followed by pointing the
   connection string at the new server. Constraint violations during transfer come from
   orphaned rows in the source and must be cleaned before the transfer, not after.
5. **Verify before removing the old store**: sign in, list peers, confirm counts match,
   and make one change that writes to the database.

Keep the old store until the new one has run for a full day.

## 18. Keeping the geolocation database current

Geolocation posture checks and the location shown on peers rely on a database that is not
updated automatically. It is refreshed roughly twice a week upstream, and a server that
never updates it will gradually misplace addresses.

The refresh is a download, a copy into the running container, and a restart. On a server
with no outbound access, download on a connected machine and transfer the files. The
initial-setup symptom, where the database is missing entirely and geolocation endpoints
return a precondition failure, is covered in `03-server-troubleshooting.md`.

## 19. Certificate noise that is not a fault

On a default installation using automatic certificates, the proxy also attempts a
certificate for the wildcard form of the domain. That attempt cannot succeed with the
validation method in use, so the logs carry repeated failures for the wildcard name.

This is expected and harmless. The certificate for the actual domain is issued
separately and works. Do not treat these entries as a certificate incident, and do not
start deleting certificate state because of them. They matter only if the customer
genuinely needs a wildcard certificate, which requires supplying one rather than having
it issued automatically.
