# Netzilo Client — Troubleshooting Runbook

**Audience:** an AI operator diagnosing a user's or server's Netzilo client. Work from
the symptom; each entry gives the evidence to collect, the cause, and the fix. Error
strings are quoted exactly as the client prints them. Never ask the customer to reinstall as a
first step — most problems are configuration, network, or identity.

Always start with the same three commands (run on the affected device):

```bash
netzilo version
netzilo status -d
tail -n 200 /var/log/netzilo/client.log        # Windows: %PROGRAMDATA%\Netzilo\client.log
```

If you are handed a log rather than a symptom, start with `13-log-interpretation.md`
(profile the templates, find the last healthy sequence, rule out the noise families) and
come back here for the fix. For anything non-trivial collect a bundle: `sudo netzilo debug bundle -A` (anonymized), or
for intermittent issues `sudo netzilo debug for 5m -A`. The bundle zips the whole log
folder plus `status.txt` — on Windows that folder also holds `config.json` and
`token.dat`, so keep the bundle private.

---

## 1. CLI cannot talk to the daemon

**Symptom:** any command prints
`failed to connect to daemon error: … If the daemon is not running please run: netzilo service install / netzilo service start`.

| Check | Command |
|---|---|
| Service state | Linux `systemctl status Netzilo`; macOS `sudo launchctl print system/Netzilo`; Windows `sc query Netzilo` |
| Socket | Linux/macOS `ls -l /var/run/netzilo.sock`; Windows `netstat -ano \| findstr 40836` |
| Custom address | is `--daemon-addr`/`NB_DAEMON_ADDR` set to something else? |

Fixes: `sudo netzilo service start`; if the service is missing `sudo netzilo service install && sudo netzilo service start`.
`failed to listen daemon interface` in the log = stale socket or busy port → remove
`/var/run/netzilo.sock` (or free 40836) and restart. On macOS, if `netzilo` is "not found",
use the full path `/Applications/Netzilo.app/Contents/MacOS/netzilo` or open a new shell.

---

## 2. Not logged in / cannot log in

`netzilo status` → `Daemon status: NeedsLogin` or `LoginFailed`.

| Message | Cause | Fix |
|---|---|---|
| `NeedsLogin` after it worked before | session expired (peer login expiration, account default 24 h for SSO peers), or someone ran `netzilo down` (which logs out) | `netzilo up`; for servers use a setup key so expiration does not apply |
| `LoginFailed` | management unreachable, TLS failure, wrong URL | `grep ManagementURL /etc/netzilo/config.json`; `curl -sS -o /dev/null -w "%{http_code}\n" https://<mgmt-host>/api/users` should return `401`; check proxy/firewall |
| `login failed: … peer is not registered` | management no longer knows this peer's key (peer deleted in dashboard, or config was reset) | re-enrol: `netzilo up --setup-key <KEY>` or SSO |
| `invalid setup-key format` | key mistyped | copy the key exactly (UUID-like) |
| `couldn't add peer: setup key is invalid` (server side) | key revoked/expired/over its usage limit, or belongs to another server | create a new key in Setup Keys |
| `invalid PAT token` / `PAT token expired` / `PAT token has expired on …` | bad or expired PAT | new PAT; delete `pat.dat`; unset `NETZILOPAT` |
| `no SSO provider returned from management. Please proceed with setting up this device using setup keys` | self-hosted server has no IdP configured for device login | use `--setup-key` or fix server `management.json` auth flows |
| `no available port found from configured redirect URLs` | localhost 53000/54000 busy during PKCE | free the port or run on a host with a browser; the CLI falls back to device-code flow when no desktop is detected |
| `authentication timeout after N seconds` / `waiting for browser login failed` | user did not finish the browser login | run `netzilo up` again and complete login promptly |
| `sso user code is invalid` / `oauth flow is not initialized` | stale flow | rerun `netzilo up` |
| `user is blocked` | account admin blocked the user | unblock in Team → Users |
| `maximum number of personal peers reached` | Free-plan peer limit (100) | remove peers or upgrade |
| `user does not belong to any of the allowed JWT groups` | Settings → Groups → "JWT allow group" excludes this user | fix IdP group membership or the setting |
| Browser shows Zitadel error after SSO redirect | see `04-identity-and-sso.md` §8 | |
| Peer shows **Approval required** in dashboard | peer approval is on (Cloud) | admin clicks **Approve** on the peer |

Headless servers: `netzilo up` prints a URL and a code (device flow); complete it in any
browser, or prefer a setup key.

---

## 3. Connected to management but peers unreachable

For a full source-to-destination investigation (including hosts behind routing peers and
exit nodes) follow `11-connectivity-diagnosis.md`; the table below covers the quick
single-peer reads. Read `netzilo status -d` for the affected peer.

| Observation | Meaning | Fix |
|---|---|---|
| Peer `Status: Disconnected`, `Last WireGuard handshake: -` | no path found (ICE failed) | check both sides have `Relays: n/n Available`; open outbound UDP; if relays are 0 see §4 |
| `Connection type: Relayed` | direct UDP blocked (symmetric NAT, corporate firewall) — works but slower | allow outbound UDP (any port) from the client; on servers behind 1:1 NAT set `netzilo up --external-ip-map <public-ip>` |
| `Connected` but no traffic, handshake older than ~3 min | tunnel stale / packets dropped | PSK mismatch (`--preshared-key` on one side only)? MTU is fixed at 1280 so MTU is rarely the cause; run `netzilo debug for 3m` |
| Peer not listed at all | policy does not connect these two groups | Dashboard → Network → Policies: both peers must be in groups covered by an enabled policy; remember only `accept` rules exist and TCP/UDP one-way rules need ports |
| Peer listed, `ping` works, service port refused | policy allows the protocol but not the port, or the target's OS firewall | check policy ports; check local firewall on the target |
| Everything worked, then all peers dropped after a network change | network monitor restarted the engine (`Network monitor: default route changed`) | wait 10–20 s; if still stuck use `sudo netzilo service restart` (do not use `netzilo down`, which logs the peer out) |
| Access denied events `peer.access.blocked` in Activity | a posture check failed | event meta names the check and reason; fix device posture or the check |

Reference: two peers talk only if an **enabled policy** covers a group of each, and every
**posture check** attached to that policy passes for the source peer. The Default policy
(All → All) allows everything; once deleted, traffic is deny-by-default.

---

## 4. Relays / signal / management connectivity

On a self-hosted server, the server-side half of this — verifying signal, testing
STUN/TURN with the tools in the coturn image, credential consistency, cloud NAT — is
`03-server-troubleshooting.md` §4a. Read the client symptoms below, then go there.

| Status line | Fix |
|---|---|
| `Management: Disconnected, reason: …` | outbound TCP 443 to the management host; corporate proxy → `netzilo up --proxy http://proxy:3128` or `--proxy auto`; if HTTP/2 is stripped by a middlebox → `NB_FORCE_WS=1` in the service environment |
| `Signal: Disconnected` | same as above; signal is on the same host/443 for self-hosted |
| `Relays: 0/2 Available` | outbound UDP/TCP 3478 and 5349 to the relay host (self-hosted: the server domain); the relay URIs appear in `--detail`. TURN over TLS on 5349 may fail on Let's Encrypt servers (`02-server-operations.md` §8.4) — UDP 3478 must work |
| `Nameservers: 0/1 Available` | the DNS server distributed to this peer is unreachable through the tunnel — check the routing peer/policy to the resolver (UDP 53) |

Log lines: `failed connecting to the Management service`, `connection to management is not ready`,
`disconnected from the Management service but will retry silently` (transient; retries
with backoff up to 14 days), `error while connecting to the Signal Exchange Service`.

---

## 5. Interface / driver problems

| Log message | Platform | Fix |
|---|---|---|
| `failed creating tunnel interface` / `failed to create interface` / `interface wt0 don't have an ipv4 address` | Linux | `modprobe tun`; in containers add `--cap-add=NET_ADMIN` and `/dev/net/tun`; another interface named `wt0`? use `--interface-name` |
| `couldn't access device /dev/net/tun … add flag --cap-add=NET_ADMIN` | container | add the capability / device |
| `Interface type: Userspace` on Linux | no `wireguard` kernel module (or `NB_WG_KERNEL_DISABLED`) | functional; install `wireguard` module for performance |
| `invalid interface name … Please use the prefix utun followed by a number on MacOS` | macOS | `--interface-name utun100` |
| wintun errors / no adapter | Windows | `wintun.dll` must sit next to `Netzilo.exe`; reinstall; AV quarantine? |
| `no firewall manager found, trying to use userspace packet filtering firewall` | Linux without nft/iptables | install `nftables` (or `iptables`) — policies still enforced by the userspace filter |
| `Default route is configured but sysctl operations failed … NB_USE_LEGACY_ROUTING=true or setting net.ipv4.conf.*.rp_filter to 2` | Linux exit-node client on hardened kernel | set the env var in the service or the sysctl |

Non-admin/non-root runs are silently forced into **netstack** mode: no TUN device, only
the SOCKS5 proxy (`127.0.0.1:41339`) can reach peers, and DNS names do not resolve. If
the symptom is "connected but nothing routes", check whether the daemon runs as root/SYSTEM.

---

## 6. DNS

| Symptom / log | Fix |
|---|---|
| `peer.netzilo.network` does not resolve | `netzilo status` → `Nameservers` line; Linux check backend: `resolvectl status` (systemd-resolved) or `/etc/resolv.conf` (should list `100.x` Netzilo resolver); macOS `scutil --dns \| grep -A3 Netzilo`; Windows `Get-DnsClientNrptRule` shows `Netzilo-Match` |
| `the DNS manager of this peer doesn't support custom port. Disabling primary DNS setup.` | port 53 occupied on a host whose resolver cannot use a custom port | free port 53 (e.g. stop dnsmasq) or use `--dns-resolver-address 127.0.0.1:5053` with a system resolver that supports ports |
| Match-domain nameservers not applied | only macOS, Windows 10+, and Linux with systemd-resolved support match domains | provide one primary (no match domains) nameserver group for `All` |
| `broken params in resolv.conf, repairing it...` | another tool rewrote resolv.conf | expected self-heal; consider NetworkManager/systemd-resolved |
| `restoring unclean shutdown` | previous crash left DNS altered | automatic; verify resolution afterwards |
| Windows: DNS broken after uninstall | leftover NRPT rule `Netzilo-Match` | reinstall the client and run `netzilo service uninstall` (which removes the rule), or remove the rule with `Get-DnsClientNrptRule` / `Remove-DnsClientNrptRule` |
| macOS: stale DNS after crash | `sudo netzilo service uninstall` cleans `State:/Network/Service/Netzilo-*` keys; then reinstall |
| Peer name conflict | names are made unique with a numeric suffix (`peer-1`) | rename in dashboard |

Netstack mode never provides DNS (IP only).

---

## 7. Routes and exit nodes

| Symptom | Fix |
|---|---|
| Client does not see the route | `netzilo routes list`; the peer must be in a **distribution group** of the route; the route must be enabled; run `netzilo refresh` |
| Route present but traffic fails | policy from the client's group to the **routing peer's** group must allow the traffic; masquerade must be on unless the LAN routes back to `100.64.0.0/10`; the routing peer must be Linux with IP forwarding (the client enables it) |
| Overlapping routes (same CIDR via two networks) | `netzilo routes select <id>` to pin one; `select all` restores default |
| Exit node: no Internet | IPv6 is blocked by design (no `::/0`); add a DNS server without match domains to the same distribution group; check the exit node's own egress |
| Exit node on Linux client fails with sysctl error | see §5 `NB_USE_LEGACY_ROUTING` |
| Domain route not updating | `--dns-router-interval` (default 1m); "Keep Routes" retains old IPs by design |

---

## 8. SSH

| Message | Fix |
|---|---|
| `error: you must have Administrator privileges to run this command` | run with `sudo` / elevated |
| `Couldn't connect. Please check the connection status or if the ssh server is enabled on the other peer` | target needs `netzilo up --allow-server-ssh` **and** dashboard peer → SSH Access enabled; target must be `Connected` in status |
| target log `running SSH server is not permitted` | local flag off on the target |
| login fails for user | the OS user must exist on the target; default user is `root` |

---

## 9. TLS inspection / AI security side effects

The daemon always runs a TLS-inspecting proxy on `127.0.0.1:41339` and trusts its own CA
(`Netzilo Edge CA`). Traffic is only steered into it for processes named in an Edge
Filter's **Agents** list (macOS/Windows); on Linux only processes explicitly configured
to use the proxy are affected.

| Symptom | Fix |
|---|---|
| App shows certificate error for an AI/SaaS site while Netzilo runs | app does not use the OS trust store (Python, curl, Java) → `export SSL_CERT_FILE=/etc/netzilo/netzilo-ca.pem REQUESTS_CA_BUNDLE=/etc/netzilo/netzilo-ca.pem`; Java: import into `cacerts`; Firefox: enterprise-roots policy or `certutil -A -d sql:<profile>`; app uses certificate pinning → ask Netzilo to add the domain to skip-domains, or remove the app from the filter's Agents |
| `MITM: CA trust install failed (manual trust may be required)` / `no supported CA trust tool found` | install manually: macOS `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain /etc/netzilo/netzilo-ca.pem`; Debian `sudo cp /etc/netzilo/netzilo-ca.pem /usr/local/share/ca-certificates/netzilo-mitm-ca.crt && sudo update-ca-certificates`; RHEL `… /etc/pki/ca-trust/source/anchors/ && sudo update-ca-trust extract`; Windows `certutil -addstore -f Root "%PROGRAMDATA%\Netzilo\netzilo-ca.pem"` |
| `MITM: user cancelled the authorization dialog — CA not installed` (macOS) | `sudo netzilo service restart` and accept, or the manual command above |
| `WSS server: could not load CA cert (WSS on port 41337 disabled)` | delete `netzilo-ca.pem`/`netzilo-ca-key.pem` in the config dir and restart the service (regenerates) |
| `MacFilter: NetziloFilterManager not found alongside daemon binary; extension must be installed manually` | the binary is not running from `/Applications/Netzilo.app`; reinstall the pkg |
| `MacFilter: manager exited with error` | approve the system extension: System Settings → General → Login Items & Extensions → Network Extensions |
| `NWFilter: init failed` / `nwfilter.exe not found` (Windows) | reinstall; check AV quarantine of `nwfilter.exe` |
| `unified proxy stopped with error` / `MCP gateway failed to start` | port 41339 / 41338 in use → `netzilo up --socks5-port <p>` / `--mcp-gateway-port <p>` |
| Node-based tools fail TLS after uninstall | leftover `NODE_EXTRA_CA_CERTS` pointing to a deleted file → remove from `/etc/environment`, `/etc/zshenv`, `/etc/profile`, or HKLM Environment |

More in `10-ai-security-aidr.md` §9.

---

## 10. Upgrade / install problems

| Symptom | Fix |
|---|---|
| Linux one-liner: `netzilo: command not found` afterwards | script needs `sudo` and `wget`; check `/usr/bin/netzilo` exists |
| After Linux one-liner the peer appears twice / asks to log in | the script runs `netzilo down` (logout + key reset); delete the stale peer in the dashboard, re-enrol. Next time upgrade by replacing the binary and `service restart` |
| Windows installer: "Netzilo is already installed. We must remove it…" | expected; proceed (config is kept) |
| macOS: CLI not on PATH | new terminal or full path; PATH line is appended to `~/.zshrc` of the installing user only |
| Dashboard says "Update available" but tray shows no update | in-app version feed is currently unavailable (404); download from the links in `05-client-install-and-deploy.md` |
| Version mismatch between "GUI" and "Service" in tray | UI and daemon from different installs; reinstall |

---

## 11. Verbose diagnostics

```bash
# temporary
netzilo debug log level trace
# persistent (Linux systemd)
sudo systemctl edit Netzilo        # add: [Service] Environment=NB_LOG_LEVEL=debug
sudo systemctl restart Netzilo
# persistent (any OS)
sudo netzilo service stop && sudo netzilo service uninstall && sudo netzilo service install --log-level debug && sudo netzilo service start
# foreground with ICE + gRPC verbosity (Linux/macOS)
sudo netzilo service stop
sudo PIONS_LOG_DEBUG=all GRPC_GO_LOG_VERBOSITY_LEVEL=99 GRPC_GO_LOG_SEVERITY_LEVEL=info NB_LOG_LEVEL=debug netzilo up -F --log-file console
# Windows foreground must run as SYSTEM (wintun):
#   netzilo service stop
#   PsExec64.exe -s cmd.exe /c "\"C:\Program Files\Netzilo\Netzilo.exe\" up -F --log-level debug > C:\Windows\Temp\netzilo.out.log 2>&1"
# userspace WireGuard test (kernel firewall suspicion)
sudo NB_WG_KERNEL_DISABLED=true netzilo up -F --log-file console
```

Remember to `sudo netzilo service start` afterwards (foreground Ctrl-C logs the peer out).

---

## 12. What to report

- Device: OS/arch, `netzilo version`, install method
- `netzilo status -dA`
- Relevant log excerpt (or the `debug bundle -A` path)
- Dashboard facts: peer groups, policies covering them, posture checks attached, the
  Activity events for the peer (`peer.access.blocked`, `peer.login.expire`, …)
- What changed (upgrade, network, policy edit) and when

If the runbook is exhausted and the problem persists, build a support package with
`12-escalation-package.md` rather than sending loose files — the client debug bundle
needs inspection and redaction before it leaves the device.
