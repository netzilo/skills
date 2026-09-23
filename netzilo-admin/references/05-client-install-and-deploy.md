---
id: '05'
title: Netzilo Client — Installation, Enrollment and Fleet Deployment
requires:
- client-device
executable_on:
- netzilo-harness
- human-operator
chars: 24086
sections:
- id: '0'
  title: Facts you need before touching a device
  chars: 3683
- id: '1'
  title: Enrollment methods (decide first)
  chars: 1313
- id: '2'
  title: Windows
  chars: 3573
- id: '3'
  title: macOS
  chars: 1983
- id: '4'
  title: Linux
  chars: 2191
- id: '5'
  title: Mobile
  chars: 283
- id: '6'
  title: Containers and Kubernetes
  chars: 1554
- id: '7'
  title: Upgrading clients
  chars: 1413
- id: '8'
  title: Fleet deployment patterns
  chars: 2411
- id: '9'
  title: Post-install verification checklist
  chars: 646
- id: '10'
  title: What enrollment changes on the device
  chars: 1211
- id: '11'
  title: Platform details that cause first-install tickets
  chars: 2729
- id: '12'
  title: What Cloud customers must allow outbound
  chars: 718
---
# Netzilo Client — Installation, Enrollment and Fleet Deployment

**Audience:** an AI operator installing the Netzilo client on end-user devices and
servers, enrolling them (SSO, setup key, or PAT), deploying at scale, upgrading and
uninstalling.

Companion documents: `06-client-cli-reference.md` (every command and flag),
`07-client-troubleshooting.md` (symptom → fix).

---

## 0. Facts you need before touching a device

| Item | Value |
|---|---|
| Binary / CLI name | `netzilo` (GUI: `netzilo-ui`) |
| OS service name | `Netzilo` on Linux (systemd `Netzilo.service`), macOS (launchd `Netzilo`), Windows (SCM `Netzilo`) |
| Config file | Linux/macOS `/etc/netzilo/config.json`; Windows `%PROGRAMDATA%\Netzilo\config.json` |
| Log file | Linux/macOS `/var/log/netzilo/client.log` (5 MB × 10, 30 days, gzip); Windows `%PROGRAMDATA%\Netzilo\client.log` |
| Daemon socket | `unix:///var/run/netzilo.sock`; Windows `tcp://127.0.0.1:40836` |
| Default management URL | `https://srv.netzilo.com:443` (Netzilo Cloud). Self-hosted: `https://<your-domain>` |
| Default admin URL | `https://go.netzilo.com:443` (derived automatically from the management URL: `srv.` → `go.`; for self-hosted it equals the management host) |
| WireGuard interface / port | `wt0` (Linux, Windows), `utun100` (macOS); UDP `51820`; MTU fixed 1280 |
| Peer IP range | `100.64.0.0/10`; peer FQDN `<name>.netzilo.network` (cloud) or `<name>.<dns-domain>` set on the server |
| Local loopback ports the daemon opens | 41336 (local control HTTP), 41337 (WSS), 41338 (MCP gateway), 41339 (SOCKS5/HTTP proxy with TLS inspection), 40836 (Windows daemon gRPC); 17998/17999 on macOS (filter extension) |
| Outbound requirements | TCP 443 to the management/signal/relay hosts; UDP any (ideally) for direct peer connections; without UDP the client works via TURN over TCP/TLS |
| Inbound requirements | none |

Download URLs (base `https://pkg.netzilo.com`; a self-hosted dashboard may point to a
mirror via `NETZILO_PKG_BASE_URL`, same paths):

| Platform | URL |
|---|---|
| Windows online installer (downloads the package at install time) | `/download/windows/netzilo_setup.exe` |
| Windows x64 offline installer | `/download/windows/x64/nz_installer_64.exe` |
| Windows x64 MSI | `/download/windows/x64/netzilo_x64.msi` |
| macOS Intel pkg | `/download/macos/amd64/nz_installer_amd64.pkg` |
| macOS Apple Silicon pkg | `/download/macos/arm64/nz_installer_arm64.pkg` |
| Linux one-liner | `curl -fsSL https://pkg.netzilo.com/download/linux/install_netzilo_linux.sh \| sh` |
| Linux raw binary | `/download/linux/netzilo` (amd64) |
| Coding-agent hooks installer | `curl -fsSL https://pkg.netzilo.com/download/plugin/install.sh \| sh` |
| Android | Google Play `io.netzilo.app` |
| iOS | App Store id `6532624291` |
| Enterprise Browser (Windows / macOS / mobile) | `/download/windows/browser_setup.exe`, `/download/macos/{amd64,arm64}/NetziloEnterpriseBrowser_{amd64,arm64}.dmg`, Play `com.netzilo.browser2`, App Store id `6747919491` |
| Browser extension | Chrome Web Store `kdcpnkonhjcknlkjmjapclhpoamlckji`; Edge Add-ons `efflopncanncclcfnddajplbnmhoebml`; Firefox `netzilo-secure-browser`; Safari App Store id `6740890085` |

Both the dashboard (Peers → Add Peer, or `/install`) and the pages above show these
links; the dashboard auto-selects the visitor's OS. The dashboard's Linux snippet appends
`--management-url <grpc endpoint>` when the deployment configures one.

All URLs above were verified live (HTTP 200) at the time of writing. The management
server's `GET /api/getclient?os=…` redirect points at different filenames
(`windows/x64/netzilo_installer_amd64.exe`, `macos/*/netzilo_installer_*.pkg`) which
currently return **404** — do not hand out that endpoint; use the dashboard links.

Not available: an apt/yum repository, a Homebrew tap, a winget/choco package, or an
official Docker Hub image for the `netzilo` binary. Older documentation that mentions a
`netzilo/netzilo` Docker image or apt repository steps is out of date; do not promise
them. For containers see §6.

---

## 1. Enrollment methods (decide first)

| Method | Use when | How | Peer semantics |
|---|---|---|---|
| **SSO (interactive)** | user devices | `netzilo up` (or tray **Connect**) → browser login | peer is bound to the user; **login expiration** applies (account default 24 h, admin-configurable); inactivity expiration can apply |
| **Setup key** | servers, containers, IaC, kiosks | `netzilo up --setup-key <KEY>` | peer has no user; never expires by login; auto-assigned to the key's groups; `ephemeral` keys remove the peer 10 min after it goes offline |
| **PAT (personal access token)** | headless devices that must act as a user (AI agents, CI runners) | `netzilo up --pat nzl_…` or env `NETZILOPAT`, or `netzilo deploy-user` | peer bound to the token's user |

Self-hosted always add `--management-url https://<domain>` (the admin URL is derived).
The management URL is persisted in `config.json`; subsequent `netzilo up` needs no flags.

Setup keys are created in Dashboard → Endpoint → **Setup Keys** → **Create Setup Key**:
name, "Make this key reusable" (off = one-off), usage limit (blank = unlimited),
"This key expires" (1–365 days, default 7), "Ephemeral Peers", auto-assigned groups. The
key is shown once. Revoking or deleting a key **does not** disconnect peers already
enrolled with it.

---

## 2. Windows

Three installer forms deliver the same client (`40-windows-hosts.md` §2–3 has the full
behaviour):

| Form | File | Switches | Use |
|---|---|---|---|
| Online installer | `netzilo_setup.exe` | — | interactive install by a person with internet access; it downloads the package from `pkg.netzilo.com` at install time and fails offline with "failed to download installer." |
| Offline installer | `nz_installer_64.exe` | `-s` silent, `-na` non-admin mode | scripted pushes, machines without direct internet |
| MSI | `netzilo_x64.msi` | properties `NONADMIN=1`, `CONFIGFILE=<path>`; add `REBOOT=ReallySuppress` | Intune / SCCM / GPO software installation, in **device (system) context** |

Installers named `netzilo_setup_<name>.exe` / `netzilo_x64_<name>.msi` apply that tenant's
pre-seeded configuration at install time; the user only signs in.

**Interactive:** download, run, accept the UAC prompt. There is no need to "run as
Administrator": the installer starts unelevated and elevates itself. Files go to
`%ProgramData%\Netzilo Client\` (`netzilo.exe`, `netzilo-ui.exe`, `installer.exe`,
`nwfilter.exe`, `nzcontainer.exe`, drivers, `wintun.dll`); configuration and logs go to
`%ProgramData%\Netzilo\`. The `Netzilo` service and its drivers are installed and started,
the tray autostart is registered for the user, and the firewall rules `Netzilo` and
`Netzilo Client` are created. Nothing is added to `PATH`; use the full path to
`netzilo.exe`. An install that is denied elevation continues as a non-admin install (below).

**Silent (SCCM/Intune/GPO):**

```powershell
nz_installer_64.exe -s
msiexec /i netzilo_x64.msi /qn REBOOT=ReallySuppress
# then enroll servers/kiosks (elevated PowerShell); user devices sign in from the tray
& "$env:ProgramData\Netzilo Client\netzilo.exe" up --management-url https://<domain> --setup-key <KEY>
```

Deploy in device context: the MSI is per-user scoped and self-elevates, and a `SYSTEM`
deployment context has no user proxy, so the online installer is the wrong form for a
managed rollout. For user devices with SSO, let the user click **Connect** in the tray;
the installer starts the service, and the tray app starts at login.

**Non-admin install:** an unelevated install (or `-na` / `NONADMIN=1`) becomes non-admin
mode: a per-user client with userspace networking (no TUN adapter, no drivers, no
workspace, no AI network filter), a per-user daemon port, and
`%ProgramData%\netzilo\usservice<N>.json` / `.log` instead of `config.json` /
`client.log`. Switching non-admin → admin mode is a full uninstall followed by a fresh
install. ARM64 devices always get the network client only (no drivers, workspace or AI
network filter). Prefer elevated x64 installs.

**Verify:** `sc.exe query Netzilo` → RUNNING; `& "$env:ProgramData\Netzilo Client\netzilo.exe" status`.

**Uninstall:** Settings → Apps → Netzilo Client, or
`"%ProgramData%\Netzilo Client\installer.exe" -u` (silent: `-u -q`). This removes the
program files, services and drivers **and deletes `%ProgramData%\Netzilo`** (config, the
peer's identity, tokens, logs), `C:\Netzilo`, workspace containers, and
`HKLM\Software\Netzilo` / `HKCU\Software\Netzilo`. A reinstall therefore becomes a **new
peer**: SSO users sign in again, and the stale peer should be deleted in the dashboard.
Collect any logs you need before uninstalling. A failed install rolls back the same way.
If the `Netzilo Edge CA` root remains in the machine store afterwards
(`certutil -store Root "Netzilo Edge CA"`), remove it with
`certutil -delstore Root "Netzilo Edge CA"`.

---

## 3. macOS

**Interactive:** download the pkg for the chip (Apple menu → About This Mac; "Apple M…"
= arm64). Install. The pkg places `/Applications/Netzilo.app` (bundle id
`com.netzilo.client`, minimum macOS 12) with `Contents/MacOS/netzilo`, `netzilo-ui` and
`NetziloFilterManager.app` (system extensions `com.netzilo.NetziloFilter`,
`com.netzilo.NetziloSecurity`). The postinstall script runs
`service stop/uninstall/install/start` and appends
`export PATH="/Applications/Netzilo.app/Contents/MacOS:$PATH"` to the installing user's
`~/.zshrc` (or `~/.bashrc`), then launches the menu-bar app.

Consequences to tell users: open a **new** terminal before `netzilo` is on PATH, or use
the full path `/Applications/Netzilo.app/Contents/MacOS/netzilo`. Nothing is put in
`/usr/local/bin`. The first activation prompts to allow the system extension in
System Settings → General → Login Items & Extensions (Network Extensions); until
approved, per-app traffic interception is inactive (VPN connectivity still works).

**Silent (MDM):** `sudo installer -pkg nz_installer_arm64.pkg -target /`, then
`sudo /Applications/Netzilo.app/Contents/MacOS/netzilo up --management-url https://<domain> --setup-key <KEY>`
for headless Macs, or leave SSO to the user. Pre-approve the system extensions
(`com.netzilo.NetziloFilter`, `com.netzilo.NetziloSecurity`) with an MDM
SystemExtensions payload so users are not prompted.

**Verify:** `sudo launchctl print system/Netzilo | head`, `netzilo status`.

**Uninstall:** `sudo /Applications/Netzilo.app/Contents/MacOS/netzilo service uninstall`
(this also removes the system extension via `NetziloFilterManager --uninstall`, cleans
`scutil` DNS state, removes force-installed browser extensions and the
`NODE_EXTRA_CA_CERTS` LaunchAgent), then `sudo rm -rf /Applications/Netzilo.app
/etc/netzilo /var/log/netzilo`. The `Netzilo Edge CA` remains in the System keychain;
remove via Keychain Access if desired. Remove the PATH line from `~/.zshrc`.

---

## 4. Linux

**One-liner (any distro with systemd, amd64):**

```bash
curl -fsSL https://pkg.netzilo.com/download/linux/install_netzilo_linux.sh | sh
```

What it does (read from the published script): if service `Netzilo` is active it runs
`netzilo down` and `netzilo service uninstall`; removes `/opt/netzilo` and
`/usr/bin/netzilo`; downloads `https://pkg.netzilo.com/download/linux/netzilo` into
`/opt/netzilo`, copies to `/usr/bin/netzilo`, `chmod +x`; `sudo netzilo service install`;
`systemctl start Netzilo`; `systemctl enable Netzilo`. It needs `sudo` and `wget`. It
prints an example `netzilo up --management-url https://srv.netzilo.com --setup-key …`.
Running it again is the upgrade path (it re-downloads the current binary; `netzilo down`
in the script logs the peer out — see §7).

**Manual (air-gapped or arm64 unavailable):**

```bash
sudo install -m 0755 netzilo /usr/bin/netzilo
sudo netzilo service install && sudo netzilo service start
netzilo up --management-url https://<domain> --setup-key <KEY>
```

Requirements: root for kernel WireGuard and TUN (`/dev/net/tun`), `nft` or `iptables`
present (nftables preferred; `NZ_SKIP_NFTABLES_CHECK=true` forces iptables). Without the
`wireguard` kernel module the client falls back to userspace WireGuard
(`Interface type: Userspace` in status; functional, slower). Non-root runs are forced into
netstack mode.

**Headless SSO:** `netzilo up` on a server without a browser prints a URL and a code
(device-code flow) — paste the URL into any browser. Prefer setup keys for servers.

**Persistent flags for the service:** `sudo netzilo service install --log-level debug`
bakes flags into the unit; or set `NB_*` env vars in the unit's environment
(`systemctl edit Netzilo`).

**Uninstall:** `sudo netzilo down; sudo netzilo service uninstall; sudo rm -f /usr/bin/netzilo; sudo rm -rf /opt/netzilo /etc/netzilo /var/log/netzilo`.
The CA anchor `netzilo-mitm-ca.crt` stays under `/usr/local/share/ca-certificates/` (or
`/etc/pki/ca-trust/source/anchors/`); remove it and run `update-ca-certificates`
(`update-ca-trust extract` on RHEL) for a full clean-up, and remove the
`NODE_EXTRA_CA_CERTS` line from `/etc/environment`.

---

## 5. Mobile

Android (`io.netzilo.app`) and iOS (`6532624291`): install, tap **Connect**, sign in with
email. Self-hosted: change the server in the app's settings before connecting (the app's
"Server" field takes the management URL). Rosenpass/PQC is not available on mobile.

---

## 6. Containers and Kubernetes

There is no official published Netzilo container image. Build one from the Linux binary:

```dockerfile
FROM alpine:3.19
RUN apk add --no-cache ca-certificates iptables ip6tables wget \
 && wget -O /usr/local/bin/netzilo https://pkg.netzilo.com/download/linux/netzilo \
 && chmod +x /usr/local/bin/netzilo
ENV NB_FOREGROUND_MODE=true
ENTRYPOINT ["/usr/local/bin/netzilo","up"]
```

Run:

```bash
docker run -d --name netzilo-peer --hostname <peer-name> \
  --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=SYS_RESOURCE \
  -e NB_SETUP_KEY=<KEY> -e NB_MANAGEMENT_URL=https://<domain> \
  -v netzilo-client:/etc/netzilo <image>
```

- `NB_FOREGROUND_MODE=true` runs the engine in-process (no daemon).
- Add `-e NB_WG_KERNEL_DISABLED=true` if the host lacks the WireGuard module.
- Fully unprivileged: `-e NB_USERSPACE_MODE=true` (or `NB_USE_NETSTACK_MODE=true`) — no TUN,
  reachability only through the SOCKS5 proxy on 41339 / `NB_SOCKS5_LISTENER_PORT`; DNS
  names are not resolvable in netstack mode.
- Persist `/etc/netzilo` so the peer keeps its identity across restarts (otherwise every
  start creates a new peer; use an ephemeral setup key if you want auto-cleanup).

Kubernetes routing peers: reusable **ephemeral** setup key with auto-group (e.g.
`kubernetes-routers`), a Deployment with the env above and
`securityContext.capabilities.add: [NET_ADMIN, SYS_ADMIN, SYS_RESOURCE]`, then a route
whose routing group is `kubernetes-routers` (routing peers must be Linux). `replicas: 3`
gives HA automatically.

---

## 7. Upgrading clients

| Platform | Procedure | Notes |
|---|---|---|
| Windows | run the new installer in any form (`netzilo_setup.exe`, `nz_installer_64.exe -s`, or the MSI) | in-place upgrade, no "already installed" prompt: services and drivers are stopped, old files set aside, config and enrollment kept. If a running driver cannot be replaced, `HKLM\System\CurrentControlSet\Control\NetziloPendingReboot` is set and the next install says "Please reboot computer and try again." — reboot, then run it again (`40-windows-hosts.md` §2) |
| macOS | install the new pkg | postinstall re-installs the service; enrollment kept |
| Linux | re-run the one-liner, or replace `/usr/bin/netzilo` and `sudo netzilo service restart` | **the one-liner runs `netzilo down` which logs the peer out and regenerates keys** — SSO devices must log in again; setup-key devices must re-run `netzilo up --setup-key` (a new peer entry may appear; delete the old one). Replacing the binary manually + `service restart` preserves enrollment |

Version check: `netzilo version`; the tray shows "GUI" and "Service" versions and a
"Download latest version" item. The dashboard flags peers older than the latest release
with "Update available". The client's in-app update URL
(`pkg.netzilo.com/releases/latest/version`) currently returns 404, so in-app update
notifications may not work; direct users to the download links above.

---

## 8. Fleet deployment patterns

### 8.1 Servers / IaC
Reusable setup key with usage limit and auto-groups; `netzilo up --setup-key` in
cloud-init/Ansible; `--hostname <name>` to control the peer name. Use `ephemeral` keys for
autoscaling groups.

### 8.2 End-user laptops (SSO)
Push the installer silently; users click **Connect** in the tray and sign in. Configure
**Peer login expiration** (Settings → Authentication) to force periodic re-auth. Peers
added with setup keys are exempt from login expiration (toggle disabled for them).

### 8.3 Headless devices acting as a user (AI agents, CI)
`netzilo deploy-user` provisions a user + PAT in one step and stores the PAT locally:

```bash
netzilo deploy-user --fullname "Build Agent 01" --email build01@example.com \
  --groups "Agents" --tokenname build01 --tokenexp 180 \
  --servicetoken nzl_<admin-or-service-user-PAT> --apiurl https://<domain>
netzilo up   # uses the stored pat.dat automatically
```

Or store an existing PAT: `netzilo deploy-user --usertoken nzl_… --apiurl https://<domain>`.
Or simply `NETZILOPAT=nzl_… netzilo up`. PAT file: Linux `~/.config/netzilo/pat.dat`,
macOS `~/Library/Application Support/Netzilo/pat.dat`, Windows `%PROGRAMDATA%\Netzilo\pat.dat`
(encrypted). A JSON config file is accepted with `--config-file` and expands `${VAR}`.

### 8.4 Corporate proxies
`netzilo up --proxy http://proxy.corp:3128` (or `socks5://…`, or `--proxy auto` to use
system settings) routes management/signal/TURN traffic through the proxy. Persisted in
config. If gRPC over HTTP/2 is blocked, `NB_FORCE_WS=1` uses WebSocket transport.

### 8.5 Pre-shared key
`netzilo up --preshared-key <psk>` on every peer that should talk together; peers with
different or no PSK cannot communicate. Rarely needed; document it if used.

### 8.6 Routing peers / exit nodes
Linux only. Size ≥ 2 vCPU/4 GB for small sites (docs recommend 4 vCPU/8 GB). Enroll with a
setup key, then Dashboard → Network → Routes → Add Route (range or domains, routing peer
or Linux peer group, distribution groups, masquerade on unless the LAN routes back to
`100.64.0.0/10`). Exit node = route `0.0.0.0/0` via Peers → ⋮ → Add Exit Node; add a DNS
server with no match domains for the same distribution groups so DNS leaves via the exit
node. IPv6 default routes are blocked. Clients pick the route by metric (lower wins); users
can override with `netzilo routes select`.

---

## 9. Post-install verification checklist

```bash
netzilo status -d
```

- `Management: Connected`, `Signal: Connected`, `Relays: N/N Available`
- `Netzilo IP: 100.x.y.z/16` and `FQDN`
- `Interface type: Kernel` (Linux with module) or `Userspace` (macOS always, Windows always)
- Peers show `Status: Connected`; `Connection type: P2P` preferred; `Relayed` means UDP is
  blocked somewhere (works, higher latency)
- Dashboard → Peers shows the device online with the expected groups

If the device is missing from the dashboard, the peer is enrolled against a different
management URL — check `grep ManagementURL /etc/netzilo/config.json`.

---

## 10. What enrollment changes on the device

- Creates the WireGuard interface (`wt0`/`utun100`), adds routes for `100.64.0.0/10` and
  any distributed routes, installs firewall rules (nftables/iptables on Linux, userspace
  filter elsewhere) implementing the account's policies.
- Configures DNS for the peer domain (`systemd-resolved`/NetworkManager/`resolv.conf`
  on Linux; `scutil` state on macOS; NRPT rule `Netzilo-Match` and interface DNS on
  Windows). Restored on `netzilo down` or service stop; an unclean shutdown is repaired
  on next start.
- Generates the `Netzilo Edge CA` (`netzilo-ca.pem` in the config dir) and trusts it in
  the OS store; sets `NODE_EXTRA_CA_CERTS` system-wide so Node-based tools accept
  intercepted TLS. This supports the AI security features (see
  `10-ai-security-aidr.md`). On macOS non-root installs an authorization dialog
  "Netzilo AI Edge needs to install its CA certificate…" appears — cancelling leaves the
  CA untrusted and TLS inspection non-functional until `sudo netzilo service restart`.
- Starts the local loopback services listed in §0. Port conflicts on 41336–41339 must be
  resolved with `--web-server-port`, `--mcp-gateway-port`, `--socks5-port`.

## 11. Platform details that cause first-install tickets

**macOS needs three approvals, not one.** A network extension, a separate endpoint
security extension, and Full Disk Access for the security monitor. Approving only the
first leaves the tunnel working while the inspection and security features silently do
nothing, which is then reported as "the AI features don't work". Under device management,
pre-approving the two extensions does not cover Full Disk Access; that needs its own
privacy preferences profile.

**Windows has three installer forms, and the online one is wrong for managed rollouts.**
`netzilo_setup.exe` downloads the real package from `pkg.netzilo.com` while it runs; from
a deployment tool's system context, which has no user proxy, or on a machine without
internet, it stops with "failed to download installer." and the tool reports a failed or
silent install. Use the offline `nz_installer_64.exe -s` for scripted pushes and the MSI
(`REBOOT=ReallySuppress`, device context) wherever the tool requires a package, including
group-policy software installation and application wrapping. A deployment run in user
context on a non-administrator account yields a non-admin install (userspace networking,
no drivers or workspace), which is reported later as "the AI features are missing".
Install logs for silent failures: `%ProgramData%\Netzilo\netzilo_online_install.log` and
`netzilo_offline_nsis_install.log`; `installer_internal.log` in the same folder is
encrypted and is for Netzilo support only. Details: `40-windows-hosts.md` §2–3.

**Linux has an optional tray application** distributed separately from the command-line
client. On desktop environments that do not show legacy tray icons, notably stock GNOME,
it needs an indicator extension before the icon appears. A missing icon is a desktop
environment issue, not a client fault.

**Enterprise-managed configuration for mobile is not available.** The management server
address cannot be pre-seeded through mobile device management; users set it in the app.
Do not promise a zero-touch mobile rollout.

**On hardened Kubernetes, routing peers need an exemption.** A routing peer needs
elevated network capabilities, which clusters enforcing restricted pod security or a
default security context constraint will refuse outright. The pod is rejected rather than
misbehaving. Arrange the exemption before deploying.

**Security tooling on Linux can block the client silently.** Where mandatory access
control is enforcing, denials appear in the host's audit log rather than in the client's
own log. No policy ships with the product. Check the audit log when a routing peer fails
to apply firewall rules or create its interface with no explanation.

## 12. What Cloud customers must allow outbound

Customers of the hosted service often need to tell their own network team what to permit.
They need outbound access on the standard secure web port to the Netzilo dashboard and
management hostnames, and outbound access for relay traffic on the relay ports so that
devices behind restrictive networks can still connect.

Two practical points. Allow the hostnames rather than addresses wherever the customer's
equipment supports it, because addresses can change. And if the customer's network
performs interception, exempt these hostnames, because the client validates the
certificate itself and interception will break the connection in a way that looks like an
outage.
