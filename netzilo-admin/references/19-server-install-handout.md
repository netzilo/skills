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

Make sure your server / cloud security group allows inbound traffic on:

| Port(s) | Protocol | Purpose |
|---------|----------|---------|
| `80` | TCP | HTTPS certificate validation + redirect to HTTPS |
| `443` | TCP | Dashboard, API, and login (all web traffic) |
| `3478` | TCP & UDP | Secure networking (STUN/TURN) |
| `5349` | TCP & UDP | Secure networking over TLS (TURN/TLS) |
| `22` | TCP | SSH — your own administrative access |

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

To install without any prompts — for automation — set the answers as environment
variables and pass `--yes`:

```bash
curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh -o install-netzilo.sh
sudo NETZILO_ASSUME_YES=1 \
     NETZILO_DOMAIN=go.example.com \
     NETZILO_PUBLIC_IP=203.0.113.10 \
     NETZILO_ADMIN_FIRST_NAME=John \
     NETZILO_ADMIN_LAST_NAME=Doe \
     NETZILO_ADMIN_EMAIL=admin@example.com \
     NETZILO_ADMIN_PASSWORD='ChangeMe!2026' \
     NETZILO_TLS_MODE=letsencrypt \
     bash install-netzilo.sh --yes
```

To use your own certificate instead, replace the last two lines with:

```bash
     NETZILO_TLS_MODE=provided \
     NETZILO_CERT_FILE=/root/certs/fullchain.pem \
     NETZILO_KEY_FILE=/root/certs/privkey.pem \
     bash install-netzilo.sh --yes
```

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

**Update to the latest version:**

```bash
cd /opt/netzilo
sudo docker compose pull        # fetch the newest images
sudo docker compose up -d       # apply them
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Browser shows a certificate warning | The HTTPS certificate hasn't been issued yet, or DNS isn't pointing here | Confirm `A` record → server IP, ports 80/443 open, then wait a minute and refresh |
| "Let's Encrypt will fail" warning during install | Domain doesn't resolve to this server yet | Fix the DNS `A` record (Step 1), then re-run the installer |
| Can't reach the dashboard at all | Firewall/security group blocking 80/443 | Open the ports in Step 1 |
| Clients can connect but relaying fails | TURN ports blocked | Open `3478` and `5349` (Step 1) |
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
