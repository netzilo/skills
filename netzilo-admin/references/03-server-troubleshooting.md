# Netzilo Server — Troubleshooting Runbook

**Audience:** an AI operator diagnosing a self-hosted Netzilo Server (on-prem installer,
AWS AMI, or Azure image). Symptom → evidence → cause → fix. Message strings are quoted
exactly as they appear in the logs. Do not restart Postgres, wipe volumes, or re-run the installer as a "fix" unless the
evidence points there and the customer has consented (see `02-server-operations.md` §10).

**You need shell access to the server for almost everything here.** If you do not have
it, ask for it before guessing — SSH, or AWS Systems Manager Session Manager
(`aws ssm start-session --target <instance-id>`) on an AWS deployment, or Serial
Console / Bastion on Azure. Start read-only, announce state-changing commands before
running them, and do not open the configuration files that hold secrets
(`management.json`, `zitadel.env`, `dashboard.env`, `.env`, `CREDENTIALS`). If access
cannot be granted, send the customer the copy-paste blocks in
`12-escalation-package.md` §8 and work from their output.

To read a management or signal log without a known symptom — healthy start-up order,
steady-state families such as `NOOP` and `FILTER_DIAG`, which `WARN`/`ERRO` lines are
benign, what `debug`/`trace` add — use `13-log-interpretation.md` §5.

Standard first pass (on the server):

```bash
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo ); cd "$C"
sudo docker compose ps
sudo docker compose logs --tail=100 management | tail -n 60
sudo docker compose logs --tail=100 zitadel     | grep -iE "error|fatal|warn" | tail -n 30
sudo docker compose logs --tail=60  caddy
df -h /; free -h; uptime
D=$(grep -oE '^[^*].*:443' Caddyfile | head -1 | sed 's/:443//'); echo "domain=$D"
curl -sS -o /dev/null -w "dashboard %{http_code}\n" https://$D/
curl -sS -o /dev/null -w "oidc %{http_code}\n" https://$D/.well-known/openid-configuration
curl -sS -o /dev/null -w "api %{http_code}\n" https://$D/api/users     # 401 expected
```

---

## 1. Nothing loads / certificate problems

| Symptom | Evidence | Cause | Fix |
|---|---|---|---|
| Browser: connection refused / timeout | `curl … https://$D/` → `000` | ports 80/443 blocked, Caddy down, DNS wrong | `docker compose ps caddy`; `ss -ltnp \| grep -E ':80 \|:443 '`; cloud SG/NSG; `getent hosts $D` must equal the public IP |
| Browser certificate warning; `openssl s_client` shows issuer `Caddy Local Authority` or self-signed | Caddy could not get a Let's Encrypt cert | DNS not pointing here, port 80 blocked (HTTP-01), outbound 443 blocked, or LE rate limit | `docker compose logs caddy \| grep -iE "acme\|challenge\|obtain\|rate"`; fix DNS/ports; Caddy retries automatically. Rate-limited (`too many certificates already issued`) → wait or switch to `provided` mode |
| Works by IP but not by name (or vice versa) | | Caddy only serves the configured domain (and `*.domain`) | always use `https://<domain>`; the installer's `use-ip` mode is HTTP-only and for tests |
| `502 Bad Gateway` right after install/restart | | upstream containers still starting | wait 60 s; if persistent see §2 |
| Dashboard loads, assets missing / blank page | `docker compose logs dashboard` | dashboard container not running or `dashboard.env` unsubstituted | `docker compose up -d --force-recreate dashboard` |
| Login page shows "Instance not found. Make sure you got the domain right." (404) | Zitadel `unable to set instance using origin <host> (ExternalDomain is <x>)` | request Host ≠ `ZITADEL_EXTERNALDOMAIN` (alias/CNAME, IP, or wrong proxy Host header) | use the installed domain exactly; do not add aliases |

Provided-certificate deployments: expiry is **your** job. Check
`echo \| openssl s_client -connect $D:443 -servername $D 2>/dev/null \| openssl x509 -noout -enddate`
and rotate per `02-server-operations.md` §8.2.

---

## 2. A container is unhealthy or restarting

`docker compose ps` shows `Restarting`, `Exit`, or `unhealthy`.

| Container | Log signature | Cause | Fix |
|---|---|---|---|
| `postgres` | `FATAL: … max_connections`, disk errors, `could not write` | disk full, too many clients | `df -h`; see §6; lower pool sizes (`02-server-operations.md` §5) |
| `postgres` | `database files are incompatible with server` | someone changed the `postgres:16` tag | restore the `postgres:16` tag; never bump major without dump/restore |
| `management` | `failed creating Store: …` / `NETBIRD_STORE_ENGINE_POSTGRES_DSN is not set` | DSN env missing/edited, DB down | check `docker-compose.yml` management env; `docker compose ps db` |
| `management` | `failed retrieving a new idp manager with err: … configuration is incomplete, X is missing` | `management.json` `IdpManagerConfig` broken | restore from backup (`config.tgz`); fields required: ClientID, ClientSecret, TokenEndpoint, ManagementEndpoint, GrantType |
| `management` | `failed fetching OIDC configuration from endpoint https://<domain>/.well-known/openid-configuration` | Zitadel not up yet, or Caddy not resolving the domain internally | wait for Zitadel; check `extra_hosts` in compose maps `<domain>` to the host IP / `172.20.0.1`; `docker exec management getent hosts <domain>` |
| `management` | `failed creating datadir` | volume permission | `docker volume inspect netzilo_management`; permissions on `/var/lib/docker` |
| `management` | `auto migrate: …` | schema migration failed (upgrade) | note exact error; roll back image tag (`02-server-operations.md` §4.3); restore DB dump if the new schema is partially applied |
| `management` | `TrustedPeers are configured to default value '0.0.0.0/0', '::/0'. This allows connection IP spoofing.` | informational warning | ignore (single-host deployments) |
| `management` | `could not initialize geo location service: … we proceed without geo support` | GeoLite2 DB missing (no internet at first start) | geo posture checks unavailable until the DB downloads; retry with internet or copy `GeoLite2-City.mmdb` + `geonames.db` into the `netzilo_management` volume and restart |
| `zitadel` | `masterkey must be 32 bytes, but is N` / `No master key provided` | `ZITADEL_MASTERKEY` edited/lost in `zitadel.env` | restore the original value from backup — there is no recovery without it |
| `zitadel` | `unable to decrypt key` | masterkey does not match the database | same as above; the DB was created with a different key |
| `zitadel` | `DB CONNECTION ERROR` (`/debug/ready` → 412) | Postgres down or credentials changed | `docker compose ps db`; compare `ZITADEL_DATABASE_POSTGRES_*` in `zitadel.env` with `POSTGRES_PASSWORD` in compose |
| `zitadel` | `migration already started, will check again in 5 seconds` (looping) | a previous start died mid-migration | wait a few minutes; if stuck >10 min restart Zitadel once |
| `zitadel` | container still runs `start-from-init` after years | normal on AMI images if installer didn't switch; harmless (idempotent) | none |
| `caddy` | `address already in use` | host nginx/apache on 80/443 | stop the other server |
| `coturn` | `Cannot bind` | host port 3478/5349 busy | free the port; coturn runs in host network mode |
| `redis` | `MISCONF … Redis is configured to save RDB snapshots` | disk full | free disk; `docker compose restart redis` |

Get full logs for the failing service: `docker compose logs --since 30m <service>`.

---

## 3. Cannot log in to the dashboard

| Symptom | Cause | Fix |
|---|---|---|
| Wrong password on first login | credentials are in `/opt/netzilo/CREDENTIALS` (username = admin email); AWS also in SSM `/netzilo/<stack>/admin-credentials` | use those; if the admin password was operator-supplied no change is forced at first login |
| Login page loops back to the dashboard login button | OIDC redirect URI mismatch — accessing via a different hostname than installed | use the exact domain; check the browser URL bar |
| Zitadel page: `The requested redirect_uri is missing in the client configuration.` | same as above, or the Dashboard app's redirect URIs were edited in the Zitadel console | Zitadel console → Projects → NETZILO → Dashboard → Redirect URIs must contain `https://<domain>/nb-auth`, `/nb-silent-auth`, `/nb-auth-x`; post-logout `https://<domain>/`, `/nb-logout` |
| Zitadel page: `code_challenge required` / `invalid client_id / client_secret` | Dashboard app auth method changed from **None (PKCE)** | set back to None |
| Dashboard: "Oops, something went wrong — There was an error logging you in." | token could not be validated by the dashboard/management | `curl https://<domain>/.well-known/openid-configuration` must return `"issuer":"https://<domain>"`; management log `invalid issuer` / `invalid audience` → `management.json` `HttpConfig.AuthIssuer`/`AuthAudience` vs Zitadel Dashboard client id |
| Infinite spinner after login | dashboard cannot reach the API: `/api/users` failing (CORS, 5xx) | `curl -sS https://<domain>/api/users -H "Authorization: Bearer x"` should be 401 not 5xx; check management logs |
| `User could not be found` / `User is locked` / `User is not active` | Zitadel user state | see `04-identity-and-sso.md` §5 (unlock/reactivate/reset) |
| Password reset email never arrives | **no SMTP is configured by the installer** | configure SMTP in the Zitadel console (`04-identity-and-sso.md` §6) or reset the password from the dashboard/console instead |
| `user.failedlogin` events pile up in Activity | expected audit of failed IdP logins | investigate the user/IP |
| New user invited from dashboard never receives email | same SMTP gap | create the user with **Create password** instead of **Email invitation**, or configure SMTP |
| Admin sees plan limits ("Upgrade Plan") on a self-hosted server | tenant not Enterprise and MSP mode not active | `02-server-operations.md` §12.2 |

---

## 4. Clients cannot connect to the server

| Symptom on client | Server-side check | Fix |
|---|---|---|
| `Management: Disconnected` | `curl -sS -o /dev/null -w "%{http_code}" https://<domain>/api/users` → 401 means management is fine | client network/proxy; certificate not trusted by the client OS (provided cert with missing intermediates → installer warns `fullchain.pem contains only the leaf certificate.`) |
| `Signal: Disconnected` while management connected | `docker compose logs signal` | Caddy route `/signalexchange.SignalExchange/*` → `signal:10000`; restart signal |
| `Relays: 0/2 Available` | `docker compose logs coturn`; `ss -lunp \| grep 3478` | open 3478 tcp/udp and 5349 tcp/udp inbound; relay range 49152–65535/udp for relayed sessions; behind 1:1 NAT add `external-ip=` to `turnserver.conf` (`02-server-operations.md` §12.4) |
| TURN test from a browser (WebRTC trickle-ICE sample) shows no `relay` candidates | | same port problem, or the TURN credential in `management.json` (`TURNConfig.Turns[].Password`) differs from `turnserver.conf` `user=self:<pw>` (only if someone edited one of them) |
| `peer is not registered` for all clients after a restore | restored DB is older than the peers' registrations | re-enrol the affected peers |
| Setup keys rejected: `setup key is invalid` | key expired/revoked/over limit in Dashboard → Setup Keys | new key |
| Peers connect but cannot see each other | policies (`08-network-administration.md` §4); management log `NB_DISABLE_PEER_BROADCASTS` is `true` in the shipped compose — clients pull updates every ~30 s | wait 30 s or `netzilo refresh` on the client |
| gRPC works only on port 33073 for old clients | management also listens on legacy 33073 internally, but Caddy exposes only 443 | clients must use `https://<domain>` (443) |

---

## 4a. Signal and relay (STUN/TURN) — dedicated diagnosis

Three server components stand between two peers, and they fail differently. Identify
which one before touching anything.

| Component | What it does | If it is down |
|---|---|---|
| **Management** | authenticates peers, distributes the network map, policies, routes and the **list of STUN/TURN servers with credentials** | peers cannot enrol or receive updates; existing tunnels keep working |
| **Signal** | relays the connection *offer* between two peers (ICE candidates) so they can find each other; stateless, carries no data | peers stay `Connected` to management but **new** peer-to-peer connections never establish |
| **Relay (coturn)** | **STUN** tells a peer its public address; **TURN** forwards WireGuard packets when a direct path cannot be found | peers behind restrictive NAT show `Disconnected` or flap; peers that could connect directly still work |

Shipped configuration (the installer writes it; know it before diagnosing):

- coturn runs in **host network mode**, so its ports belong to the host: `3478` tcp+udp
  (STUN/TURN), `5349` tcp+udp (TURN over TLS), relay allocations `49152–65535/udp`.
- Peers receive from management: `stun:<domain>:3478`, `turn:<domain>:3478` (UDP) and
  `turns:<domain>:5349?transport=tcp`, with a **static** username `self` and a password
  that must match `user=self:<password>` in `turnserver.conf`. Credentials are not
  time-based.
- In Let's Encrypt mode **no certificate is mounted into coturn**, so `turns:5349` cannot
  complete TLS; clients fall back to `turn:3478/udp`. UDP 3478 must therefore be
  reachable (`02-server-operations.md` §8.4).
- `external-ip` is **not** set. Behind 1:1 NAT (every cloud VM) coturn advertises its
  private address in relay candidates (`02-server-operations.md` §12.4).
- Signal is reached through Caddy on 443: route `/signalexchange.SignalExchange/*` →
  `signal:10000` (gRPC over h2c).
- An account can override the built-in relay with Integrations → Networking (Twilio,
  Cloudflare, or **TURN/STUN Servers**); if one is active, the peers are not using
  coturn at all — check there first.

### 4a.1 Read the client first

`netzilo status -d` on any affected peer tells you which component to look at:

| Client shows | Points at |
|---|---|
| `Signal: Disconnected, reason: …` while `Management: Connected` | signal container or its Caddy route |
| `Relays: 0/2 Available` (`--detail` lists each URI as `Unavailable, reason: …`) | coturn not reachable: ports, host firewall, cloud security group, container down |
| `Relays: 1/2 Available` with the `turns:…:5349` entry unavailable | expected on Let's Encrypt installs (no TLS cert for coturn); only a problem if UDP 3478 is also blocked at the client's site |
| every peer `Connection type: Relayed` | direct paths impossible (symmetric NAT, UDP blocked at client sites); relay is working; performance complaint, not outage |
| peers `Disconnected`, handshake `-`, relays available | signal exchange failing, or relay allocations blocked (port range) |
| one site fine, another all-relayed or failing | the failing site's outbound firewall, not the server |

### 4a.2 Verify signal (server)

```bash
cd "$C"
sudo docker compose ps signal                         # Up
sudo docker compose logs --tail=100 signal            # errors?
grep -n "signalexchange" Caddyfile                    # route must exist
sudo docker compose logs --tail=200 caddy | grep -i signalexchange | tail -5
```

Signal keeps no state; if the container is Up, the route exists and Caddy is serving 443,
signal works. A restart is harmless: `sudo docker compose restart signal`. If `netzilo
status` still shows `Signal: Disconnected` afterwards, the problem is between the client
and port 443 (proxy, TLS trust, DPI on HTTP/2 — try `NB_FORCE_WS=1` on the client).

### 4a.3 Verify STUN/TURN (server)

Ports and process:

```bash
sudo ss -lunp | grep -E ':3478|:5349'                 # udp listeners
sudo ss -ltnp | grep -E ':3478|:5349'                 # tcp listeners
sudo docker compose logs --tail=200 coturn            # "401" lines = credential rejections
```

Credentials consistent between what management hands out and what coturn accepts —
compares hashes, prints no secret:

```bash
cd "$C"
A=$(sudo jq -r '.TURNConfig.Turns[0].Password' management.json | tr -d '\n' | shasum -a 256 | cut -c1-12)
B=$(sudo sed -n 's/^user=self://p' turnserver.conf | tr -d '\n' | shasum -a 256 | cut -c1-12)
[ "$A" = "$B" ] && echo "TURN credentials consistent" || echo "MISMATCH: management.json vs turnserver.conf"
```

A mismatch only happens if a file was edited by hand; fix by making `turnserver.conf`
match `management.json` and `docker compose restart coturn`.

Functional self-test with the tools shipped inside the coturn image (host network, so
`127.0.0.1` reaches the daemon):

```bash
cd "$C"
PW=$(sudo jq -r '.TURNConfig.Turns[0].Password' management.json)
# STUN binding
sudo docker compose exec coturn turnutils_stunclient -p 3478 127.0.0.1
# TURN allocation + client-to-client relay over UDP
sudo docker compose exec coturn turnutils_uclient -v -y -n 3 -u self -w "$PW" -p 3478 127.0.0.1
# TURN over TLS (expected to FAIL on Let's Encrypt installs — no cert mounted)
sudo docker compose exec coturn turnutils_uclient -v -y -n 3 -t -S -u self -w "$PW" -p 5349 127.0.0.1
unset PW
```

Read the results: a successful run reports the allocation and sent/received counts;
`401` in the output means the credential was rejected (run the consistency check
above); no response at all means the port is not reachable. Testing against
`127.0.0.1` proves the daemon; it does **not** prove the public path — cloud NAT
usually blocks hairpin, so test the public address from an outside machine (§4a.4).

### 4a.4 Verify from a client site

Browser test (documented for Netzilo): open the WebRTC **trickle ICE** sample page,
remove the default servers, add `turn:<domain>:3478` with username `self` and the
password from `management.json`, and gather candidates. Expect `host`, `srflx` (STUN
worked) and `relay` (TURN worked). `srflx` missing → UDP 3478 blocked between that site
and the server. `relay` missing with `srflx` present → credentials, or the relay range
`49152–65535/udp` blocked inbound to the server.

From a Linux/macOS machine outside the server's network, the same image works as a
client: `docker run --rm coturn/coturn turnutils_stunclient -p 3478 <public-ip-or-domain>`.

### 4a.5 Failure table

| Evidence | Cause | Fix |
|---|---|---|
| coturn `Cannot bind` / restart loop | 3478 or 5349 already used on the host | `sudo ss -lunp \| grep 3478`; stop the other service |
| Relays unavailable from everywhere; `ss` shows listeners | inbound 3478/5349 blocked by cloud security group or host firewall | open them; on marketplace images they are open by default |
| `srflx` present, `relay` absent for all sites | relay range `49152–65535/udp` not open inbound; or credentials | open range; run the consistency check |
| relay works from the host, fails externally | cloud 1:1 NAT: candidates carry the private IP | add `external-ip=<public>/<private>` to `turnserver.conf`, `docker compose restart coturn` |
| `turns:5349` unavailable, `turn:3478` fine | expected in Let's Encrypt mode | leave it, or mount a certificate (`02` §8.4); ensure client sites allow UDP 3478 |
| relays fine, peers still `Disconnected`, signal `Connected` | ICE cannot complete: both sites block UDP and TCP TURN also blocked | at minimum allow outbound TCP 5349 or UDP 3478 from client sites |
| everything relayed for one site | that site's NAT/firewall blocks UDP to other peers | acceptable; open outbound UDP or set `--external-ip-map` on servers behind 1:1 NAT (`07` §3) |
| relays fine at install, broken after enabling an integration | Integrations → Networking overrides the relay list | check Twilio/Cloudflare/static config; **Test Connection** in the dashboard |
| coturn logs many `401` | credentials mismatch or a foreign client probing | consistency check; if consistent and clients work, ignore probing |
| high CPU on coturn | many relayed sessions | make direct paths possible (UDP at sites), or scale the host |

Logs to keep for escalation: `docker compose logs coturn` and `signal` for the window,
plus `netzilo status -d` from one affected peer at each site.

---

## 5. Performance and load

| Symptom | Evidence | Fix |
|---|---|---|
| Dashboard slow, API timeouts | `docker stats`; management log `too many clients already` | lower `NETBIRD_DB_MAX_OPEN_CONNS`/`IDLE` (200/100 → 60/30) or raise Postgres `max_connections`; move to 4 vCPU/16 GB |
| High CPU on management with many peers | `NB_SYNC_MAX_CONCURRENT=100` limits concurrent syncs | expected under mass reconnect; increase instance size |
| Zitadel slow / 5xx under login storm | `ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS=20` | raise to 40 in `zitadel.env` (keep total under Postgres `max_connections`) |
| Disk filling | `du -sh /var/lib/docker/containers/*` | container logs unbounded — configure Docker log rotation (`02-server-operations.md` §2.2); lower `ZITADEL_LOG_LEVEL` to `info` |
| Postgres volume growing fast | `events` table (activity) grows with usage; `account_stats` pruned at 90 days automatically | archive/stream events to S3 (Integrations → Event Streaming) and prune with a DB maintenance window (coordinate with Netzilo before deleting rows) |

---

## 6. Disk full

```bash
df -h /
sudo du -sh /var/lib/docker/containers /var/lib/docker/volumes/netzilo_* /var/lib/docker/overlay2 2>/dev/null
sudo docker system df
```

Safe reclaim: `sudo docker image prune -f` (old images), truncate container logs
(`sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log`) then configure rotation,
delete old backups under `/var/backups/netzilo`. **Never** `docker volume prune` on this
host — `netzilo_db_data` is the database. After freeing space `docker compose restart
postgres redis management zitadel`.

---

## 7. After a host reboot / cloud maintenance

Expected: all containers return automatically. If not:

```bash
sudo systemctl status docker
cd "$C" && sudo docker compose up -d && sudo docker compose ps
```

AWS: if the instance got a new public IP (no EIP association) DNS is stale → fix the `A`
record; Let's Encrypt renews on the same domain. Azure: the public IP is static.

Coturn advertises the host's addresses; a changed private IP requires no config unless
`external-ip=` was set manually — update it.

---

## 8. Upgrade went wrong

1. `docker compose ps` — which container is failing; read its log (§2).
2. Roll back: restore the previous `image:` lines in `docker-compose.yml`
   (marketplace images) or pin the previous tag instead of `:latest` (on-prem), then
   `docker compose up -d`.
3. If management applied an incompatible migration, restore the pre-upgrade dump
   (`02-server-operations.md` §7.1) **and** the old image together.
4. Zitadel migrations are forward-only; do not downgrade Zitadel after it started
   successfully on the new version — leave it and roll back only management/dashboard if
   needed.

---

## 9. Metering / billing (marketplace)

| Log (`/var/log/netzilo-metering.log`) | Meaning | Action |
|---|---|---|
| `metering disabled — skipping` | `METERING_ENABLED=0` (contract listing) | none |
| `no Marketplace product code on this instance — not a metered Marketplace launch; skipping` | AMI launched outside Marketplace | none (no billing) |
| `ERROR: could not read user count (got '…') — not reporting` | Postgres unreachable | fix DB; the timer retries hourly |
| `WARN: AWS meter-usage failed (rc=N) — will retry next hour` | IAM role lacks `aws-marketplace:MeterUsage` or no egress to the metering API | check instance role and outbound 443 |
| `no managed-application resource id on this instance — not a managed-app deploy; skipping` | Azure VM deployed outside the managed app | none |
| `WARN: no metering token — skipping` | VM identity lacks `Reader` on the resource group | fix role assignment |

Run now: `sudo systemctl start netzilo-metering.service && sudo tail -n 20 /var/log/netzilo-metering.log`.

---

## 10. When to escalate to Netzilo

Escalate (support@netzilo.com) with the first-pass output when:

- management logs a Go panic or `auto migrate` failure not fixed by rollback;
- Zitadel masterkey is lost and no backup exists (data recovery is impossible; the
  answer is reinstall + re-enrol, but confirm with the customer first);
- on-prem stack shows plan/billing limits although MSP mode is configured;
- a suspected bug in policy/route enforcement reproducible on a clean pair of peers.

Do not send an ad-hoc e-mail. Build the support package with
`12-escalation-package.md` — it defines what to collect, the mandatory redaction pass,
and the summary/timeline documents support needs. Never include `zitadel.env`,
`management.json`, `CREDENTIALS`, or database dumps in a ticket.
