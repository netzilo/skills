---
id: '18'
title: Netzilo Server — Gate-Driven Install and Verification (Custom / On-Prem)
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 14246
sections:
- id: '0'
  title: Gather inputs from the user (mandatory — do not assume)
  chars: 2657
- id: '1'
  title: Pre-flight (run on the host)
  chars: 863
- id: '2'
  title: Install (non-interactive)
  chars: 1892
- id: '3'
  title: Wait for completion
  chars: 607
- id: '4'
  title: End-to-end verification
  chars: 1888
- id: '5'
  title: Login smoke test (optional but preferred)
  chars: 656
- id: '6'
  title: Diagnostics (when a gate fails)
  chars: 1951
- id: '7'
  title: Cleanup / teardown
  chars: 413
- id: '8'
  title: Success criteria (report this)
  chars: 739
- id: appendix-a-provisioning-a-throwa
  title: Appendix A — Provisioning a throwaway test VM
  chars: 717
- id: appendix-b-environment-variables
  title: Appendix B — Environment variables
  chars: 756
---
# Netzilo Server — Gate-Driven Install and Verification (Custom / On-Prem)

**Audience:** an AI agent instructed to install the custom (bring-your-own-server)
Netzilo Server on a Linux host and prove it works end to end.

**Contract:** follow this runbook top to bottom. Each **Gate** has an explicit
expected result — do not report success until every gate passes. If a gate
fails, go to **§6 Diagnostics**, apply the fix, and re-run the gate. Report the
final state honestly, including any gate that did not pass and why.

**Do NOT assume or invent parameter values.** Before installing, you MUST
explicitly prompt the user for every required input in §0 and wait for their
answers. Values shown in this document (e.g. `John`, `admin@example.com`,
`ChangeMe!2026`) are **format examples only** — never use them as defaults.
The single exception is values you can *derive from the host itself* (the public
IP, and a `nip.io` domain built from it) — and even then, show the derived value
to the user and let them override it.

Everything below has been validated on a real Ubuntu 22.04 VM end to end.

---

## 0. Gather inputs from the user (mandatory — do not assume)

**Stop and ask the user for the following before doing anything else.** Prompt
for each value, wait for the answer, then echo the full set back and get explicit
confirmation to proceed. Do not fall back to defaults or placeholders. The only
values you may pre-fill are ones derived from the host (see the notes), and even
those must be shown for confirmation or override.

Ask the user for each of these:

| # | Prompt to the user | Required? | Validation | Example format (NOT a default) |
|---|--------------------|-----------|------------|-------------------------------|
| 1 | **How do I reach the server?** SSH host/IP and username. | Yes | Reachable over SSH with `sudo`/root | `ubuntu@203.0.113.10` |
| 2 | **What domain (FQDN) should the server use?** Or reply `auto` to use a `nip.io` name derived from the server's public IP. | Yes | Valid FQDN, or `auto` | `go.example.com` / `auto` |
| 3 | **HTTPS mode:** trusted Let's Encrypt, or your own certificate? | Yes | `letsencrypt` or `provided` | `letsencrypt` |
| 3a | *(only if `provided`)* Paths to the full-chain cert and private key. | Cond. | Files exist on the host | `/root/fullchain.pem`, `/root/privkey.pem` |
| 4 | **Admin first name** | Yes | non-empty | `John` |
| 5 | **Admin last name** | Yes | non-empty | `Doe` |
| 6 | **Admin email (this is the login username)** | Yes | valid email | `admin@example.com` |
| 7 | **Admin password** | Yes | ≥12 chars incl. upper, lower, number, symbol | — |

**Derived values (show to the user, allow override — never silently assume):**
- `PUBLIC_IP` — auto-detect from the host once connected
  (`curl -s ifconfig.me` or the cloud metadata service). Confirm it with the user.
- If the user answered `auto` for the domain, set `DOMAIN="${PUBLIC_IP}.nip.io"`
  (nip.io resolves `<ip>.nip.io` to that IP automatically, so Let's Encrypt works
  with **zero DNS setup**). Tell the user the exact `nip.io` name you will use.

**If the user gave a real FQDN:** its `A` record must point at `PUBLIC_IP` before
installing. Verify with `getent hosts "$DOMAIN"`; if it doesn't resolve to
`PUBLIC_IP`, tell the user and wait — do not proceed and let Let's Encrypt fail.

**Confirmation gate:** echo back the full parameter set (mask the password) and
ask the user to confirm. Only proceed to §1 after an explicit "yes".

> ⚠️ `nip.io` shares Let's Encrypt rate limits. If cert issuance fails with a
> rate-limit error, ask the user whether to retry later or fall back to
> `provided` mode with a self-signed cert (see §6) — the stack still comes up;
> only the trusted-cert gate is waived.

---

## 1. Pre-flight (run on the host)

SSH in and confirm the environment. Inline all SSH options (some shells don't
word-split a quoted options variable):

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_USER@$HOST" '
  . /etc/os-release; echo "OS=$PRETTY_NAME"
  echo "arch=$(uname -m)  nproc=$(nproc)"; free -h | awk "/Mem/{print \"RAM=\"\$2}"
  df -h / | awk "NR==2{print \"disk_avail=\"\$4}"
'
```

**Gate 1 — environment:** OS is Ubuntu 20.04/22.04/24.04, arch `x86_64`, ≥ 2 CPU,
≥ 4 GB RAM, ≥ 20 GB free disk. If not, stop and report.

**Firewall / ports.** The host must accept **inbound** `80`, `443`, `3478`
(TCP+UDP), `5349` (TCP+UDP), and `22`. (The coturn relay range `49152–65535/UDP`
does **not** need an inbound rule.) On a cloud VM, open these in the security
group / NSG. Outbound `443` must reach the internet.

---

## 2. Install (non-interactive)

The installer runs unattended using **the values the user gave you in §0**. Set
these shell variables from the confirmed user input first — do not hardcode them:

```bash
# All of these come from §0 (user-provided or user-confirmed) — none are defaults.
HOST=…            SSH_USER=…
DOMAIN=…          PUBLIC_IP=…
ADMIN_FIRST=…     ADMIN_LAST=…
ADMIN_EMAIL=…     ADMIN_PASSWORD=…
TLS_MODE=…        # letsencrypt | provided
```

Then run the installer in the background on the host:

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_USER@$HOST" "
  sudo bash -c 'cat > /root/run-install.sh <<EOF
export NETZILO_ASSUME_YES=1
export NETZILO_DOMAIN=$DOMAIN
export NETZILO_PUBLIC_IP=$PUBLIC_IP
export NETZILO_ADMIN_FIRST_NAME=$ADMIN_FIRST
export NETZILO_ADMIN_LAST_NAME=$ADMIN_LAST
export NETZILO_ADMIN_EMAIL=$ADMIN_EMAIL
export NETZILO_ADMIN_PASSWORD=$ADMIN_PASSWORD
export NETZILO_TLS_MODE=$TLS_MODE
curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh | bash -s -- --yes
EOF'
  sudo bash -c 'nohup bash /root/run-install.sh > /root/install.log 2>&1 & echo launched pid=\$!'
"
```

For `TLS_MODE=provided`, also export `NETZILO_CERT_FILE` and `NETZILO_KEY_FILE`
(the paths the user gave in §0-3a) inside the heredoc.

Notes:
- Run the installer in the **background** (`nohup … &`) writing to `/root/install.log`;
  the install takes several minutes and must survive the SSH session.
- Do the redirect **inside** `sudo bash -c '… > /root/install.log …'` — redirecting
  from the outer (non-root) shell fails with *permission denied*.
- **Air-gapped / offline fallback:** copy both scripts to the host and run the
  wrapper locally (it finds the core next to it, no download):
  `scp marketplace/custom/install-netzilo.sh marketplace/aws/install_netzilo.sh $SSH_USER@$HOST:` then run the wrapper with the same env vars.

---

## 3. Wait for completion

Poll the log until the completion marker or an error appears (up to ~10 min):

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_USER@$HOST" \
  "for i in \$(seq 1 40); do
     sudo grep -qE 'Done\. Netzilo is starting' /root/install.log && { echo DONE; break; }
     sudo grep -qE 'ERROR:|aborted' /root/install.log && { echo FAILED; break; }
     sleep 15
   done
   sudo tail -n 15 /root/install.log"
```

**Gate 2 — install completed:** the log shows `Done. Netzilo is starting at https://<DOMAIN>`.
If it shows `ERROR:`/`aborted`, go to §6.

---

## 4. End-to-end verification

Run this verify block. Every check must pass.

```bash
D="$DOMAIN"

# 4a. Container health (run on the host)
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_USER@$HOST" \
  "cd /opt/netzilo && sudo docker compose ps"

# 4b–4e. Web-facing checks (run from anywhere that can resolve $D)
curl -sS -o /dev/null -w "dashboard  -> HTTP %{http_code}\n" "https://$D/"
curl -sS -o /dev/null -w "oidc       -> HTTP %{http_code}\n" "https://$D/.well-known/openid-configuration"
curl -sS "https://$D/.well-known/openid-configuration" | grep -o '"issuer":"[^"]*"'
curl -sS "https://$D/" | grep -oiE '<title>[^<]*</title>'
echo | openssl s_client -connect "$D:443" -servername "$D" 2>/dev/null \
  | openssl x509 -noout -issuer -dates
```

| Gate | Check | Expected |
|------|-------|----------|
| **3** | `docker compose ps` | **8 services Up**: `caddy`, `coturn`, `dashboard`, `management`, `signal`, `zitadel`, `postgres` (healthy), `redis` (healthy) |
| **4** | dashboard | `HTTP 200` |
| **5** | TLS cert | `issuer=… Let's Encrypt …`, and `notAfter` is in the future (waived if `TLS_MODE=provided`) |
| **6** | OIDC discovery | `HTTP 200`, `"issuer":"https://<DOMAIN>"` |
| **7** | dashboard app | `<title>Netzilo</title>` |
| **8** | credentials written | `/opt/netzilo/CREDENTIALS` exists |

Credentials check:
```bash
ssh … "$SSH_USER@$HOST" "sudo test -f /opt/netzilo/CREDENTIALS && sudo cat /opt/netzilo/CREDENTIALS"
```

> The Let's Encrypt certificate is issued on the **first HTTPS request** and can
> take up to ~60 s. If Gate 4/5 fails immediately after install, wait 60 s and
> retry once before diagnosing. A brief `502`/timeout right after start is the
> normal cert-issuance / warm-up window, not a failure.

**All gates green ⇒ the server is installed and login-ready.** Report the
dashboard URL and that gates 1–8 passed.

---

## 5. Login smoke test (optional but preferred)

Confirms the identity path works, not just that pages load:

```bash
# Zitadel OIDC token endpoint should be advertised and reachable
TOKEN_EP=$(curl -sS "https://$D/.well-known/openid-configuration" | grep -o '"token_endpoint":"[^"]*"' | cut -d'"' -f4)
curl -sS -o /dev/null -w "token endpoint -> HTTP %{http_code}\n" "$TOKEN_EP"   # expect 200/405, NOT 000/5xx
```

Full UI login (admin email + password → forced password change) requires a
browser; if a browser tool is available, drive it and confirm the dashboard
loads post-login. Otherwise gates 6–7 are sufficient evidence of login-readiness.

---

## 6. Diagnostics (when a gate fails)

Work from the symptom. Always gather context first:

```bash
ssh … "$SSH_USER@$HOST" "sudo tail -n 60 /root/install.log; echo '--- firstboot ---'; sudo tail -n 40 /var/log/netzilo-firstboot.log 2>/dev/null"
ssh … "$SSH_USER@$HOST" "cd /opt/netzilo && sudo docker compose ps && echo '--- caddy ---' && sudo docker compose logs --tail=40 caddy"
```

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Install log has `ERROR: password must contain …` | Weak admin password | Use 12+ chars incl. upper/lower/number/symbol; re-run |
| Install log warns DNS mismatch, then LE fails | `DOMAIN` doesn't resolve to `PUBLIC_IP` | Fix DNS `A` record (or use `<ip>.nip.io`); re-run |
| Gate 5: cert `issuer` is not Let's Encrypt / self-signed | LE could not validate (ports 80/443 blocked, DNS, or rate limit) | Confirm 80/443 open + DNS; if rate-limited, set `NETZILO_TLS_MODE=provided` (self-signed) and waive Gate 5 |
| Gate 4: `HTTP 000`/timeout | Ports 80/443 not open, or still warming up | Open ports; wait 60 s; retry once |
| Gate 3: a container `Restarting`/`Exit` | That service crashed | `sudo docker compose logs <svc>` — read the error |
| `management`/`zitadel` unhealthy | DB not ready or bad config | `sudo docker compose logs management zitadel postgres` |
| One-liner fetch fails | CDN unreachable or offline host | Use the air-gapped fallback in §2 (copy both scripts) |

**Re-running the installer is DESTRUCTIVE.** The installer detects an existing
install (by `docker-compose.yml` / `zitadel.env` in `/opt/netzilo`) and, because the
wrapper always runs with `NETZILO_ASSUME_YES=1`, it **wipes all containers, volumes
(including the Postgres database) and config without asking**. Only re-run on a
throwaway host or after an intentional teardown (§7) with the customer's explicit
consent. Never re-run it to "repair" a server that holds data — see
`02-server-operations.md` §10.

---

## 7. Cleanup / teardown

**Remove the install but keep the host:**
```bash
ssh … "$SSH_USER@$HOST" "cd /opt/netzilo && sudo docker compose down --volumes; sudo rm -rf /opt/netzilo /root/run-install.sh /root/install.log"
```

**Throwaway cloud VM:** delete the whole resource group / instance you created
for the test (do not leave it running — it costs money and exposes ports).
Verify deletion afterward.

---

## 8. Success criteria (report this)

Report PASS only if **all** are true:

- [ ] Gate 1 — host meets Ubuntu + sizing requirements
- [ ] Gate 2 — installer completed (`Done. Netzilo is starting …`)
- [ ] Gate 3 — all 8 containers Up (postgres + redis healthy)
- [ ] Gate 4 — dashboard returns HTTP 200
- [ ] Gate 5 — trusted Let's Encrypt cert (or explicitly waived for self-signed)
- [ ] Gate 6 — OIDC discovery 200 with correct issuer
- [ ] Gate 7 — dashboard serves `<title>Netzilo</title>`
- [ ] Gate 8 — `/opt/netzilo/CREDENTIALS` present
- [ ] Teardown done (if this was a throwaway test)

If any gate did not pass, report which one, the evidence (command output), and
your diagnosis. Never claim success on unverified gates.

---

## Appendix A — Provisioning a throwaway test VM

If you must create the test host yourself (any cloud works). Tips learned in
practice:

- **Ubuntu 22.04 LTS**, `x86-64`, a size with ≥ 2 vCPU / 8 GB (e.g. AWS
  `t3.large`, Azure `Standard_D2s_v5`/`_v7`).
- Open inbound `22, 80, 443, 3478, 5349`.
- Set `DOMAIN="<public-ip>.nip.io"` so Let's Encrypt works with no DNS.
- **Azure gotchas:** the `az vm create` command may crash in some CLI builds —
  deploy via a small ARM template + `az deployment group create` instead. VM
  sizes are often capacity-restricted per region; probe with
  `az deployment group validate` across sizes/regions and pick one that passes.
- Always delete the VM/resource group when done.

## Appendix B — Environment variables

| Variable | Purpose |
|----------|---------|
| `NETZILO_ASSUME_YES=1` | Skip all confirmation prompts |
| `NETZILO_DOMAIN` | FQDN to serve on (must resolve to the host) |
| `NETZILO_PUBLIC_IP` | Host public IPv4 |
| `NETZILO_ADMIN_FIRST_NAME` / `_LAST_NAME` | Admin name (use placeholders) |
| `NETZILO_ADMIN_EMAIL` | Admin login username |
| `NETZILO_ADMIN_PASSWORD` | Admin password (12+ chars, mixed classes) |
| `NETZILO_TLS_MODE` | `letsencrypt` (default) or `provided` |
| `NETZILO_CERT_FILE` / `NETZILO_KEY_FILE` | Cert + key paths when `TLS_MODE=provided` |
| `NETZILO_INSTALLER_URL` | Override core-installer source (testing/air-gapped) |
| `NETZILO_STATE_DIR` | Install location (default `/opt/netzilo`) |
