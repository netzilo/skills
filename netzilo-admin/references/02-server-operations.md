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

Before any destructive step (§9, §10, anything with `down --volumes`, `rm`, or a
re-run of the installer) you MUST state exactly what will be lost and get the
customer's explicit "yes".

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
| `docker-compose.yml` | 8 services, images, volumes, management env/command | Postgres admin password, `NETZILO_MSP_KEY` |
| `Caddyfile` | reverse proxy + TLS; all routes for dashboard, API, gRPC, Zitadel | — |
| `management.json` | management server config | `DataStoreEncryptionKey`, `InternalAPIToken`, IdP client secret, TURN password |
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

Expected: 8 containers — `caddy`, `coturn`, `dashboard`, `management`, `signal`,
`zitadel`, `postgres` (healthy), `redis` (healthy). Only `db` (`postgres`) and `redis`
have compose healthchecks; the others show plain `Up`.

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
| `docker compose ps` | 8 Up, postgres+redis healthy |

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

### 4.1 On-prem installer hosts (images tagged `:latest`)

```bash
cd /opt/netzilo
sudo docker compose pull
sudo docker compose up -d
sudo docker compose ps
```

`pull` fetches the current `:latest` of `net-management`, `net-signal`,
`net-dashboard`, `zitadel-build`, plus `caddy`, `coturn`, `redis`. Management applies
its own DB migrations on start; Zitadel applies its own on `start`. Then run the §2.1
gates and confirm a client can still log in (`netzilo status` on any peer shows
`Management: Connected`).

### 4.2 AWS AMI / Azure image hosts (images pinned by digest)

The baked `docker-compose.yml` references images as `<image>@sha256:<digest>`.
**`docker compose pull` will not upgrade anything** — it re-pulls the same digest.
To upgrade:

1. Back up first (§6).
2. Edit `/opt/netzilo/run/docker-compose.yml`: replace each Netzilo image reference
   (`image: ghcr.io/netzilo/net-management@sha256:…`) with the target tag, e.g.
   `image: ghcr.io/netzilo/net-management:latest` (or a specific version tag supplied by
   Netzilo). Do the same for `net-signal`,
   `net-dashboard`, `zitadel-build`. Leave `postgres:16` alone.
3. `cd /opt/netzilo/run && sudo docker compose pull && sudo docker compose up -d`.
4. Run the §2.1 gates.

Note the digest you replaced (keep a copy of the old compose file) so you can roll back.

### 4.3 Rollback

Rollback = restore the previous `image:` lines (tag or digest) and `docker compose up -d`.
There is no schema-downgrade tooling; if the new management version migrated the DB and
the old version cannot read it, restore the Postgres dump taken before the upgrade (§7).
Previously pulled images remain in the local daemon (`sudo docker image ls`).

### 4.4 Upgrading Postgres major version

Not scripted. The stack pins `postgres:16`; do not change the tag to a newer major
without a `pg_dumpall` → new cluster → restore cycle (§6/§7).

---

## 5. Configuration changes

General rule: edit the file in `$C`, then recreate only the affected container:

```bash
cd "$C" && sudo docker compose up -d --force-recreate <service>
```

| Change | Edit | Recreate |
|---|---|---|
| Package/download mirror shown in the dashboard | `dashboard.env` → `NETZILO_PKG_BASE_URL=https://mirror.example.com` (must mirror the `/download/...` and `/debian/` layout) | `dashboard` |
| Management log level | `docker-compose.yml` management `command:` → `"--log-level", "debug"` | `management` |
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

**Nothing in the product performs backups.** Set this up for every customer.

What must be captured together (a restore needs all of it):

| Item | Why |
|---|---|
| Postgres databases `netzilo` and `zitadel` | all accounts, peers, policies, users, identities |
| Docker volume `netzilo_management` (`/var/lib/netzilo` in the container) | management data dir (geo DBs, misc) |
| The whole `$C` directory | `ZITADEL_MASTERKEY` (without it the Zitadel DB is unreadable), `DataStoreEncryptionKey` (setup keys / PATs are encrypted with it), IdP secrets, TURN password, Caddyfile, certs |
| `/opt/netzilo/CREDENTIALS`, `/opt/netzilo/netzilo-state.env`, `/opt/netzilo/metering.env` (images) | admin credentials, state used by first-login and metering |

Redis is a cache; it does not need backing up.

Backup script (container-DB mode; run as root; keep the output somewhere off-host):

```bash
set -e
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo )
TS=$(date -u +%Y%m%dT%H%M%SZ); B=/var/backups/netzilo/$TS; mkdir -p "$B"; chmod 700 "$B"
docker exec postgres pg_dump -U postgres -Fc netzilo  > "$B/netzilo.dump"
docker exec postgres pg_dump -U postgres -Fc zitadel  > "$B/zitadel.dump"
docker exec postgres pg_dumpall -U postgres --globals-only > "$B/globals.sql"
docker run --rm -v netzilo_management:/from -v "$B":/to alpine tar czf /to/netzilo_management.tgz -C /from .
tar czf "$B/config.tgz" -C / "${C#/}" opt/netzilo/CREDENTIALS opt/netzilo/netzilo-state.env 2>/dev/null || true
ls -la "$B"
```

If the Postgres admin user is not `postgres`, read it from `$C/docker-compose.yml`
(`POSTGRES_USER`) or `/opt/netzilo/netzilo-state.env` (`DB_ADMIN_USER`,
`DB_ADMIN_PASSWORD`).

External-DB mode (`NETZILO_DB_MODE=external`, e.g. RDS / Azure Flexible Server): use the
cloud provider's snapshots for the two databases, and still back up `$C`:

```bash
. /opt/netzilo/netzilo-state.env
docker run --rm -e PGPASSWORD="$DB_ADMIN_PASSWORD" postgres:16 \
  pg_dump "host=$DB_HOST port=$DB_PORT user=$DB_ADMIN_USER dbname=netzilo sslmode=$DB_SSLMODE" -Fc > netzilo.dump
```

Schedule it (daily at 02:30, keep 14 days):

```bash
sudo tee /etc/cron.d/netzilo-backup >/dev/null <<'EOF'
30 2 * * * root /usr/local/sbin/netzilo-backup.sh >/var/log/netzilo-backup.log 2>&1 && find /var/backups/netzilo -maxdepth 1 -mtime +14 -exec rm -rf {} +
EOF
```

Verify a dump is restorable at least once: `pg_restore --list netzilo.dump | head`.

---

## 7. Restore

### 7.1 Same host, data corruption or bad upgrade

```bash
cd "$C"
sudo docker compose stop management zitadel signal dashboard caddy
sudo docker compose up -d db
# drop & recreate, then restore
docker exec postgres psql -U postgres -c "DROP DATABASE netzilo;"  -c "CREATE DATABASE netzilo;"
docker exec postgres psql -U postgres -c "DROP DATABASE zitadel;"  -c "CREATE DATABASE zitadel;"
docker exec -i postgres pg_restore -U postgres -d netzilo < /var/backups/netzilo/<TS>/netzilo.dump
docker exec -i postgres pg_restore -U postgres -d zitadel < /var/backups/netzilo/<TS>/zitadel.dump
sudo docker compose up -d
```

The `zitadel` role must exist and own its objects (it does if the cluster is the
original one; on a fresh cluster restore `globals.sql` first:
`docker exec -i postgres psql -U postgres < globals.sql`).

### 7.2 New host (disaster recovery)

Constraints that cannot be worked around:

- The **domain must be the same**. It is embedded in Zitadel's instance/OIDC config
  (in the DB), `management.json`, `Caddyfile`, `zitadel.env`, `dashboard.env`,
  `turnserver.conf`. Point the DNS `A` record at the new host.
- `ZITADEL_MASTERKEY` and `DataStoreEncryptionKey` must be the originals (they are in
  the `config.tgz` from §6).

Procedure:

1. Install Docker on the new host (same as the wrapper does: `docker-ce`,
   `docker-compose-plugin`).
2. Recreate the layout: `sudo mkdir -p /opt/netzilo && sudo tar xzf config.tgz -C /`
   (this restores `$C` with all config and secrets).
3. Create the volumes and restore data:
   ```bash
   cd "$C"
   sudo docker compose up -d db && sleep 15
   sudo docker exec -i postgres psql -U postgres < globals.sql
   sudo docker exec postgres psql -U postgres -c "CREATE DATABASE netzilo;" -c "CREATE DATABASE zitadel;"
   sudo docker exec -i postgres pg_restore -U postgres -d netzilo < netzilo.dump
   sudo docker exec -i postgres pg_restore -U postgres -d zitadel < zitadel.dump
   sudo docker volume create netzilo_management
   sudo docker run --rm -v netzilo_management:/to -v "$PWD":/from alpine tar xzf /from/netzilo_management.tgz -C /to
   sudo docker compose up -d
   ```
4. Open the firewall ports (§11), then run the §2.1 gates. Let's Encrypt re-issues on
   the first HTTPS request (allow ~60 s).
5. Existing clients reconnect automatically (same domain, same management identity).
   WireGuard keys are on the peers, not the server, so peer tunnels come back without
   re-enrolment.

**Do not re-run the installer to "recreate" a server** — see §9.

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
deletes volumes `netzilo_management netzilo_db_data netzilo_redis_data
netzilo_zitadel_certs`, and deletes all config files. **All users, peers, policies and
the admin account are lost.**

Therefore:

- Never re-run `install-netzilo.sh` / `install_netzilo.sh` on a working server to
  "repair" or "reconfigure" it.
- Never remove `/opt/netzilo/.provisioned` on a marketplace image and start
  `netzilo-firstboot.service` — same effect.
- If a re-install really is wanted (e.g. new domain), take the §6 backup first and get
  written confirmation.

Reinstall on a clean host or after intentional teardown is fine.

---

## 11. Firewall reference

Inbound to the server:

| Port | Proto | Purpose | Exposure |
|---|---|---|---|
| 22 | TCP | SSH | admin CIDR only |
| 80 | TCP | ACME HTTP-01 + redirect | public |
| 443 | TCP | dashboard, API, gRPC, OIDC, signal | public |
| 3478 | TCP+UDP | STUN/TURN | public |
| 5349 | TCP+UDP | TURN over TLS | public |
| 49152–65535 | UDP | TURN relay allocations | public (opened by the AWS/Azure templates; needed for relayed peers behind symmetric NAT) |
| 6379 | TCP | Redis | **must not be public** |

Outbound: `443` to `ghcr.io`, Docker Hub, Let's Encrypt, `pkg.netzilo.com`
(dashboard download links are client-side; the server itself needs the registries).

Clients need **no inbound** ports. They need outbound `443/tcp` to the server domain,
and outbound UDP (any) for direct WireGuard; without UDP they still work via TURN over
`5349/tcp`.

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

Check disk: `df -h / && sudo du -sh /var/lib/docker/volumes/netzilo_* /var/lib/docker/containers`.
Postgres and container logs are the growth drivers.

External Postgres (`NETZILO_DB_MODE=external`) is a first-install decision; migrating a
container DB to a managed DB later = §6 dump → restore into the managed instance →
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

This deletes all data. Take a §6 backup first if there is any chance it is wanted later.
On AWS/Azure, deleting the stack / managed application removes the VM, but also stop
metering first if the listing is metered and the customer is terminating service.

---

## 15. Quick reference

```bash
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo )
cd "$C"
sudo docker compose ps                         # health
sudo docker compose logs --tail=200 management # logs
sudo docker compose pull && sudo docker compose up -d   # upgrade (on-prem :latest only)
sudo cat /opt/netzilo/CREDENTIALS              # admin login
docker exec postgres pg_dump -U postgres -Fc netzilo > netzilo.dump   # backup mgmt DB
docker exec postgres pg_dump -U postgres -Fc zitadel > zitadel.dump   # backup IdP DB
```

Never: re-run the installer on a live server; change the domain in place; `down --volumes`
without a verified backup and explicit customer consent.

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

1. **Back up first**, both the data directory and the volumes. The migration is not
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
