---
id: '06'
title: Netzilo Client — CLI and Configuration Reference
requires:
- client-device
executable_on:
- netzilo-harness
- human-operator
chars: 14710
sections:
- id: '1'
  title: Global flags (all commands)
  chars: 1473
- id: '2'
  title: Commands
  chars: 8121
- id: '3'
  title: Environment variables beyond flags
  chars: 1388
- id: '4'
  title: Files and state
  chars: 1780
- id: '5'
  title: Tray application (`netzilo-ui`)
  chars: 869
---
# Netzilo Client — CLI and Configuration Reference

**Audience:** an AI operator who needs the exact command, flag, environment variable,
file path, or status field for the Netzilo client (`netzilo`, version line 4.4.x).
Flags not listed here do not exist in this build (in particular there is **no**
`profile`, `lazy-connection`, `block-lan`, `block-inbound`, or `mtu` flag).

Where these run: on the device being diagnosed or deployed. If the machine you work
from has its own Netzilo client, its output describes that machine's enrolment, not the
customer's (`SKILL.md` → "The Netzilo client on your own machine is a tool, not evidence").

Elevation: on Linux/macOS the daemon socket is world-writable, so most commands work
unprivileged; `service`, `ssh`, and a foreground `up -F` with a TUN device require root.
A foreground run as a normal user uses userspace mode (as with `-U`) and needs a writable
`--config`; it is reachable only through its SOCKS5 proxy (`11-connectivity-diagnosis.md`
§8). On Windows run an elevated terminal for `service`, `ssh`, and `up -F`.

---

## 1. Global flags (all commands)

Every flag maps to an environment variable `NB_<FLAG>` (uppercase, `-` → `_`). The
legacy `WT_` prefix is also read; `NB_` wins.

| Flag | Short | Default | Env | Meaning |
|---|---|---|---|---|
| `--config` | `-c` | `/etc/netzilo/config.json` (Win `%PROGRAMDATA%\Netzilo\config.json`) | `NB_CONFIG` | config file |
| `--daemon-addr` | | `unix:///var/run/netzilo.sock` (Win `tcp://127.0.0.1:40836`) | `NB_DAEMON_ADDR` | how the CLI reaches the daemon |
| `--management-url` | `-m` | `https://srv.netzilo.com:443` | `NB_MANAGEMENT_URL` (also `NETZILOSRV`) | management server |
| `--admin-url` | | derived (`srv.`→`go.`; else same host) | `NB_ADMIN_URL` | dashboard URL used for SSO session flow |
| `--setup-key` | `-k` | | `NB_SETUP_KEY` | setup key for registration |
| `--setup-key-file` | | | `NB_SETUP_KEY_FILE` | file containing the key (exclusive with `--setup-key`) |
| `--preshared-key` | | | `NB_PRESHARED_KEY` | WireGuard PSK; peers must share it to communicate |
| `--hostname` | `-n` | OS hostname | `NB_HOSTNAME` | peer name |
| `--log-level` | `-l` | `info` | `NB_LOG_LEVEL` | `panic fatal error warn info debug trace` |
| `--log-file` | | `/var/log/netzilo/client.log` (Win `%PROGRAMDATA%\Netzilo\client.log`) | `NB_LOG_FILE` | `console` = stdout, `syslog` = syslog |
| `--service` | `-s` | `Netzilo` | `NB_SERVICE` | OS service name |
| `--anonymize` | `-A` | false | `NB_ANONYMIZE` | scrub IPs/domains in output |

---

## 2. Commands

### `netzilo up` — register (if needed), log in, connect

| Flag | Default | Meaning |
|---|---|---|
| `--foreground-mode`, `-F` | false | run the engine in this process (no daemon); Ctrl-C logs out and resets keys |
| `--userspace-mode`, `-U` | false | userspace TCP/IP stack (netstack); no TUN device, reachable only through the local SOCKS5 proxy (`11-connectivity-diagnosis.md` §8) |
| `--interface-name` | `wt0` (macOS `utun100`) | WireGuard interface; macOS must be `utunN` |
| `--wireguard-port` | `51820` | local WireGuard UDP port |
| `--pat` | | personal access token login (`NB_PAT`; also `NETZILOPAT` env or stored `pat.dat`) |
| `--allow-server-ssh` | false | allow this peer to run the embedded SSH server (dashboard must also enable it) |
| `--disable-auto-connect` | false | don't connect when the service starts |
| `--dns-resolver-address` | | custom local resolver `ip:port` (e.g. `127.0.0.1:5053`); `""` clears |
| `--dns-router-interval` | `1m` | re-resolve interval for domain routes |
| `--external-ip-map` | | NAT mapping `12.34.56.78/10.0.0.1`, `IP/ifname`, comma list; `""` clears |
| `--extra-iface-blacklist` | | extra interfaces to ignore (defaults: `wt0 wt utun tun0 zt ZeroTier wg ts Tailscale tailscale docker veth br- lo`) |
| `--network-monitor`, `-N` | true on Windows/macOS, false Linux | restart engine on default-route change |
| `--enable-rosenpass` | false | experimental post-quantum PSK rotation |
| `--rosenpass-permissive` | false | also talk to non-Rosenpass peers |
| `--proxy` | | upstream proxy for management/signal/TURN: `http://…`, `socks5://…`, or `auto` |
| `--unified-proxy` | false | (daemon mode forces on) local SOCKS5+HTTP proxy |
| `--mitm` | false | (daemon mode forces on) TLS inspection on the unified proxy |
| `--socks5-port` | `41339` as root; a per-user port derived from the home directory otherwise | local SOCKS5 proxy port on `127.0.0.1` (`NB_SOCKS5_LISTENER_PORT` overrides); `netzilo status` does not show it |
| `--web-server-port` | `41336` | local control server port (hooks, browser extension) |
| `--mcp-gateway-port` | `41338` | embedded MCP gateway port |
| `--container-name`, `--parent-pid` | | internal (Windows workspace containers) |

Behaviour: if the daemon is already `Connected` prints `Already connected`. If login is
needed and no key/PAT is given, it starts SSO and prints
`Please do the SSO login in your browser.` with a URL (and a code for the device flow).
Flags given to `up` are persisted into `config.json` by the daemon, so they only need
to be passed once.

### `netzilo login` — authenticate without connecting
Same auth options as `up` (`--setup-key`, `--pat`, `--management-url`). With
`--log-file console` it runs without the daemon and writes the config directly.

### `netzilo down` — disconnect **and log out**
Tears down the tunnel, restores DNS/routes/firewall, calls management `Logout`, opens
the logout URL, deletes `token.dat` and **resets the local WireGuard keys** (config
keeps only the URLs). The next `up` re-registers the peer (SSO devices must log in again;
setup-key devices need the key again). Use `sudo netzilo service stop` if you only want
to stop without logging out.

### `netzilo status`

| Flag | Meaning |
|---|---|
| `--detail`, `-d` | per-peer details |
| `--json` / `--yaml` | machine-readable |
| `--ipv4` | print only this peer's Netzilo IPv4 |
| `--filter-by-ips a,b` | only those peers (implies detail) |
| `--filter-by-names peer-a,peer-b.netzilo.network` | prefix match on FQDN |
| `--filter-by-status connected\|disconnected` | |
| `-A` | anonymize |

Summary fields: `OS`, `Daemon version`, `CLI version`, `Management: Connected|Disconnected, reason: …`,
`Signal: …`, `Relays: n/m Available`, `Nameservers: n/m Available`, `FQDN`,
`Netzilo IP`, `Interface type: Kernel|Userspace|N/A`, `Quantum resistance`, `Routes`,
`Peers count: n/m Connected`. Detail per peer: `Status`, `Connection type: P2P|Relayed`,
`Direct`, `ICE candidate (Local/Remote)` (`host`, `srflx`, `relay`, `prflx`),
`ICE candidate endpoints`, `Last connection update`, `Last WireGuard handshake`,
`Transfer status (received/sent)`, `Quantum resistance`, `Routes`, `Latency`.

If the daemon is not logged in the output is `Daemon status: NeedsLogin` (or
`LoginFailed`) with instructions to run `netzilo up` or `netzilo up --management-url … --setup-key …`.

JSON keys: `management{url,connected,error}`, `signal{…}`, `relays{total,available,details[]}`,
`dnsServers[]`, `netziloIp`, `publicKey`, `fqdn`, `usesKernelInterface`, `routes`,
`peers{total,connected,details[{fqdn,netziloIp,publicKey,status,connectionType,direct,
iceCandidateType,iceCandidateEndpoint,lastWireguardHandshake,transferReceived,transferSent,latency,routes}]}`.

### `netzilo refresh` — force a network-map sync (bypasses the 30 s interval)
Error `failed to refresh: client is not connected` when the engine is down.

### `netzilo routes` — client-side route selection
- `netzilo routes list` (`ls`) → `ID`, `Network` or `Domains` + `Resolved IPs`, `Status: Selected|Not Selected`
- `netzilo routes select <id…>|all [-a|--append]` — selecting deselects the others unless `-a`
- `netzilo routes deselect <id…>|all`
Tray equivalent: **Network Routes** menu.

### `netzilo ssh [user@]host [-p 44338]` — SSH to a peer over the tunnel
Requires root/Administrator. Default user `root`. Target must have SSH enabled both
locally (`--allow-server-ssh`) and in the dashboard (peer → SSH Access). Auth is by the
peers' Netzilo keys; the target OS user must exist. Server listens on the peer's Netzilo
IP, TCP 44338. Interactive shell only (no scp/port-forward).

### `netzilo service install|uninstall|start|stop|restart|run`
`install` registers the OS service (Linux systemd `Netzilo.service`, macOS launchd
`Netzilo`, Windows SCM `Netzilo`), adds the Windows firewall rule `Netzilo Client`, and
generates/trusts the `Netzilo Edge CA`. Any global flag passed to `install` is baked into
the service arguments (e.g. `--log-level debug`, `--config`, `--management-url`,
`--log-file`). `stop` first runs a graceful `Down`. `uninstall` also removes the macOS
system extension, stale DNS state, force-installed browser extensions, and the
`NODE_EXTRA_CA_CERTS` environment entry (the CA itself stays trusted).

### `netzilo debug`
- `netzilo debug bundle [-A]` → zip path (e.g. `/tmp/netzilo-debug-*/netzilo.debug.*.zip`,
  Windows `%PROGRAMDATA%\Netzilo\netzilo.debug.*.zip`). Contains **every file in the log
  directory** plus `status.txt`. On Windows the log directory is also the config
  directory, so the bundle includes `config.json`, `token.dat`, and CA files — review
  before sharing. `-A` anonymizes. Fails with
  `log file is set to console, cannot create debug bundle` if the service logs to console.
- `netzilo debug log level <panic|fatal|error|warn|info|debug|trace>` — runtime only;
  reverts at daemon restart.
- `netzilo debug for <duration>` (e.g. `5m`) — down → trace → up → wait → down → bundle,
  then restores the previous state and log level.
Tray: **Support → Collect Data** / **Open Logs Folder**.

### `netzilo hook` — coding-agent hooks (Claude Code, Codex, Gemini CLI, OpenClaw)
`netzilo hook install|uninstall|verify --framework=claude-code|codex|gemini|openclaw [--url http://localhost:41336/evaluate]`.
Details in `10-ai-security-aidr.md` §4.

### `netzilo deploy-user` — provision a user + PAT and store it locally
Flags: `--fullname`, `--email`, `--groups a,b`, `--password`, `--tokenname`,
`--tokenexp` (1–365 days), `--servicetoken` (admin/service PAT, required for creation),
`--usertoken` (store an existing PAT instead), `--apiurl` (default = management URL),
`--accountid`, `--use-current-user`, `--config-file <json>` (`${VAR}` expansion),
`--debug`. Stores the PAT encrypted in `pat.dat`; `netzilo up` then logs in with it.

### `netzilo version` — prints the version, e.g. `4.4.375`.

### Hidden / platform-specific
`netzilo record` (Windows session recording; started from the tray), `netzilo webproxy`
(internal). Anything else printed by `--help` that is not listed here is internal.

---

## 3. Environment variables beyond flags

| Variable | Effect |
|---|---|
| `NETZILOSRV` | management URL override (CLI and tray) |
| `NETZILOPAT` | PAT used for login when no setup key is given |
| `NB_FORCE_WS=1` | gRPC over WebSocket to management/signal (when HTTP/2 is blocked by a proxy) |
| `NB_WG_KERNEL_DISABLED=true` | force userspace WireGuard on Linux |
| `NB_USE_NETSTACK_MODE=true` | netstack mode (no TUN); `NB_SOCKS5_LISTENER_PORT` sets the SOCKS5 port |
| `NB_USE_LEGACY_ROUTING=true` | Linux legacy routing (suggested when `rp_filter` sysctl fails on exit-node setups) |
| `NB_DISABLE_ROUTE_CACHE=true` | Windows route cache off |
| `NB_ENABLE_LOCAL_FORWARDING=true` | userspace-filter local forwarding |
| `NZ_SKIP_NFTABLES_CHECK=true` | use iptables instead of nftables |
| `NB_LOG_FORMAT=json` | JSON logs |
| `NB_WG_DEBUG=true` | WireGuard-go debug logging |
| `NB_CONN_RETRY_INTERVAL_TIME` (2m), `NB_CONN_MAX_RETRY_INTERVAL_TIME` (10m), `NB_CONN_MAX_RETRY_TIME_TIME` (14d), `NB_CONN_RETRY_MULTIPLIER` (1.7) | reconnect backoff |
| `PIONS_LOG_DEBUG=all` / `PIONS_LOG_TRACE=all` | ICE library logging |
| `GRPC_GO_LOG_VERBOSITY_LEVEL=99 GRPC_GO_LOG_SEVERITY_LEVEL=info` | gRPC logging |
| `NETZILO_HOOK_URL`, `NETZILO_HOOK_TIMEOUT_MS`, `NETZILO_HOOK_POLICY`, `NETZILO_HOOK_SKIP`, `NETZILO_HOOK_STATE_DIR` | agent hook behaviour (see `10-ai-security-aidr.md`) |

---

## 4. Files and state

| Item | Linux | macOS | Windows |
|---|---|---|---|
| Config | `/etc/netzilo/config.json` | same | `%PROGRAMDATA%\Netzilo\config.json` |
| Log | `/var/log/netzilo/client.log` | same | `%PROGRAMDATA%\Netzilo\client.log`; panics in `service.log` |
| SSO tokens | `/etc/netzilo/token.dat` (deleted on `down`) | same | `%PROGRAMDATA%\Netzilo\token.dat` |
| PAT store | `~/.config/netzilo/pat.dat` (or `$XDG_CONFIG_HOME`) | `~/Library/Application Support/Netzilo/pat.dat` | `%PROGRAMDATA%\Netzilo\pat.dat` |
| TLS-inspection CA | `/etc/netzilo/netzilo-ca.pem`, `netzilo-ca-key.pem` | same | `%PROGRAMDATA%\Netzilo\netzilo-ca.pem` |
| Skip-domain config | — | — | `%PROGRAMDATA%\Netzilo\container.json` (fetched from `pkg.netzilo.com/download/configs/container.json`) |
| Daemon socket | `/var/run/netzilo.sock` | same | `tcp://127.0.0.1:40836` |
| Binary | `/usr/bin/netzilo` (installer) | `/Applications/Netzilo.app/Contents/MacOS/netzilo` | `C:\Program Files\Netzilo\Netzilo.exe` |
| Service | `Netzilo.service` | launchd `Netzilo` | SCM `Netzilo` |

`config.json` keys: `PrivateKey`, `PreSharedKey`, `ManagementURL`, `AdminURL`,
`WgIface`, `WgPort`, `UseNetstack`, `Sock5Port`, `WebServPort`, `MCPGatewayPort`,
`NetworkMonitor`, `IFaceBlackList`, `DisableIPv6Discovery`, `RosenpassEnabled`,
`RosenpassPermissive`, `ServerSSHAllowed`, `SSHKey`, `AuthFlowType` (`session|pkce|device`),
`NATExternalIPs`, `CustomDNSAddress`, `DisableAutoConnect`, `DNSRouteInterval`,
`ClientCertPath`/`ClientCertKeyPath` (mTLS to management), `UnifiedProxyEnabled`,
`MITMEnabled`, `ICEProxyURL`. Editing the file requires `sudo netzilo service restart`;
prefer passing flags to `netzilo up`, which persists them.

Log rotation is built in (5 MB, 10 files, 30 days, gzip).

---

## 5. Tray application (`netzilo-ui`)

Menu: status line, **Connect**, **Disconnect**, **Refresh**, **Record Session**
(Windows), **Admin Panel**, **Workspaces → Terminate All / Reset Contents** (Windows),
**Network Routes**, **Advanced → Allow SSH / Connect on Startup / Enable Quantum-Resistance / Server Settings**,
**Support → Collect Data / Open Logs Folder**, **Version → GUI / Service / Download latest version**,
**Quit**. Settings window fields: Quantum-Resistance (permissive), Interface Name,
Interface Port, Management URL, Admin URL, Pre-shared Key, Config File, Log File.
Errors: `Invalid Pre-shared Key Value`, `Invalid interface port`.

Session expiry: the UI shows "Netzilo Session Expired — You need to re-authenticate…";
on headless Unix hosts `wall` broadcasts "Netzilo connection session expired". Status
then shows `NeedsLogin`; run `netzilo up`.
