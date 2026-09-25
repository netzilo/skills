---
id: '01'
title: Netzilo Server — Installation Runbook (all delivery paths)
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 32389
sections:
- id: '0'
  title: What gets installed (all paths)
  chars: 4891
- id: '1'
  title: Path A — On-prem / any Linux server (one-liner)
  chars: 8416
- id: '2'
  title: Path B — AWS Marketplace (CloudFormation)
  chars: 3879
- id: '3'
  title: Path C — Azure Marketplace (managed application)
  chars: 2245
- id: '4'
  title: Variant — external PostgreSQL
  chars: 1093
- id: '5'
  title: Variant — running the core engine directly (advanced / air-gapped)
  chars: 2636
- id: '6'
  title: Installation failures — diagnosis table
  chars: 5282
- id: '7'
  title: Legacy path — `infrastructure_files` docker-compose
  chars: 1054
- id: '8'
  title: Teardown (before a re-install, or to remove)
  chars: 751
- id: '9'
  title: Reporting template
  chars: 1227
---
# Netzilo Server — Installation Runbook (all delivery paths)

**Audience:** an AI operator installing **Netzilo Server** for a customer on any of the
three supported paths: bring-your-own Linux server (on-prem installer), AWS Marketplace
(CloudFormation + AMI), or Azure Marketplace (managed application). This document also
covers the variants the wizard does not expose (external database, air-gapped image
loading, self-signed/provided TLS) and the legacy docker-compose path.

**Contract:** follow the gates. Never invent input values — prompt the customer for each
required value, echo the full set back (password masked) and get an explicit "yes" before
running anything. Report success only when every gate passes. For the on-prem one-liner
flow with full gate scripts, `18-server-install-gated.md` (same folder) is the detailed
companion; this document adds the cloud paths and the advanced variants.

---

## 0. What gets installed (all paths)

One Ubuntu 22.04 host running nine Docker containers: `caddy`, `dashboard`,
`management`, `signal`, `zitadel` (identity), `postgres`, `redis`, `support-worker` — the
AI Assistant's agent, reachable only by `management` over the compose network — and
`coturn` (relay). Dashboard, API, management, signal and identity are all served through
Caddy on `443`; the relay is **not** — coturn runs in host network mode on its own ports
(`3478`, `5349`, relay range `49152–65535/udp`). See `02-server-operations.md` §1–2 for
the layout and service map and §11 for the firewall reference.

**Three delivery paths, three pipelines.** The custom one-liner (wrapper + engine
fetched from `pkg.netzilo.com`), the AWS AMI (Packer image + CloudFormation + first-boot)
and the Azure image (Packer + ARM + first-boot) run the same engine *file*,
`install_netzilo.sh`, but each pins its container images independently: the one-liner
retags every Netzilo image to `:latest` at install time — the moving tag that only the
AZURE release-branch builds publish, so a custom install always gets the newest release
build; the AMI and Azure builds bake the images into the VM image and pin each to an
immutable digest. Diagnose them as
separate environments — a fix in one pipeline says nothing about the other two.

**Which builds carry `support-worker`.** The worker joined the engine in September 2026.
Engines published before that — and AMIs or Azure images baked from them — install
eight containers and never show the Assistant, however new the management image is.
Tell the two apart on the host before diagnosing a "missing Assistant":

```bash
grep -c 'support-worker' /opt/netzilo/docker-compose.yml        # custom one-liner
grep -c 'support-worker' /opt/netzilo/run/docker-compose.yml    # AWS / Azure image
# 0 = pre-worker engine (eight containers): the Assistant cannot be enabled on this
#     install; a new install from a current engine/image is required (teardown §8).
# >0 = worker engine (nine containers): continue with the gates.
```

A pre-worker install cannot gain the worker in place: `docker compose pull` only
refreshes images that are already in the compose file, and re-running the installer
wipes the server (§1.4, §8). Move by backup → new install → restore
(`02-server-operations.md` §6–7).

Inputs every path needs:

| Input | Rule |
|---|---|
| Domain (FQDN) | Valid FQDN; **cannot be `*.netzilo.com`**; DNS `A` record must point at the server's public IP **before** install for Let's Encrypt. The domain is permanent (see `02-server-operations.md` §9). |
| Admin email | Becomes the dashboard login username (Zitadel human user). |
| Admin first + last name | Both **mandatory** (the core installer fails late — after containers are up — if missing). |
| Admin password | Wrapper/CFN/ARM enforce: ≥12 chars with upper, lower, digit, symbol. |
| TLS mode | `letsencrypt` (default) or `provided` (fullchain + key). |

Sizing: min 2 vCPU / 4 GB / 40 GB; recommended 2 vCPU / 8 GB.

**On the minimum.** The published product documentation quotes a higher floor than the numbers above, which reflect what the marketplace images actually run on. Below the published minimum a server will start and work for a small pilot, but sizing questions during a support case will be judged against the published figure. For anything beyond a pilot, provision to the published minimum and treat the lower numbers as a lab floor, not a target.

Firewall inbound (`02-server-operations.md` §11 is the reference): **required** `443/tcp`
(web, management, signal), `80/tcp` (Let's Encrypt validation + redirect), `3478/udp`
(STUN/TURN) and `49152–65535/udp` (relay allocations — needed for every relayed
connection); `5349/tcp` (TURN over TLS) is the fallback for clients on UDP-blocking
networks and only completes once a certificate is mounted into coturn
(`02-server-operations.md` §8.4); `3478/tcp` and `5349/udp` are **optional** (coturn
listens, no client is given an address on them); `22/tcp` from the admin CIDR only. The
AWS and Azure templates open all of these including the relay range; on a self-managed
host the customer must, and a host firewall (`ufw`/`firewalld`) applies to coturn because
it uses host networking. Never expose `6379` (Redis).

The installer needs outbound HTTPS to `ghcr.io` (Netzilo images), Docker Hub (caddy,
coturn, postgres, redis), `pkg.netzilo.com` (installer download) and Let's Encrypt.
At run time `support-worker` needs outbound HTTPS to whichever AI provider the owner
connects (Integrations → Artificial Intelligence) and, optionally, to `github.com` to
refresh its runbooks — it works from the copy baked into its image without it. Everything
about configuring, deploying and operating the Assistant after install, including
Kubernetes, proxies and air-gapped servers, is `42-ai-assistant-self-hosted.md`.

---

## 1. Path A — On-prem / any Linux server (one-liner)

### 1.1 Preconditions (Gate 1)

```bash
. /etc/os-release; echo "$PRETTY_NAME"; uname -m; nproc; free -h | awk '/Mem/{print $2}'; df -h / | awk 'NR==2{print $4}'
getent hosts <domain>      # must print the server's public IP
curl -s ifconfig.me        # public IP as seen from outside
```

Ubuntu 20.04/22.04/24.04 x86_64 (the wrapper warns and continues on other distros:
`WARN: designed for Ubuntu; '<id>' may work but is untested.`); root or sudo.
Docker is installed automatically by the wrapper if missing (Docker CE apt repo +
compose plugin).

### 1.2 Interactive install

```bash
curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh | sudo bash
```

Prompts, in order: domain, public IP, admin first name, admin last name, admin email,
admin password (silent), TLS mode `[1/2]` (1 = Let's Encrypt, 2 = provided; then the
paths to the fullchain PEM and private key PEM). It then warns if DNS does not resolve
to the given IP (`WARN: Let's Encrypt will FAIL until the A record points here`) and
asks `Continue anyway? [y/N]`.

### 1.3 Unattended install (preferred when an agent drives it)

The wrapper takes every answer from environment variables and skips the prompts with
`--yes`. Do **not** put the values on the command line (they would land in shell history
and the process list, and quoting breaks on passwords containing `'`, `$`, `` ` `` or
`!`). Put them in a root-only `0600` env file that bash sources — `printf '%q'`
shell-quotes each value so it reaches the installer byte-for-byte — and delete the file
after the install:

```bash
sudo -n true                                    # unattended runs need passwordless sudo
umask 077
IFS= read -r -s -p 'Admin password: ' PW; echo
{
  printf '%s=%q\n' NETZILO_DOMAIN           '<fqdn>'
  printf '%s=%q\n' NETZILO_PUBLIC_IP        '<ipv4>'
  printf '%s=%q\n' NETZILO_ADMIN_FIRST_NAME '<first>'
  printf '%s=%q\n' NETZILO_ADMIN_LAST_NAME  '<last>'
  printf '%s=%q\n' NETZILO_ADMIN_EMAIL      '<email>'
  printf '%s=%q\n' NETZILO_ADMIN_PASSWORD   "$PW"
  printf '%s=%q\n' NETZILO_TLS_MODE         letsencrypt
  printf '%s=%q\n' NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED true   # password came through chat: replace at first login
} | sudo sh -c 'umask 077; cat > /root/netzilo-install.env'
unset PW

sudo sh -c 'umask 077; cat > /root/run-install.sh' <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
set -a; . /root/netzilo-install.env; set +a
export NETZILO_ASSUME_YES=1
curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh -o /root/install-netzilo.sh
bash /root/install-netzilo.sh --yes
EOF
```

Provided certificate instead: add `NETZILO_TLS_MODE=provided`, `NETZILO_CERT_FILE=/path/fullchain.pem`
and `NETZILO_KEY_FILE=/path/privkey.pem` lines to the env file (same `printf '%q'` form).
The fullchain must contain leaf + intermediates; the installer validates PEM syntax,
key/cert match, expiry, chain completeness and (if a system CA bundle exists) trust.

Run it detached so it survives SSH drops (it takes 3–8 minutes), then poll for the marker
lines only — the end of the log carries the admin credentials, so do not `tail`/`cat` it
into a conversation:

```bash
sudo bash -c 'nohup bash /root/run-install.sh > /root/install.log 2>&1 &'
sudo grep -E "Done\. Netzilo is starting|ERROR:|aborted" /root/install.log   # repeat until one matches
sudo rm -f /root/netzilo-install.env /root/run-install.sh                    # as soon as it has finished
```

When the install is driven over SSH from another machine, follow
`18-server-install-gated.md` §1.1–2.3: verify and pin the host key first, and stream the
env file over stdin instead of building it on the host.

Optional wrapper variables: `NETZILO_IMAGE_TAG` (default `latest`; applies to the five
Netzilo images), `NETZILO_INSTALLER_URL` (where the core installer is downloaded from, default
`https://pkg.netzilo.com/download/install_netzilo.sh`), `NETZILO_STATE_DIR` (default
`/opt/netzilo`), `NETZILO_PKG_BASE_URL` (client download mirror shown in the dashboard).

### 1.4 What the wrapper does (so you can diagnose it)

1. Validates inputs (regexes in §0), installs `ca-certificates curl gnupg jq openssl`
   and Docker if missing.
2. DNS pre-check with `getent hosts`.
3. Downloads the core engine to `/opt/netzilo/install_netzilo.sh` (unless present
   next to the wrapper), copies a provided cert to `/opt/netzilo/certs/`.
4. Exports `NETZILO_NONINTERACTIVE=1 NETZILO_ASSUME_YES=1 NETZILO_IMAGE_SOURCE=cloud
   NETZILO_DB_MODE=container NETBIRD_DOMAIN=<domain> NETZILO_TLS_MODE=<mode>` and runs
   the engine **in `/opt/netzilo`** (compose files land directly there).
5. The engine: renders `docker-compose.yml`, `Caddyfile`, `zitadel.env` → starts
   `db`+`coturn` → `caddy`+`zitadel` → bootstraps Zitadel (project `NETZILO`, OIDC apps
   `Dashboard` and `Cli`, machine user `netzilo-service-account`, human admin, deletes
   the Zitadel default `zitadel-admin` user) → renders `management.json`,
   `turnserver.conf`, `dashboard.env` → `docker compose up -d` → writes
   `/opt/netzilo/CREDENTIALS` and `/opt/netzilo/netzilo-state.env`. Along the way it
   generates a shared `NETBIRD_SUPPORT_WORKER_TOKEN` and writes it into both places
   that must agree: `management.json` (`SupportConfig`: `WorkerURL
   http://support-worker:8080`, `ManagementURL http://management:80`, the token) and
   the `support-worker` service environment (`SUPPORT_WORKER_TOKEN`). The worker
   refuses to start if that variable is empty, so a mismatch fails loudly.
6. Prints `==> Done. Netzilo is starting at https://<domain>` and the credentials.

**Re-running the installer on the same host is destructive.** Because the wrapper
always runs with `NETZILO_ASSUME_YES=1`, the installer detects the existing
`docker-compose.yml`/`zitadel.env` and **wipes all containers, volumes (including
Postgres) and config without asking**. Only re-run after an intentional teardown or on a
throwaway host.

### 1.5 Verification gates (Gate 2–8)

```bash
D=<domain>
cd /opt/netzilo && sudo docker compose ps                                  # 9 Up, postgres+redis+support-worker healthy
curl -sS -o /dev/null -w "dashboard %{http_code}\n" https://$D/              # 200
curl -sS https://$D/.well-known/openid-configuration | grep -o '"issuer":"[^"]*"'   # "issuer":"https://<domain>"
curl -sS https://$D/ | grep -oiE '<title>[^<]*</title>'                      # <title>Netzilo</title>
echo | openssl s_client -connect $D:443 -servername $D 2>/dev/null | openssl x509 -noout -issuer -dates
sudo cat /opt/netzilo/CREDENTIALS
```

The Let's Encrypt certificate is obtained on the **first HTTPS request**; allow ~60 s.
A `502`/timeout in the first minute is warm-up, not failure.

### 1.6 First login

Open `https://<domain>`, sign in with the admin email + password. If the password was
generated by the installer (no `NETZILO_ADMIN_PASSWORD` given) Zitadel forces a
password change; with an operator-supplied password no change is forced unless
`NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED=true` was set (§1.3 sets it — a password that
passed through chat must not stay in use). The CREDENTIALS file says "You will be
required to change this password" in every case — that line is printed
unconditionally. The first authenticated login creates the tenant row.

Then hand the customer: dashboard URL, admin username, the location of
`/opt/netzilo/CREDENTIALS` (mode `600`; they read it on the host, you do not print it),
and the backup arrangement. **Nothing is backed up automatically.** Install the
fail-closed script and schedule from `02-server-operations.md` §6.2–6.3 and run it once
by hand: it must end with `BACKUP OK`, and it exits non-zero and marks the run `.FAILED`
if any required artifact (database dumps, `management.json`, `zitadel.env`,
`docker-compose.yml`, `Caddyfile`, `dashboard.env`, `turnserver.conf`, provided
certificates) is missing. Agree a date for the isolated restore rehearsal (§6.4); until
one has passed the customer is not disaster-recovery ready, and say so in the handover.

The **AI Assistant** is installed and healthy but stays hidden until an owner connects
an AI provider and approves a model for Assistant under Integrations → Artificial
Intelligence (`30-activity-reports-and-integrations.md` §4a). No model key ships with
the server; say so when handing over, so its absence is not reported as a fault.

---

## 2. Path B — AWS Marketplace (CloudFormation)

Listing: `https://aws.amazon.com/marketplace/pp/prodview-vf2pu4dhv53bs`. Time 10–15 min.

### 2.1 Before launching

1. **Allocate an Elastic IP** in the target region (EC2 → Elastic IPs → Allocate). Note
   the allocation ID `eipalloc-…`.
2. **Create the DNS `A` record** `<domain> → <Elastic IP>`. The template goes straight
   to Let's Encrypt on first boot; if DNS is not in place, certificate issuance fails
   until it is (Caddy retries; fix DNS and wait).
3. Pick a VPC and a **public subnet in that same VPC** (error "security group and subnet
   belong to different networks" means they don't match).

### 2.2 Parameters

| Parameter | Notes |
|---|---|
| `NetziloDomain` | FQDN (regex-validated) |
| `EipAllocationId` | from step 1 |
| `AdminEmail`, `AdminFirstName`, `AdminLastName`, `AdminPassword` | password ≥12 chars, upper/lower/digit/symbol |
| `InstanceType` | `t3.large` (default, "up to a few hundred peers"), `t3.xlarge`, `m6i.large`, `m6i.xlarge` |
| `KeyName` | optional; SSM Session Manager works without it |
| `AllowedAdminCidr` | SSH source, e.g. `203.0.113.5/32`; avoid `0.0.0.0/0` |
| `VpcId`, `SubnetId` | public subnet in the VPC |
| `DbMode` | `container` (default) or `external` (+ `DbHost`, `DbPort`, `DbAdminUser`, `DbAdminPassword`, `DbSslMode` require/disable/verify-full) |

The stack creates: IAM role (SSM core + `ssm:PutParameter` on
`/netzilo/<stack>/*` + `aws-marketplace:MeterUsage`), security group (22 from admin
CIDR; 80, 443, 3478, 5349, 49152–65535/udp public), EIP association, EC2 with IMDSv2
required and a 30 GB encrypted gp3 root.

### 2.3 After `CREATE_COMPLETE`

Stack outputs: `DashboardURL`, `AdminCredentialsConsoleLink`, `AdminCredentialsCLI`,
`SessionManagerCommand`, `DnsReminder`.

```bash
aws ssm get-parameter --with-decryption --region <region> \
  --name /netzilo/<stack>/admin-credentials --query Parameter.Value --output text
aws ssm start-session --region <region> --target <instance-id>
```

First boot (`netzilo-firstboot.service`) takes ~5 minutes after the instance is
running; watch with `sudo tail -f /var/log/netzilo-firstboot.log` until
`=== Netzilo first-boot complete ===`. Compose dir is **`/opt/netzilo/run`**.
Credentials are in `/opt/netzilo/CREDENTIALS` and `/etc/motd`, and in SSM as above.

Metering (`METERING_ENABLED=1`, dimension `users`) runs hourly — see
`02-server-operations.md` §12.3.

### 2.4 What the AMI carries

- **Nine containers, all baked.** The image ships every container including
  `support-worker`, each pinned to an immutable digest; first boot starts them from the
  local image store (`NETZILO_IMAGE_SOURCE=cloud`, nothing is pulled). The worker's shared
  token is generated at first boot and written into both `management.json`
  (`SupportConfig.WorkerToken`) and the worker's environment, exactly as on the one-liner.
- **No new inbound port.** The worker listens on `:8080` on the compose network only and
  is called by `management`; the security group is unchanged (22 admin CIDR; 80, 443,
  3478, 5349, 49152–65535/udp public). Outbound it needs `443` to the AI provider the
  owner later connects, and to `github.com` for runbook refresh — the default egress
  rule allows both.
- **Nothing to configure for AI at launch.** The template has no AI parameters. The
  Assistant stays hidden until an owner adds a provider under Integrations →
  Artificial Intelligence (`30-activity-reports-and-integrations.md` §4a).
- **AMIs built before September 2026 have eight containers** and cannot be upgraded in
  place to nine — see §1 "Which builds carry `support-worker`". Launch a new stack from
  the current AMI and restore (`02-server-operations.md` §6–7).

Run the §1.5 gates against the domain: `docker compose ps` in `/opt/netzilo/run` must
show 9 Up with `postgres`, `redis` and `support-worker` healthy.

---

## 3. Path C — Azure Marketplace (managed application)

Listing: `https://marketplace.microsoft.com/en-us/product/netzilo.netzilo?tab=Overview`.
Billing is per named user per hour via Azure Marketplace metering.

### 3.1 Wizard

- **Basics:** subscription, resource group, region, domain FQDN, admin email, first/last
  name, admin password (≥12, complex). Application name and managed resource group.
- **Virtual machine:** size `Standard_D2s_v5` (recommended) or `Standard_D4s_v5`; OS
  username (default `azureuser`); SSH public key or password.
- **Network & access:** allowed admin source CIDR (default `*`). This restricts **only
  port 22** (the UI text says "SSH/dashboard"; dashboard 80/443 are always public).

DB parameters are not exposed in the wizard (container mode).

### 3.2 After deployment

1. Outputs: `dashboardAddress`, `publicIpAddress`, `sshCommand`, `dnsReminder`.
   **Create the DNS `A` record now** (`<domain> → publicIpAddress`; the IP is static).
   Unlike AWS there is nothing to reserve beforehand.
2. Let's Encrypt issues within a couple of minutes after DNS resolves.
3. SSH `azureuser@<publicIpAddress>`; MOTD shows the credentials; compose dir
   `/opt/netzilo/run`; first-boot log `/var/log/netzilo-firstboot.log`.
4. Run the §1.5 gates.

The VM has a system-assigned identity with `Reader` on the resource group; metering
uses it to discover the managed-application resource id.

### 3.3 What the Azure image carries

Same as the AMI (§2.4): nine containers baked and digest-pinned, including
`support-worker`; shared token generated at first boot; the worker is reachable only
from `management` on the compose network, so the NSG is unchanged (22 admin CIDR;
80, 443, 3478, 5349 and the relay range 49152–65535/udp public) and no wizard field
concerns AI. Outbound `443` to the
chosen AI provider and to `github.com` must be allowed (the default NSG outbound rule
does). The Assistant appears only after an owner connects a provider. Images published
before September 2026 run eight containers and cannot gain the worker in place — new
managed application from the current image, then restore (`02-server-operations.md`
§6–7). Gate 3 reads 9 Up with `postgres`, `redis` and `support-worker` healthy.

---

## 4. Variant — external PostgreSQL

Supported by all paths (`NETZILO_DB_MODE=external`; CFN `DbMode`; on Azure only by
editing the ARM template or a `firstboot.conf`). Requirements: PostgreSQL reachable from
the host; an admin role able to `CREATE DATABASE` and `CREATE ROLE`; `sslmode`
`require` recommended. The installer creates databases `netzilo` and `zitadel` and role
`zitadel`. No `db` container or `netzilo_db_data` volume is created. Backups become the
DB provider's responsibility; everything else in `02-server-operations.md` still applies.
`support-worker` is unaffected by the DB mode — it holds no data and talks only to
`management`; the stack is eight containers in external mode (no `postgres`).

On-prem, pass through the wrapper by exporting before `bash install-netzilo.sh --yes`:
`NETZILO_DB_MODE=external NETZILO_DB_HOST=… NETZILO_DB_PORT=5432 NETZILO_DB_ADMIN_USER=… NETZILO_DB_ADMIN_PASSWORD=… NETZILO_DB_SSLMODE=require`.
(The wrapper itself hard-sets `NETZILO_DB_MODE=container`; for external mode run the
core engine directly as in §5 with these variables.)

---

## 5. Variant — running the core engine directly (advanced / air-gapped)

The core engine `install_netzilo.sh` (published at
`https://pkg.netzilo.com/download/install_netzilo.sh`) is the file all three pipelines
run — with their own image pins, see §0. Use it directly when the wrapper's assumptions
don't fit. It writes into its **current working
directory**; run it from the intended install dir (`/opt/netzilo`).

```bash
sudo mkdir -p /opt/netzilo && cd /opt/netzilo
sudo NETZILO_NONINTERACTIVE=1 NETZILO_STATE_DIR=/opt/netzilo \
     NETBIRD_DOMAIN=<fqdn> NETZILO_TLS_MODE=letsencrypt \
     NETZILO_ADMIN_EMAIL=<email> NETZILO_ADMIN_FIRST_NAME=<first> NETZILO_ADMIN_LAST_NAME=<last> \
     NETZILO_ADMIN_PASSWORD='<pw>' \
     bash install_netzilo.sh
```

Engine variables not exposed by the wrapper:

| Variable | Default | Use |
|---|---|---|
| `NETBIRD_DOMAIN` | — | FQDN, or literal `use-ip` for **plain HTTP on port 80** (test only; no TLS at all) |
| `NETZILO_TLS_MODE` | `letsencrypt` | `selfsigned` generates a 1-year RSA-4096 cert in `./certs`; `provided` uses `NETZILO_CERT_DIR` |
| `NETZILO_CERT_DIR` | `./certs` | must contain `fullchain.pem` + `privkey.pem` |
| `NETZILO_IMAGE_SOURCE` | `cloud` | `disk` loads images from `NETZILO_IMAGES_DIR` (`*.tar.gz`/`*.tar`) — **air-gapped**; the nine archives must carry the expected tags |
| `NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED` | `false` | force a password change at first login even with a supplied password; the wrapper passes it through unchanged, so it also works in the §1.3 env file |
| `NETZILO_DB_*` | container | external DB (see §4) |
| `NETZILO_ZITADEL_DB_MAXOPENCONNS` etc. | 20/20/30m/5m | Zitadel pool |
| `NETZILO_MSP_KEY` | generated | non-empty enables MSP/Enterprise mode in management + dashboard |
| `NETZILO_PKG_BASE_URL` | `https://pkg.netzilo.com` | client download mirror |
| `NETZILO_L3_URL` | `https://l3.netzilo.com` | Netzilo Level 3 gate the AI Assistant escalates to |
| `NETZILO_L3_TOKEN` | empty | Netzilo Cloud service-account token; empty **disables** the Assistant's escalation tool (the Assistant itself still works) |

Air-gapped procedure: on a connected machine `docker pull` the nine images (tags from
the engine's `IMAGE_*` lines), `docker save <image> | gzip > netzilo-<name>.tar.gz`,
copy them plus the engine to the host, run with `NETZILO_IMAGE_SOURCE=disk
NETZILO_IMAGES_DIR=/path`. Docker must already be installed. Let's Encrypt is impossible
offline → use `provided` or `selfsigned`.

Docker prerequisite error: `ERROR: Docker is not installed or not running.` — the engine
never installs Docker (the wrapper does).

---

## 6. Installation failures — diagnosis table

Gather context first:

```bash
sudo tail -n 80 /root/install.log 2>/dev/null; sudo tail -n 80 /var/log/netzilo-firstboot.log 2>/dev/null
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo ); cd "$C"
sudo docker compose ps; sudo docker compose logs --tail=60 zitadel caddy
```

| Log line / symptom | Cause | Fix |
|---|---|---|
| `ERROR: password must contain upper, lower, number and a symbol.` / `must be at least 12 characters` | policy | new password, re-run on clean host |
| `ERROR: admin first and last name are required.` | names missing (engine, fails after containers are up) | set both names; **teardown** (§8) then re-run |
| `WARN: DNS for <d> = '<x>', not <ip>.` then cert never issues | A record wrong/missing | fix DNS; Caddy retries automatically (no re-run needed) |
| `ERROR: NETZILO_TLS_MODE must be 'letsencrypt' or 'provided'` | typo | fix value |
| `ERROR: Private key does not match the certificate.` / `Certificate expired on …` / `fullchain.pem contains only the leaf certificate.` | bad cert material | supply correct fullchain (leaf + intermediates) and matching key |
| `ERROR: Docker is not installed or not running.` | engine run without wrapper | install Docker CE + compose plugin |
| `Waiting for Zitadel's PAT to be created ....` forever | Zitadel not starting (DB, memory) | `docker logs zitadel`; check `docker compose ps db`; RAM ≥4 GB |
| `Failed requesting getting Zitadel PAT` | PAT file content `null` | Zitadel failed FirstInstance; check `docker logs zitadel`; teardown + re-run |
| `ERROR calling create_new_project: …` (or any `ERROR calling <fn>`) | Zitadel API rejected a bootstrap call — most often the bootstrap PAT **expired (30-minute lifetime from render time)** because image pulls/DB init took too long, or a previous partial run left data | teardown (§8) and re-run with images pre-pulled (`docker pull` the nine images first) |
| `ERROR: Could not verify service account credentials after 3 attempts.` | Zitadel token endpoint unreachable through Caddy at `https://<domain>` from the host (installer uses `--resolve <domain>:443:127.0.0.1`) | check `docker compose logs caddy`; ensure nothing else binds 80/443 (`ss -ltnp | grep -E ':80|:443'`); teardown + re-run |
| `ERROR: NETZILO_NONINTERACTIVE=1 but NETBIRD_DOMAIN is unset/invalid.` | engine run without domain | set `NETBIRD_DOMAIN` |
| `The domain name cannot be *.netzilo.com` | reserved | use the customer's own domain |
| Gate: `docker compose ps` shows fewer than 9, `management` restarting | management can't reach DB/redis or bad `management.json` | `docker compose logs management`; check `db`/`redis` healthy |
| Gate: `support-worker` `Restarting`/`Exit`, log `refusing to start: SUPPORT_WORKER_TOKEN is empty` | the shared token was not rendered into `docker-compose.yml` (hand-edited compose, or an engine older than the worker) | `SUPPORT_WORKER_TOKEN` in `docker-compose.yml` must equal `SupportConfig.WorkerToken` in `management.json`; fix both or re-install on a clean host |
| Dashboard has no AI Assistant button after login | no AI provider approved for Assistant — **expected on a fresh install** | owner connects a provider under Integrations → Artificial Intelligence (`30 §4a`) |
| Assistant message fails: `support agent is not configured on this deployment` | `SupportConfig` missing from `management.json` (engine older than the worker) | re-install with the current engine, or add the `SupportConfig` block and restart `management` |
| Any other Assistant failure after install (`support agent is unavailable`, `support worker returned HTTP 401`, provider errors, stale runbooks) | worker down, token mismatch, provider or egress trouble, old runbook copy | the symptom table in `42-ai-assistant-self-hosted.md` §11 |
| Gate: dashboard 200 but login loops back / "Oops, something went wrong" | browser reached the server by a different name than the installed domain (e.g. IP or alias) | always use `https://<domain>` exactly; OIDC redirect URIs are bound to it |
| Gate: TLS issuer is Caddy/self-signed instead of Let's Encrypt | HTTP-01 challenge failed (80 blocked, DNS) or LE rate limit | open 80/443, fix DNS; Caddy retries. If rate-limited (`too many certificates`) wait or use `provided` |
| Port 80/443 already in use | another web server on the host | stop/disable it (nginx/apache) before install |
| One-liner `curl` fails | no egress to `pkg.netzilo.com` | download on another machine, `scp` both scripts, run wrapper locally (it finds `install_netzilo.sh` next to itself) |
| `docker compose pull` → `manifest unknown` for a `ghcr.io/netzilo/*` image | a tag that does not exist (hand-edited pin), or — seen on a developer Mac — Docker Desktop mid credential-helper prompt answering `manifest unknown` for everything; the packages are public and need no login | verify the tag from a clean shell: `docker manifest inspect <image>`; if a known-good tag also fails, the client is at fault, not the registry |

Zitadel bootstrap is not resumable: after any `ERROR calling …` the only path is
teardown and a fresh run. Because the engine wipes state on re-run anyway, that is
acceptable **only at install time** (no customer data yet).

---

## 7. Legacy path — `infrastructure_files` docker-compose

The documentation site still contains an older, pre-installer self-hosting guide
(`setup.env` + `configure.sh` → `artifacts/docker-compose.yml`, ports 33073/10000, IdP
env blocks for Zitadel/Keycloak/Authentik/Entra/Okta/Google/Auth0/JumpCloud). If a
customer runs it:

- Their compose dir is `infrastructure_files/artifacts/`; management data in the
  `management` container at `/var/lib/netzilo/`; backup = copy `docker-compose.yml
  turnserver.conf management.json` + `docker compose cp -a management:/var/lib/netzilo/ backup/`.
- Upgrade = `docker compose pull && docker compose up -d --force-recreate`.
- Store engine is in `management.json` `StoreConfig.Engine` (`sqlite` default since
  0.26; `postgres` via `NETZILO_STORE_ENGINE_POSTGRES_DSN`).
- Their IdP is whatever `NETZILO_MGMT_IDP` says — use the per-provider env blocks in the
  docs (`selfhosted/identity-providers`) and `04-identity-and-sso.md` §7.

Do not mix the two paths on one host. For new installs always use §1–3.

---

## 8. Teardown (before a re-install, or to remove)

```bash
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo )
cd "$C" && sudo docker compose down --volumes
sudo rm -rf /opt/netzilo /root/run-install.sh /root/install-netzilo.sh /root/netzilo-install.env /root/install.log
```

This deletes everything. On a server that has ever held data, the backup gate
(`02-server-operations.md` §6.3) must have passed first — a complete, checksum-verified
backup less than an hour old — and the customer must have confirmed in writing. On a marketplace image also `sudo rm -f /opt/netzilo/.provisioned`
only if you intend firstboot to run again on next boot (it will then re-install from the
instance user-data).

---

## 9. Reporting template

Report PASS only if all are true; otherwise name the failing gate, paste the evidence,
and state the diagnosis:

- [ ] Gate 1 host meets OS/sizing/DNS prerequisites
- [ ] Gate 2 installer completed (`Done. Netzilo is starting …` / `first-boot complete`)
- [ ] Gate 3 9 containers Up, postgres + redis + support-worker healthy
- [ ] Gate 4 dashboard HTTP 200
- [ ] Gate 5 trusted certificate (or waived: provided/self-signed)
- [ ] Gate 6 OIDC discovery 200 with `issuer` = `https://<domain>`
- [ ] Gate 7 `<title>Netzilo</title>`
- [ ] Gate 8 `/opt/netzilo/CREDENTIALS` present (mode `600`) and handed over without printing it
- [ ] Firewall: required inbound rows of §0 open (`80`, `443`, `3478/udp`, `49152–65535/udp`; `5349/tcp` for UDP-blocked client sites) — on a self-managed host confirmed by the customer, on a marketplace image by the template
- [ ] Backup: fail-closed script and schedule installed, first run ended `BACKUP OK`, restore rehearsal date agreed (`02-server-operations.md` §6.2–6.4) — or the customer explicitly declined, in writing
- [ ] Admin password supplied through chat: `NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED=true` set and the customer told to replace it at first login
