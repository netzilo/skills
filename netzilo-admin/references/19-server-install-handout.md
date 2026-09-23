---
id: '19'
title: Install Netzilo Server on Your Own Server
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 9846
sections:
- id: step-1-check-the-prerequisites
  title: Step 1 — Check the prerequisites
  chars: 2078
- id: step-2-run-the-installer
  title: Step 2 — Run the installer
  chars: 416
- id: step-3-answer-the-prompts
  title: Step 3 — Answer the prompts
  chars: 732
- id: step-4-choose-how-https-is-secured
  title: Step 4 — Choose how HTTPS is secured
  chars: 654
- id: step-5-log-in
  title: Step 5 — Log in
  chars: 569
- id: optional-unattended-scripted-install
  title: Optional — Unattended (scripted) install
  chars: 1722
- id: managing-your-server
  title: Managing your server
  chars: 1992
- id: troubleshooting
  title: Troubleshooting
  chars: 980
- id: uninstall
  title: Uninstall
  chars: 170
- id: need-help
  title: Need help?
  chars: 156
---
# Install Netzilo Server on Your Own Server

Netzilo Server is a self-hosted secure-networking platform (management, signal,
dashboard, identity, and TURN relay). This guide installs the **complete stack
on a single Ubuntu server you control** — a cloud VM, a VPS, or bare metal — in
one command, with an automatic HTTPS certificate.

Total time: about **5–10 minutes**.

---

## Step 1 — Check the prerequisites

**A server**

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Operating system | Ubuntu 22.04 LTS (20.04 / 24.04 also work) | Ubuntu 22.04 LTS |
| CPU | 2 vCPU | 2 vCPU |
| Memory | 4 GB RAM | 8 GB RAM |
| Disk | 40 GB | 40 GB SSD |
| Access | `root` (or a user with `sudo`) | `root` |

**A domain name**

You need a domain (or subdomain) — for example `go.example.com` — and you must
point its **DNS `A` record at your server's public IP address _before_ you
install.** This is required so the server can obtain a free HTTPS certificate.

> Example: if your server's public IP is `203.0.113.10`, create this DNS record:
> `go.example.com  →  A  →  203.0.113.10`
>
> DNS changes can take a few minutes to take effect. You can verify with:
> `ping go.example.com` — it should reply from your server's IP.

**Open firewall ports**

Make sure your server / cloud security group **and** any firewall on the server itself
(`ufw`, `firewalld`) allow inbound traffic on:

| Port(s) | Protocol | Needed? | Purpose |
|---------|----------|---------|---------|
| `443` | TCP | Required | Dashboard, API, login, and the connection every client keeps open to the server |
| `80` | TCP | Required | HTTPS certificate validation + redirect to HTTPS |
| `3478` | UDP | Required | Relay service (STUN/TURN) — how clients find each other |
| `49152–65535` | UDP | Required for relayed connections | The relay hands each relayed connection a port from this range; without it, clients that cannot connect directly will not connect at all |
| `5349` | TCP | Recommended | Relay over TLS — the fallback for clients on networks that block UDP (only active once a certificate is configured for the relay; ask support) |
| `3478` TCP, `5349` UDP | — | Optional | The relay listens on them but clients are never sent there; opening or closing them changes nothing |
| `22` | TCP | Your address only | SSH — your own administrative access |

The relay is a separate service on its own ports; it does **not** run through `443`.

---

## Step 2 — Run the installer

Log in to your server over SSH, then run this **single command**:

```bash
curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh | sudo bash
```

That's it. The installer will:

1. install everything it needs (Docker), automatically;
2. download the latest Netzilo Server software;
3. start the whole platform;
4. secure it with a free, auto-renewing HTTPS certificate.

---

## Step 3 — Answer the prompts

The installer asks a few questions. Have these ready:

| You'll be asked for | Example | Notes |
|---------------------|---------|-------|
| **Domain (FQDN)** | `go.example.com` | The domain you pointed at this server in Step 1. |
| **Public IP** | `203.0.113.10` | This server's public IP address. |
| **Admin first name** | `John` | The first administrator. |
| **Admin last name** | `Doe` | |
| **Admin email** | `admin@example.com` | This becomes your **login username**. |
| **Admin password** | `••••••••••••` | At least **12 characters**, with an uppercase letter, a lowercase letter, a number, and a symbol. |
| **HTTPS certificate** | `1` | Choose how HTTPS is secured — see Step 4. |

---

## Step 4 — Choose how HTTPS is secured

When prompted, pick one:

**Option 1 — Let's Encrypt (recommended, the default)**
A trusted certificate is obtained and renewed automatically, for free. This is
the right choice for almost everyone. It requires that your domain points at
this server (Step 1) and that ports 80 and 443 are open (Step 1).

**Option 2 — Use your own certificate**
If your organization already has a certificate, choose this and provide the file
paths when asked:
- the **full-chain certificate** (your certificate plus any intermediates), and
- the matching **private key**.

A wildcard certificate (`*.example.com`) is fine.

---

## Step 5 — Log in

When the installer finishes, it prints your dashboard address and credentials.

1. Open **`https://<your-domain>`** in a browser (e.g. `https://go.example.com`).
2. Sign in with the **admin email** and **password** you entered.
3. You'll be asked to **set a new password** on first login.

Your credentials are also saved on the server at:
`/opt/netzilo/CREDENTIALS`

> The first time you open the dashboard, it may take a minute for the HTTPS
> certificate to be issued. If your browser shows a security warning, wait a
> minute and refresh.

---

## Optional — Unattended (scripted) install

To install without any prompts — for automation — put the answers in a file that only
`root` can read, run the installer with `--yes`, and delete the file afterwards. Do not
type the password on the command line: it would be saved in your shell history, and
passwords containing `'`, `$`, `` ` `` or `!` break there. Typing it at the hidden prompt
below and storing it with `printf '%q'` keeps any password intact.

```bash
umask 077
IFS= read -r -s -p 'Admin password: ' PW; echo
{
  printf '%s=%q\n' NETZILO_DOMAIN           go.example.com
  printf '%s=%q\n' NETZILO_PUBLIC_IP        203.0.113.10
  printf '%s=%q\n' NETZILO_ADMIN_FIRST_NAME 'John'
  printf '%s=%q\n' NETZILO_ADMIN_LAST_NAME  'Doe'
  printf '%s=%q\n' NETZILO_ADMIN_EMAIL      admin@example.com
  printf '%s=%q\n' NETZILO_ADMIN_PASSWORD   "$PW"
  printf '%s=%q\n' NETZILO_TLS_MODE         letsencrypt
} | sudo sh -c 'umask 077; cat > /root/netzilo-install.env'
unset PW

curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh -o install-netzilo.sh
sudo bash -c 'set -a; . /root/netzilo-install.env; set +a; NETZILO_ASSUME_YES=1 bash install-netzilo.sh --yes'
sudo rm -f /root/netzilo-install.env
```

To use your own certificate instead, replace the `NETZILO_TLS_MODE` line with:

```bash
  printf '%s=%q\n' NETZILO_TLS_MODE  provided
  printf '%s=%q\n' NETZILO_CERT_FILE /root/certs/fullchain.pem
  printf '%s=%q\n' NETZILO_KEY_FILE  /root/certs/privkey.pem
```

If someone else entered these values for you (for example through a support chat), add
`printf '%s=%q\n' NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED true` to the file: you will then
be asked to choose a new password at your first login.

---

## Managing your server

Everything is installed under **`/opt/netzilo`** and runs as Docker containers.
Run these from that directory:

```bash
cd /opt/netzilo

sudo docker compose ps          # see what's running
sudo docker compose logs -f     # follow logs (Ctrl-C to stop)
sudo docker compose restart     # restart the platform
sudo docker compose down        # stop the platform
sudo docker compose up -d       # start it again
```

**Back up:**

Nothing is backed up automatically. Your data is in the database volumes and in the
configuration files next to the compose file — `management.json`, `zitadel.env`,
`docker-compose.yml`, `Caddyfile`, `dashboard.env`, `turnserver.conf`, and your certificate
files if you provided your own. A backup that is missing any of these cannot be restored,
so use a backup that **fails closed**: it captures every one of them or reports failure
and exits non-zero. Netzilo support (or the operator who installed the server) will give
you the backup script and daily schedule; run it once by hand and check that it ends with
`BACKUP OK`. Keep copies off the server, and rehearse a restore onto a separate test
machine at least once — until a restore has been proven, you do not have a backup.

**Update to the latest version:**

Back up first (see "Back up" above). Then update one Netzilo component at a time and
check it before the next. Name the service; do not pull everything at once, because that
also moves the proxy, relay and cache to whatever their upstream latest happens to be.

```bash
cd /opt/netzilo
for s in zitadel management dashboard signal; do
  sudo docker compose pull "$s"
  sudo docker compose up -d --no-deps "$s"
  sudo docker compose ps "$s"            # wait for Up, then open the dashboard
done
```

Your data is in named volumes and in files next to this compose file; updating containers
does not touch it. Never add `-v` to `docker compose down`, and never re-run the installer
to update: both erase the server.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Browser shows a certificate warning | The HTTPS certificate hasn't been issued yet, or DNS isn't pointing here | Confirm `A` record → server IP, ports 80/443 open, then wait a minute and refresh |
| "Let's Encrypt will fail" warning during install | Domain doesn't resolve to this server yet | Fix the DNS `A` record (Step 1), then re-run the installer |
| Can't reach the dashboard at all | Firewall/security group blocking 80/443 | Open the ports in Step 1 |
| Clients sign in but cannot reach each other | Relay ports blocked (in the cloud firewall or on the server itself) | Open `3478/udp`, `49152–65535/udp` and `5349/tcp` (Step 1) |
| Password rejected during install | Doesn't meet the policy | Use 12+ chars with upper, lower, number, and a symbol |

To see what happened during install, check the logs:

```bash
sudo docker compose -f /opt/netzilo/docker-compose.yml logs
```

---

## Uninstall

To remove Netzilo Server completely (this deletes all data):

```bash
cd /opt/netzilo
sudo docker compose down --volumes
sudo rm -rf /opt/netzilo
```

---

## Need help?

Contact **support@netzilo.com** with your server's OS version and the output of
`sudo docker compose -f /opt/netzilo/docker-compose.yml ps`.
