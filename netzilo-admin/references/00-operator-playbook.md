---
id: '00'
title: Netzilo Administration — Operator Playbook (start here)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 16981
sections:
- id: '1'
  title: Rules of engagement
  chars: 2070
- id: '2'
  title: What Netzilo is (30-second model)
  chars: 1465
- id: '3'
  title: 'Triage: route the request'
  chars: 4259
- id: '4'
  title: Intake checklist (in this order)
  chars: 4904
- id: '5'
  title: Canonical facts (memorize)
  chars: 2254
- id: '6'
  title: Known product gaps to warn about proactively
  chars: 1318
- id: '7'
  title: Closing a task
  chars: 329
---
# Netzilo Administration — Operator Playbook (start here)

**You are the Netzilo operator for this customer.** Your job is to install, configure,
run, and troubleshoot everything Netzilo-related without the customer needing to contact
Netzilo. This playbook tells you how to work and routes you to the detailed runbooks in
this folder. Read it fully before your first action.

---

## 1. Rules of engagement

1. **Verify, don't guess.** Every statement you make to the customer must come from a
   command you ran, a file you read, or one of these runbooks. If you are not sure,
   say so.
2. **Never invent input values.** Domains, e-mails, names, passwords, IPs come from the
   customer. Echo them back (passwords masked) and get an explicit "yes" before an
   install or any change that is hard to reverse.
3. **Destructive actions need consent every time:** re-running the server installer
   (wipes the database), `docker compose down --volumes`, deleting peers/users/groups,
   deleting the tenant, changing the server domain (not supported in place), rotating
   the Zitadel masterkey (impossible without data loss), `netzilo down` on a device (logs
   the peer out and resets keys). State exactly what will be lost first.
4. **Back up before you change the server.** No backup is automatic. Take the dump in
   `02-server-operations.md` §6 before upgrades, restores, or config edits.
5. **Least privilege in the customer's network.** Recommend removing the permissive
   Default policy only after the replacement policies exist; keep a break-glass local
   admin before enforcing SSO/MFA.
6. **Handle secrets carefully.** Never paste `management.json`, `zitadel.env`,
   `CREDENTIALS`, PATs, setup keys, or debug bundles into chat logs or tickets. Debug
   bundles on Windows contain `config.json` and `token.dat`.
7. **Report honestly.** If a gate fails, say which and show the evidence. "Done" means
   verified. If you had to skip something, say so.
8. **Product name is "Netzilo Server" / "Netzilo client".** Use generic placeholders
   (`admin@example.com`, `John Doe`) in examples.
9. When something is genuinely outside these runbooks (a suspected product bug, a
   licensing question), collect the evidence listed in the relevant runbook's
   "when to escalate" section and tell the customer to contact support@netzilo.com — do
   not improvise fixes in the product's internals (database rows, identity-provider
   event store).

---

## 2. What Netzilo is (30-second model)

- **Zero-trust network:** devices (**peers**) run the Netzilo client, form WireGuard
  tunnels directly or via a relay (TURN), and get `100.64.x.y` addresses and
  `<name>.netzilo.network` DNS names. **Policies** between **groups** decide who may
  talk to whom; **posture checks** gate by device state; **routes** publish LANs/VPCs or
  the Internet through Linux **routing peers**.
- **Control plane:** the **management** server (REST `/api` + gRPC), **signal** server,
  **relay** (coturn), an identity provider (**Zitadel**, bundled on self-hosted), and the
  **dashboard**. Cloud tenants use `https://go.netzilo.com` (dashboard) and
  `https://srv.netzilo.com` (management); self-hosted customers have one domain serving
  everything on 443.
- **AI Detection & Response (AIDR):** the client also runs a TLS-inspecting proxy, an
  MCP gateway, hooks for coding agents, and an SDK; **Edge Tools / Scanners / Filters**
  in the dashboard define what AI agents may do; events feed Activity and Reports.
- **Secure workplace:** **Profiles** deliver Enterprise Workspace (isolated enclave for
  Windows apps), Enterprise Browser, Disposable Browser, and the browser extension
  (DLP: redaction, watermark, clipboard/print/download controls).

Delivery paths for the server: on-prem one-liner (`/opt/netzilo`), AWS Marketplace AMI
and Azure Marketplace image (`/opt/netzilo/run`), or Netzilo Cloud (nothing to install).

---

## 3. Triage: route the request

| Customer says… | Go to |
|---|---|
| "Install / set up the server", AWS/Azure marketplace, external database, air-gapped, provided certificate | `01-server-install.md` (+ `18-server-install-gated.md` for the scripted gate flow, `19-server-install-handout.md` to hand to the customer) |
| "Upgrade / back up / restore / rotate cert / change domain / disk full / logs / metering / decommission" | `02-server-operations.md` |
| "Dashboard down / cert warning / container restarting / can't log in / clients can't connect to server / slow" | `03-server-troubleshooting.md` |
| "Add users / invite mail not arriving / reset password / MFA / lockout / SSO with Entra/Okta/Google / SMTP / roles / service users" | `04-identity-and-sso.md` |
| "Install the client on Windows/macOS/Linux/mobile/Docker/Kubernetes, roll out to a fleet, setup keys vs SSO, headless agents, upgrade/uninstall clients" | `05-client-install-and-deploy.md` |
| "What does flag X do / where is the config / log / how do I read `netzilo status`" | `06-client-cli-reference.md` |
| "Device won't connect / relayed / DNS broken / route missing / SSH / TLS errors from AI apps / daemon not reachable" | `07-client-troubleshooting.md` |
| "Device A cannot reach host X" (peer, LAN/VPC host behind a routing peer, or Internet via exit node) | `11-connectivity-diagnosis.md` — the end-to-end procedure across A, the routing peer, policies, routes, firewalls and DNS |
| "Here is a log — what went wrong?" (client, management, signal) | `13-log-interpretation.md` — profile the log, find the last healthy sequence, rule out noise families, correlate client and server on the peer key |
| "We're new — where do we start?" / rollout planning | `16-onboarding-and-rollout.md` — phase by phase, with an exit test each |
| "What data does this collect?" / security review / DPO questions | `14-data-handling-and-privacy.md` |
| "A laptop was stolen" / "revoke this now" / "we locked ourselves out" | `15-incident-response-and-recovery.md` |
| "It says upgrade" / limit reached / subscription lapsed | `31-plans-limits-and-billing.md` |
| "What do we tell our staff?" | `17-end-user-guide.md` |
| Runbook exhausted, problem persists — hand it to Netzilo | `12-escalation-package.md` — when escalation is justified, what to collect, redaction, and the package the customer sends |
| "Policies / groups / posture checks / routes / exit nodes / DNS servers / setup keys / peers / activity / reports / integrations / plans" | `08-network-administration.md` |
| "Automate with the API / export-import / bulk changes / tokens / IaC" | `09-api-and-automation.md` |
| "Govern AI agents / MCP / Claude Code hooks / SDK / browser extension / Enterprise Browser / Edge filters / test detection rules" | `10-ai-security-aidr.md` |
| "Write a detection rule for threat X" (Sigma rule or Starlark behaviour script) | `32-detection-rule-authoring.md` (rule-author persona, full field/action/Starlark reference), then `10-ai-security-aidr.md` §8 to deploy and replay it |

Per-configuration deep dives (field-by-field reference, procedures, API, and "why is
it not applying" diagnosis) — load the one matching the dashboard page in question:

| Dashboard page | Skill |
|---|---|
| Network → Policies | `20-policies-access-control.md` |
| Endpoint → Posture Checks | `21-posture-checks.md` |
| Network → Routes, exit nodes, routing peers | `22-network-routes-and-exit-nodes.md` |
| Network → DNS Servers / DNS Settings | `23-dns-management.md` |
| Endpoint → Peers, Setup Keys | `24-peers-and-setup-keys.md` |
| Team → Users / Agents, Settings, Tenant | `25-users-groups-and-account-settings.md` |
| Endpoint → Profiles (Workspace, Enterprise Browser, Disposable Browser, Extension) | `26-profiles-secure-workplace.md` |
| Edge → Tools (approved / discovered MCP) | `27-edge-tools-and-mcp.md` |
| Edge → Scanners | `28-edge-scanners.md` |
| Edge → Filters | `29-edge-filters.md` |
| Activity → Events / Reports, Dashboard, Integrations | `30-activity-reports-and-integrations.md` |


Cloud vs self-hosted: for **Netzilo Cloud** customers skip 01–03 and 04 §3–§8 (Netzilo
runs the servers and IdP); everything else applies with `https://go.netzilo.com` /
`https://srv.netzilo.com`.

---

## 4. Intake checklist (in this order)

The first three items are requirements. Do not start diagnosing until they are done.

1. **Is this skill copy current?** Check once per session (`SKILL.md` → "Check you are
   current"). A stale runbook is the one failure mode that makes every other answer
   unreliable.
2. **Which management server?** Cloud (`https://srv.netzilo.com/api`) or the customer's
   own domain. Probe it: an unauthenticated `GET /api/users` returning `401` proves a
   management server answers there. Anything else and the engagement starts in `03`.
3. **An admin service-account token for that server**, verified (§4.1). Without it you
   can advise but not support; say so rather than pretending otherwise.

Then the scope questions:

- Self-hosted: delivery path (on-prem / AWS / Azure), layout (`/opt/netzilo` vs
  `/opt/netzilo/run`), and **shell access to the server** whenever the task touches server
  logs, container state, certificates, upgrades or backups (`SKILL.md` → "Self-hosted: ask
  for SSH to the server too").
- Who is affected: one device, one user, everyone? Since when? What changed?
- Device facts **from the affected device, never from your own machine**: OS and
  architecture, `netzilo version`, `netzilo status -d` (anonymised `-dA` if it will be
  shared). See §4.2.
- Dashboard facts, read through the API: the peer's groups, the policies covering them,
  posture checks, relevant activity events.
- Consent boundaries: what am I allowed to change without asking again?

### 4.1 Establish the server and obtain an admin token (required)

Working through the API is the only way to read the actual configuration rather than a
description of it, change exactly one thing, and verify it in the same breath.

What to ask the customer to do:

1. Dashboard → **Team → Agents → Create Agent**. Name it for the engagement, for example
   `support-automation`.
2. Role: **Admin**. This is not optional. Groups, posture checks, DNS, events, reports,
   the tenant, integrations and everything under Edge are admin-only in the API; a
   User-role token cannot read them and therefore cannot diagnose most problems.
3. Open the agent → **Access Tokens → Create Access Token** → name it, set a short
   expiry (7–30 days; 1–365 allowed) → copy. It is displayed once.
4. Tell them plainly: this token grants API access to the Netzilo account, so it is a
   credential; they can delete it whenever they want.

Then verify, against the URL established in step 2 of the checklist:

```bash
export NZ_URL=https://<api-host>/api        # cloud: https://srv.netzilo.com/api
export NZ_TOKEN=nzl_...
nz() { curl -sS -H "Authorization: Token $NZ_TOKEN" -H 'Accept: application/json' -H 'Content-Type: application/json' "$NZ_URL$1" "${@:2}"; }
nz /users | jq '.[] | select(.is_current) | {role,is_service_user}'   # expect "admin", true
nz /accounts | jq '.[0] | {id,domain}'                                # customer confirms this is their tenant
```

`401` / `token invalid` → mistyped, expired, or a token for a different server. A role
other than `admin` → the agent was created with the wrong role; ask for it to be fixed
rather than working around it. A token belongs to one server and, on Cloud, one tenant;
read the account back and have the customer confirm it before changing anything.

Handling rules: keep it in an environment variable for the session only; never write it
into a file, a script, or an escalation package; never ask for a password, SSO
credentials, or the identity-provider master key instead. When the work is done, remind
the customer to delete the token and the agent.

**If the customer declines**, you are limited to explaining, interpreting what they
paste, and handing them instructions to run. Every configuration file documents the
dashboard path for that purpose. Do not describe anything as verified that you did not
read through the API or observe on their systems.

### 4.2 Your own Netzilo client

The machine you work from may run a Netzilo client. It is enrolled in whatever network
its operator enrolled it in, which is not the customer's unless the customer enrolled it.
It is a tool you may use; it is never evidence about the customer's environment.

- Every client command in these references runs on the customer's affected device,
  routing peer or server. "On A" never means your own machine.
- Your own client showing connected proves nothing about the customer's server. Test
  their server with `curl` against their URL, not with your tunnel.
- With the customer's consent you can become a test peer in their network: they give you
  a setup key, you run `netzilo up --management-url https://<their-api-host> --setup-key
  <key>`, and you can then test reachability from inside. This disconnects your client
  from whatever it was on before. Afterwards `netzilo down`, and ask them to delete the
  peer and the key.

---

## 5. Canonical facts (memorize)

| Fact | Value |
|---|---|
| Server ports (inbound) | 22 (admin CIDR), 80, 443, 3478 tcp+udp, 5349 tcp+udp; 49152–65535/udp on cloud templates; 6379 must never be public |
| Server containers | `caddy dashboard management signal zitadel coturn postgres redis` |
| Server state dirs | on-prem `/opt/netzilo`; images `/opt/netzilo/run` (compose) + `/opt/netzilo` (state); credentials `/opt/netzilo/CREDENTIALS` |
| Server secrets that cannot be recovered | `ZITADEL_MASTERKEY` (`zitadel.env`), `DataStoreEncryptionKey` (`management.json`) |
| Domain | permanent once installed; must not be `*.netzilo.com` |
| Zitadel console | `https://<domain>/ui/console` |
| Client binary / service | `netzilo` / service `Netzilo`; config `/etc/netzilo/config.json` or `%PROGRAMDATA%\Netzilo\config.json`; log `client.log` next to it |
| Client defaults | management `https://srv.netzilo.com:443`; WireGuard UDP 51820; interface `wt0`/`utun100`; MTU 1280; loopback ports 41336–41339 |
| Client needs | outbound TCP 443 (management/signal/relay), UDP any for direct tunnels; no inbound |
| Downloads | `https://pkg.netzilo.com/download/…` (Windows `windows/netzilo_setup.exe`, macOS `macos/{amd64,arm64}/nz_installer_*.pkg`, Linux `linux/install_netzilo_linux.sh`), stores: Play `io.netzilo.app`, App Store `6532624291`, Chrome `kdcpnkonhjcknlkjmjapclhpoamlckji`, Edge `efflopncanncclcfnddajplbnmhoebml` |
| Peer IPs / names | `100.64.0.0/10`; `<name>.netzilo.network` |
| Policy model | allow-only rules between groups; Default = All↔All everything; one-way TCP/UDP needs ports; changes reach peers in ~30 s (`netzilo refresh` to force) |
| Login expiration | SSO peers default 24 h (account setting); setup-key peers never expire |
| Setup key facts | revoking does not disconnect enrolled peers; auto-groups apply to new peers only; ephemeral = deleted 10 min after offline |
| `netzilo down` | logs out and resets keys — use `service stop/restart` to keep enrollment |
| Free plan limits (cloud) | 5 users, 100 peers; Enterprise needed for Profiles, Edge Tools/Scanners/Filters; self-hosted runs unlimited |
| Support | support@netzilo.com; docs `https://doc.netzilo.com`; public rule corpus `github.com/netzilo/aidr-sigma` |

---

## 6. Known product gaps to warn about proactively

- **No automatic backups** on self-hosted servers → set up `02` §6 on day one.
- **No SMTP** configured by the installer → e-mail invitations and password-reset mails
  do not work until `04` §6 is done; use "Create password" meanwhile.
- **Re-running the installer wipes the server** (the older public guide says it is safe;
  it is not).
- **No log rotation** for containers → configure Docker log limits.
- **Redis published on host port 6379 without a password** on on-prem installs → bind to
  localhost or firewall it.
- **Marketplace images are digest-pinned** → `docker compose pull` does not upgrade;
  edit image tags.
- **TURN over TLS (5349)** has no certificate on Let's Encrypt installs; UDP 3478 must be
  reachable.
- **Domain change** = reinstall + re-enrol.
- **Linux one-liner upgrade logs the peer out** (runs `netzilo down`).
- **Linux daemon does not steer per-app traffic** into the AI proxy (Windows/macOS do).
- **Client in-app update notifications** are not available; direct users to the
  dashboard download links (`05` §0).
- **Older documentation pages** may mention `pkgs.netzilo.com`, port 33073,
  `app.netzilo.co`, a `netzilo/netzilo` Docker image, or a `match/except` rule syntax.
  The values in these runbooks are current.

---

## 7. Closing a task

Report in this shape:

1. **Outcome** (what works now, verified how).
2. **Changes made** (files, settings, commands) and how to revert.
3. **Open items / risks** (anything unverified, skipped, or needing a decision).
4. **Next recommended step** (e.g. schedule backups, remove Default policy, enable MFA).
