---
id: '18'
title: Netzilo Server — Gate-Driven Install and Verification (Custom / On-Prem)
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 27123
sections:
- id: '0'
  title: Gather inputs from the user (mandatory — do not assume)
  chars: 2795
- id: '1'
  title: Pre-flight (run on the host)
  chars: 4131
- id: '2'
  title: Install (non-interactive)
  chars: 6200
- id: '3'
  title: Wait for completion
  chars: 1030
- id: '4'
  title: End-to-end verification
  chars: 3393
- id: '5'
  title: Login smoke test (optional but preferred)
  chars: 656
- id: '6'
  title: Diagnostics (when a gate fails)
  chars: 3018
- id: '7'
  title: Cleanup / teardown
  chars: 829
- id: '8'
  title: Success criteria (report this)
  chars: 1448
- id: appendix-a-provisioning-a-throwaway-test-vm
  title: Appendix A — Provisioning a throwaway test VM
  chars: 941
- id: appendix-b-environment-variables
  title: Appendix B — Environment variables
  chars: 1011
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

The gate flow below has been validated on a real Ubuntu 22.04 VM end to end. Run
the input-handling checklist in §2.4 once on a throwaway host before the first
customer install driven from this document, and again after any change to §2.

**Credentials arrive in chat.** There is no out-of-band channel: the customer
types the admin password into the conversation. Handle it as in §2 — never echo
it back (mask it when confirming), never place it on a command line or in a
generated script, keep it only in the `0600` env file the installer reads and
delete that file afterwards, and tell the customer it will be replaced at first
login.

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
| 1 | **How do I reach the server?** SSH host/IP and username, and where you can confirm its SSH host-key fingerprint (cloud console, provisioning record). | Yes | Reachable over SSH with passwordless `sudo`/root; fingerprint confirmable (§1.1) | `ubuntu@203.0.113.10` |
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

### 1.1 Verify and pin the host key (Gate 0)

Never use `StrictHostKeyChecking=no` or `UserKnownHostsFile=/dev/null`: the
install sends the admin password over this connection, so the host must be
authenticated first. Fetch the key, show the operator the fingerprint, and have
them confirm it against an independent source (the cloud console's serial log /
"get host key" output, `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` run
through the provider's console, or a fingerprint the customer recorded when the
VM was built). Only then pin it to a dedicated `known_hosts` file that every later
SSH call uses.

```bash
HOST=…; SSH_USER=…                              # from §0, item 1
KH="$HOME/.ssh/netzilo-install-$HOST.known_hosts"
umask 077; mkdir -p "$HOME/.ssh"
ssh-keyscan -T 10 -t ed25519,rsa -- "$HOST" 2>/dev/null > "$KH"
[ -s "$KH" ] || { echo "no host key received from $HOST"; exit 1; }
ssh-keygen -lf "$KH"                            # show the fingerprint(s) to the operator
```

**Gate 0 — host identity:** the operator has confirmed the fingerprint matches
the one shown by the provider or the customer. If they cannot confirm it, stop;
do not proceed on an unverified host. If a later call reports
`REMOTE HOST IDENTIFICATION HAS CHANGED`, stop and report — do not edit the
pinned file to make it pass.

Define one helper and use it for **every** remote command in this runbook; it
sends a single argument as the remote command, so quote each remote script as
one string:

```bash
rssh() { ssh -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$KH" \
             -o BatchMode=yes -o ConnectTimeout=15 -- "$SSH_USER@$HOST" "$@"; }
rssh 'echo ok; sudo -n true && echo "sudo ok"'   # both lines must print
```

`sudo -n true` must succeed: the install runs unattended and cannot answer a
sudo password prompt. If it fails, have the customer grant passwordless sudo for
the install window or run the runbook as `root`.

### 1.2 Environment (Gate 1)

```bash
rssh '
  . /etc/os-release; echo "OS=$PRETTY_NAME"
  echo "arch=$(uname -m)  nproc=$(nproc)"; free -h | awk "/Mem/{print \"RAM=\"\$2}"
  df -h / | awk "NR==2{print \"disk_avail=\"\$4}"
  ss -ltnup 2>/dev/null | grep -E ":(80|443|3478|5349) " || echo "ports 80/443/3478/5349 free"
'
```

**Gate 1 — environment:** OS is Ubuntu 20.04/22.04/24.04, arch `x86_64`, ≥ 2 CPU,
≥ 4 GB RAM, ≥ 20 GB free disk, and nothing already listens on 80, 443, 3478 or
5349. If not, stop and report.

**Firewall / ports.** Management and signal are served through Caddy on `443`;
the relay is a separate coturn container in **host network mode**, on its own
ports, so a host firewall (`ufw`, `firewalld`) applies to it as well as the cloud
security group / NSG. Inbound rules the host needs
(`02-server-operations.md` §11 is the reference):

| Inbound | Status | Why |
|---|---|---|
| `443/tcp` | **Required** | dashboard, API, management and signal, identity |
| `80/tcp` | **Required** with Let's Encrypt | ACME HTTP-01 validation and the HTTPS redirect |
| `3478/udp` | **Required** | STUN/TURN — the `stun:`/`turn:` addresses every client receives |
| `49152–65535/udp` | **Required for relayed connections** | coturn allocates each relayed session's address from this range; the AWS and Azure templates open it, and a self-managed host must too |
| `5349/tcp` | **Required** for clients on UDP-blocking networks | TURN over TLS fallback; completes only when a certificate is mounted into coturn (`02-server-operations.md` §8.4), which the Let's Encrypt mode does not do |
| `3478/tcp`, `5349/udp` | Optional | coturn listens but no client is given an address on them; the cloud templates open them, closing them breaks nothing |
| `22/tcp` | Admin source CIDR only | SSH |

Outbound `443/tcp` must reach `pkg.netzilo.com`, `ghcr.io`, Docker Hub and Let's
Encrypt. Never expose `6379` (Redis). Ask the customer to open the required rows
before §2; the gates in §4 do not test the relay ports, so a missing rule shows up
later as peers that connect to management but cannot reach each other
(`03-server-troubleshooting.md` §4a).

---

## 2. Install (non-interactive)

The installer runs unattended using **the values the user gave you in §0**. The
values are never interpolated into a remote command line, a heredoc or a
generated script: they travel once, over the authenticated SSH connection from
§1.1, into a root-only `0600` environment file that only bash sources, and that
file is deleted after the install. Every step checks its exit status.

### 2.1 Hold the values locally

Set the variables in **your** shell from the confirmed §0 answers. Read the
password with `read -r -s` rather than typing it into a command line, so it lands
neither in shell history nor in a process list:

```bash
set -euo pipefail
# All of these come from §0 (user-provided or user-confirmed) — none are defaults.
# HOST, SSH_USER and KH are already set from §1.1.
DOMAIN=…          PUBLIC_IP=…
ADMIN_FIRST=…     ADMIN_LAST=…
ADMIN_EMAIL=…
TLS_MODE=…        # letsencrypt | provided
CERT_FILE=…       KEY_FILE=…      # only for TLS_MODE=provided (paths on the host)
IFS= read -r -s -p 'Admin password (not echoed): ' ADMIN_PASSWORD; echo
```

Values may contain spaces, quotes, `$`, backticks, `!`, `#` or `;` — they are
carried verbatim by the steps below, so do **not** escape or trim them yourself.

### 2.2 Send the values as a root-only env file (via stdin)

`printf '%q'` shell-quotes each value; the remote `umask 077; cat` creates the
file as `0600 root:root` before a single byte is written. Nothing is written on
your machine, and the values never appear in a command line on either side.

```bash
{
  printf '%s=%q\n' NETZILO_DOMAIN            "$DOMAIN"
  printf '%s=%q\n' NETZILO_PUBLIC_IP         "$PUBLIC_IP"
  printf '%s=%q\n' NETZILO_ADMIN_FIRST_NAME  "$ADMIN_FIRST"
  printf '%s=%q\n' NETZILO_ADMIN_LAST_NAME   "$ADMIN_LAST"
  printf '%s=%q\n' NETZILO_ADMIN_EMAIL       "$ADMIN_EMAIL"
  printf '%s=%q\n' NETZILO_ADMIN_PASSWORD    "$ADMIN_PASSWORD"
  printf '%s=%q\n' NETZILO_TLS_MODE          "$TLS_MODE"
  printf '%s=%q\n' NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED true
  if [ "$TLS_MODE" = provided ]; then
    printf '%s=%q\n' NETZILO_CERT_FILE "$CERT_FILE"
    printf '%s=%q\n' NETZILO_KEY_FILE  "$KEY_FILE"
  fi
} | rssh 'sudo -n sh -c "umask 077; cat > /root/netzilo-install.env" && sudo -n stat -c "%a %U %s bytes" /root/netzilo-install.env'
unset ADMIN_PASSWORD
```

Expected: one line `600 root <n> bytes`. Anything else — stop; the pipeline's exit
status is non-zero under `set -o pipefail`.

`NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED=true` makes the identity provider force a
new password at the admin's first login. Set it whenever the password reached
you through chat or any other channel you do not control: the value in the env
file then never becomes the long-lived admin password.

### 2.3 Write the runner (no secrets in it) and launch

The runner is a fixed script; the quoted heredoc (`<<'EOF'`) means nothing is
expanded while writing it, and it contains no customer values. It sources the env
file with `set -a` so every variable is exported to the installer, downloads the
wrapper to a file first (so a failed download is a failed step, not an empty
script piped into bash), and runs it with `--yes`.

```bash
rssh 'sudo -n sh -c "umask 077; cat > /root/run-install.sh"' <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
set -a; . /root/netzilo-install.env; set +a
export NETZILO_ASSUME_YES=1
curl -fsSL https://pkg.netzilo.com/download/install-netzilo.sh -o /root/install-netzilo.sh
bash /root/install-netzilo.sh --yes
EOF

rssh 'sudo -n bash -c "nohup bash /root/run-install.sh > /root/install.log 2>&1 & echo launched pid=\$!"'
```

Expected: `launched pid=<n>`. The install takes several minutes and must survive
the SSH session, hence `nohup … &`. Keep the redirect **inside** the `sudo bash -c`
string — redirecting from the outer (non-root) shell fails with *permission
denied*. The log is created by root with mode `0600`; keep it that way (§4 below
confirms it) because the installer prints the admin credentials at the end.

**Air-gapped / offline fallback:** if the host cannot fetch from
`pkg.netzilo.com`, download `install-netzilo.sh` (wrapper) and
`install_netzilo.sh` (engine) on a connected machine, `scp` both **to the same
directory** on the host over the pinned connection
(`scp -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$KH" …`), and replace the
`curl` line of the runner with a `cp` of the wrapper from that directory: the
wrapper uses the engine found next to itself instead of downloading it. The
images still have to be reachable, or loaded from disk as in
`01-server-install.md` §5.

### 2.4 Input-handling test checklist (run once on a throwaway host)

Before using this flow on a customer host, prove the value path is transparent
with a throwaway VM (Appendix A) and inputs that break naive quoting. Each item
must reach the installer byte-for-byte and the install must complete
(`Done. Netzilo is starting`); then sign in with exactly the password entered.

- [ ] First name and last name containing a **space** (`Anna Maria`, `van der Berg`)
- [ ] A name containing an **apostrophe** (`O'Neil`)
- [ ] Password containing a **single quote** and a **double quote**
- [ ] Password containing `$`, `$(`, `${` and a **backtick**
- [ ] Password containing `!` (history expansion) and `#` (comment character)
- [ ] Password containing `;`, `&`, `|` and a **trailing space**
- [ ] Password containing a **non-ASCII** character (`ü`, `€`)
- [ ] `TLS_MODE=provided` with cert/key paths containing a space
- [ ] After the install: `/root/netzilo-install.env` is gone, `/root/install.log`
      is `0600`, and `sudo grep -F -c -- 'Username : <email>' /opt/netzilo/CREDENTIALS`
      prints `1` (the email arrived intact; do not `cat` the file)
- [ ] Repeat once with `set -e` deliberately tripped (wrong `KEY_FILE` path):
      the run must stop at the failing step, `install.log` must show the error,
      and nothing may be reported as passed

Confirm what reached the identity provider by signing in with the exact
password; if sign-in fails while the log shows success, the mismatch is in the
value path, not on the customer's side — do not ask them to "try another
password".

---

## 3. Wait for completion

Poll the log until the completion marker or an error appears (up to ~10 min):

```bash
rssh 'for i in $(seq 1 40); do
        sudo -n grep -qE "Done\. Netzilo is starting" /root/install.log && { echo DONE; break; }
        sudo -n grep -qE "ERROR:|aborted" /root/install.log && { echo FAILED; break; }
        sleep 15
      done
      sudo -n grep -E "Done\. Netzilo is starting|ERROR:|WARN:|aborted" /root/install.log | tail -n 15'
```

**Gate 2 — install completed:** the log shows `Done. Netzilo is starting at https://<DOMAIN>`.
If it shows `ERROR:`/`aborted`, go to §6. Read the log with `grep` for the marker
lines as above, not with `tail`/`cat`: the installer prints the admin credentials
at the end of the log, and they must not be copied into the conversation.

As soon as Gate 2 passes (or fails), remove the env file — the installer has
consumed it and nothing else needs it:

```bash
rssh 'sudo -n rm -f /root/netzilo-install.env /root/run-install.sh && echo "env file removed"'
```

---

## 4. End-to-end verification

Run this verify block. Every check must pass.

```bash
D="$DOMAIN"

# 4a. Container health (run on the host)
rssh 'cd /opt/netzilo && sudo -n docker compose ps'

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
| **3** | `docker compose ps` | **9 services Up**: `caddy`, `coturn`, `dashboard`, `management`, `signal`, `zitadel`, `support-worker` (healthy), `postgres` (healthy), `redis` (healthy). Only 8 and no `support-worker` line = pre-worker engine; report it, the Assistant cannot be enabled on this install (`01-server-install.md` §1) |
| **4** | dashboard | `HTTP 200` |
| **5** | TLS cert | `issuer=… Let's Encrypt …`, and `notAfter` is in the future (waived if `TLS_MODE=provided`) |
| **6** | OIDC discovery | `HTTP 200`, `"issuer":"https://<DOMAIN>"` |
| **7** | dashboard app | `<title>Netzilo</title>` |
| **8** | credentials written, secrets contained | `/opt/netzilo/CREDENTIALS` exists and is `600`; `/root/install.log` is `600`; `/root/netzilo-install.env` is gone |

Credentials check — test for presence and mode, never print the file (it holds
the admin password; the customer reads it on the host themselves):
```bash
rssh 'sudo -n stat -c "%n %a" /opt/netzilo/CREDENTIALS /opt/netzilo/netzilo-state.env /root/install.log;
      sudo -n test ! -e /root/netzilo-install.env && echo "env file absent"'
# expected: three lines ending in 600 (chmod 600 any that is not), then "env file absent"
```

> The Let's Encrypt certificate is issued on the **first HTTPS request** and can
> take up to ~60 s. If Gate 4/5 fails immediately after install, wait 60 s and
> retry once before diagnosing. A brief `502`/timeout right after start is the
> normal cert-issuance / warm-up window, not a failure.

**All gates green ⇒ the server is installed and login-ready.** Report the
dashboard URL and that gates 0–8 passed. Tell the customer that the admin
password they gave you is to be treated as exposed (it passed through chat):
the first login forces a new one (`NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED=true`
in §2.2), and they should not reuse it anywhere.

**Relay ports are not covered by these gates.** Gates 3–8 prove the web path
(443/80). Whether `3478/udp`, `49152–65535/udp` and `5349/tcp` are open is proven
only by the first two clients connecting, or by the relay checks in
`03-server-troubleshooting.md` §4a.3 — run them if the customer manages their own
firewall rather than a marketplace template.

**Backups are not set up by the installer.** Before handing over, install the
fail-closed backup script and schedule from `02-server-operations.md` §6.2–6.3,
run it once by hand (it must end with `BACKUP OK`; it exits non-zero and marks the
run `.FAILED` if any required artifact is missing), and agree a date for the
isolated restore rehearsal (§6.4) — a customer is not disaster-recovery ready
until one has passed.

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
# Filter the install log: its last lines carry the admin credentials.
rssh 'sudo -n grep -vE "Password *:" /root/install.log | tail -n 60; echo "--- firstboot ---"; sudo -n tail -n 40 /var/log/netzilo-firstboot.log 2>/dev/null'
rssh 'cd /opt/netzilo && sudo -n docker compose ps && echo "--- caddy ---" && sudo -n docker compose logs --tail=40 caddy'
```

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Install log has `ERROR: password must contain …` | Weak admin password | Use 12+ chars incl. upper/lower/number/symbol; re-run |
| Install log warns DNS mismatch, then LE fails | `DOMAIN` doesn't resolve to `PUBLIC_IP` | Fix DNS `A` record (or use `<ip>.nip.io`); re-run |
| Gate 5: cert `issuer` is not Let's Encrypt / self-signed | LE could not validate (ports 80/443 blocked, DNS, or rate limit) | Confirm 80/443 open + DNS; if rate-limited, set `NETZILO_TLS_MODE=provided` (self-signed) and waive Gate 5 |
| Gate 4: `HTTP 000`/timeout | Ports 80/443 not open, or still warming up | Open ports; wait 60 s; retry once |
| Gate 3: a container `Restarting`/`Exit` | That service crashed | `sudo docker compose logs <svc>` — read the error |
| `management`/`zitadel` unhealthy | DB not ready or bad config | `sudo docker compose logs management zitadel postgres` |
| One-liner fetch fails (`curl: (22)`/`(6)` in the log, runner stopped there) | CDN unreachable or offline host | Use the air-gapped fallback in §2.3 (copy both scripts) |
| Runner stops before the installer starts, log is empty or `No such file` | `/root/netzilo-install.env` missing (removed early, or §2.2 failed silently without `pipefail`) | Re-run §2.2 and §2.3 in order; check the `600 root … bytes` line |
| Log shows `ERROR: admin first and last name are required.` although both were given | value path broke on a special character (§2.4 not run) | Teardown (§7), re-run §2.2 with the `printf '%q'` block exactly as written — never a hand-built heredoc |
| `Host key verification failed.` | pinned key does not match, or `KH` not exported to this shell | Re-run §1.1 and have the operator confirm the fingerprint again; if it **changed**, stop and report |
| Peers reach the dashboard and management but cannot connect to each other | relay ports closed (`3478/udp`, `49152–65535/udp`, `5349/tcp`) or host firewall blocking coturn | Open them per §1.2; verify with `03-server-troubleshooting.md` §4a.3 |

**Re-running the installer is DESTRUCTIVE.** The installer detects an existing
install (by `docker-compose.yml` / `zitadel.env` in `/opt/netzilo`) and, because the
wrapper always runs with `NETZILO_ASSUME_YES=1`, it **wipes all containers, volumes
(including the Postgres database) and config without asking**. Only re-run on a
throwaway host or after an intentional teardown (§7) with the customer's explicit
consent. Never re-run it to "repair" a server that holds data — see
`02-server-operations.md` §10.

---

## 7. Cleanup / teardown

**Remove the install but keep the host** (only on a throwaway host, or with the
customer's explicit consent after the backup gate in `02-server-operations.md`
§6.3 — this deletes all data):
```bash
rssh 'cd /opt/netzilo && sudo -n docker compose down --volumes; sudo -n rm -rf /opt/netzilo /root/run-install.sh /root/install-netzilo.sh /root/netzilo-install.env /root/install.log && echo "teardown done"'
```

**Throwaway cloud VM:** delete the whole resource group / instance you created
for the test (do not leave it running — it costs money and exposes ports).
Verify deletion afterward.

**On your own machine:** remove the pinned host-key file for a host that no longer
exists (`rm -f "$KH"`) and make sure no shell variable still holds the password
(`unset ADMIN_PASSWORD` was run in §2.2).

---

## 8. Success criteria (report this)

Report PASS only if **all** are true:

- [ ] Gate 0 — host key fingerprint confirmed by the operator and pinned; no `StrictHostKeyChecking=no` used
- [ ] Gate 1 — host meets Ubuntu + sizing requirements; nothing else on 80/443/3478/5349
- [ ] Gate 2 — installer completed (`Done. Netzilo is starting …`); `/root/netzilo-install.env` removed
- [ ] Gate 3 — all 9 containers Up (postgres + redis + support-worker healthy)
- [ ] Gate 4 — dashboard returns HTTP 200
- [ ] Gate 5 — trusted Let's Encrypt cert (or explicitly waived for self-signed)
- [ ] Gate 6 — OIDC discovery 200 with correct issuer
- [ ] Gate 7 — dashboard serves `<title>Netzilo</title>`
- [ ] Gate 8 — `/opt/netzilo/CREDENTIALS` present and `600`; `/root/install.log` `600`; no credential printed into the conversation
- [ ] Firewall — required inbound rows of §1.2 confirmed open by the customer (`3478/udp`, `49152–65535/udp`, `5349/tcp`, plus 80/443)
- [ ] Backup — fail-closed script installed and first run ended `BACKUP OK`; restore rehearsal date agreed (`02-server-operations.md` §6.2–6.4), or the customer declined in writing
- [ ] Password rotation — customer told the chat-supplied password is exposed and will be replaced at first login
- [ ] Teardown done (if this was a throwaway test)

If any gate did not pass, report which one, the evidence (command output), and
your diagnosis. Never claim success on unverified gates.

---

## Appendix A — Provisioning a throwaway test VM

If you must create the test host yourself (any cloud works). Tips learned in
practice:

- **Ubuntu 22.04 LTS**, `x86-64`, a size with ≥ 2 vCPU / 8 GB (e.g. AWS
  `t3.large`, Azure `Standard_D2s_v5`/`_v7`).
- Open inbound `22/tcp` (your address only), `80/tcp`, `443/tcp`, `3478/udp`,
  `5349/tcp` and `49152–65535/udp` (§1.2). Record the VM's SSH host-key
  fingerprint from the provider's console right after creation — that is what
  Gate 0 (§1.1) is confirmed against.
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
| `NETZILO_ADMIN_PASSWORD` | Admin password (12+ chars, mixed classes); pass it only through the `0600` env file of §2.2 |
| `NETZILO_ADMIN_PASSWORD_CHANGE_REQUIRED` | `true` forces a new password at the admin's first login (passed through by the wrapper to the engine); set it whenever the password was supplied through chat |
| `NETZILO_TLS_MODE` | `letsencrypt` (default) or `provided` |
| `NETZILO_CERT_FILE` / `NETZILO_KEY_FILE` | Cert + key paths when `TLS_MODE=provided` |
| `NETZILO_INSTALLER_URL` | Override core-installer source (testing/air-gapped) |
| `NETZILO_STATE_DIR` | Install location (default `/opt/netzilo`) |
