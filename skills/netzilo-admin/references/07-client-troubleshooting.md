---
id: '07'
title: Netzilo Client — Troubleshooting Runbook
requires:
- client-device
executable_on:
- netzilo-harness
- human-operator
chars: 27738
sections:
- id: '1'
  title: CLI cannot talk to the daemon
  chars: 1085
- id: '2'
  title: Not logged in / cannot log in
  chars: 3877
- id: '3'
  title: Connected to management but peers unreachable
  chars: 2778
- id: '4'
  title: Relays / signal / management connectivity
  chars: 1544
- id: '5'
  title: Interface / driver problems
  chars: 2414
- id: '6'
  title: DNS
  chars: 2976
- id: '7'
  title: Routes and exit nodes
  chars: 1463
- id: '8'
  title: SSH
  chars: 556
- id: '9'
  title: TLS inspection / AI security side effects
  chars: 3769
- id: '10'
  title: Upgrade / install problems
  chars: 1488
- id: '11'
  title: Verbose diagnostics
  chars: 1177
- id: '12'
  title: What to report
  chars: 604
- id: '13'
  title: Environment problems that look like product faults
  chars: 1677
---
# Netzilo Client — Troubleshooting Runbook

> **From the agent, not by hand.** Most "run on the device" steps below have an
> equivalent the dashboard assistant and the harness can execute directly through the
> device tools: `netzilo status -d` → `diag.status` `{"full": true}`, log inspection →
> `diag.logs` / `diag.grep`, DNS → `diag.dns`, reachability → `diag.probe`, routes →
> `diag.routes` / `diag.route_match`, `netzilo refresh` → `mod.refresh`,
> `netzilo debug log level` → `mod.loglevel`, `netzilo debug bundle` → `diag.bundle`,
> `netzilo down` → `mod.disconnect` (logs the device out; proposed for approval on someone
> else's device). **`netzilo up` has no device-tool equivalent**: once a device is down or
> signed out it answers no tools, and someone at the device must bring it back. Procedure,
> consent rule and limits: `references/36-device-tools.md`; tool contracts:
> `references/37-device-tool-reference.md`. A client too old for the tools still follows
> this file by hand.

**Audience:** an AI operator diagnosing a user's or server's Netzilo client. Work from
the symptom; each entry gives the evidence to collect, the cause, and the fix. Error
strings are quoted exactly as the client prints them. Never ask the customer to reinstall as a
first step — most problems are configuration, network, or identity.

Always start with the same three commands, run on the **affected device**, not on the
machine you are working from. A client on your own machine reports your own enrolment.

```bash
netzilo version
netzilo status -d
tail -n 200 /var/log/netzilo/client.log        # Windows: %ProgramData%\Netzilo\client.log
```

If you are handed a log rather than a symptom, start with `13-log-interpretation.md`
(profile the templates, find the last healthy sequence, rule out the noise families) and
come back here for the fix. For anything non-trivial collect a bundle: `sudo netzilo debug bundle -A` (anonymized). For
intermittent issues raise the level (`netzilo debug log level debug`, or `mod.loglevel`),
wait for the problem to recur, then bundle; do not use `netzilo debug for`, which runs
`netzilo down` internally and so logs the device out. The bundle zips the whole log
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
A Windows non-administrator install runs a per-user client instead of the service, on a
per-user port rather than 40836 (`references/40-windows-hosts.md`).
`failed to listen daemon interface` in the log = stale socket or busy port → remove
`/var/run/netzilo.sock` (or free 40836) and restart. On macOS, if `netzilo` is "not found",
use the full path `/Applications/Netzilo.app/Contents/MacOS/netzilo` or open a new shell.

---

## 2. Not logged in / cannot log in

`netzilo status` → `Daemon status: NeedsLogin` or `LoginFailed` (the same strings are the
`status` field of `diag.status`, although a device in either state rarely answers tools).

How the CLI reports a failed `netzilo up` / `netzilo login`: errors management marks as
final (invalid argument, permission denied, not found, unimplemented) print
**immediately** as `login failed: <reason>`; every other error is retried for about 30 s
and then printed as `login backoff cycle failed: <reason>`. The prefix therefore tells
you whether retrying could help. For any `rpc error: … desc = <reason>` not in the table
below, `13-log-interpretation.md` §4.8 lists every reason management returns, the
server-side event it pairs with, and which side owns the fix.

| Message | Cause | Fix |
|---|---|---|
| `NeedsLogin` after it worked before | session expired (peer login expiration, account default 24 h for SSO peers), or the client was logged out: `netzilo down`, `mod.disconnect`, `netzilo service stop`/`restart`, or a binary replacement followed by a restart all log the device out | `netzilo up` at the device; for servers use a setup key so expiration does not apply |
| `LoginFailed` | the last login attempt failed for a reason other than a rejected session: management unreachable, TLS failure, wrong URL, **an invalid setup key, or an invalid sign-in token** | read the reason on the `failed login:` line of the client log; for reachability `curl -sS -o /dev/null -w "%{http_code}\n" https://<mgmt-host>/api/users` should return `401`; check proxy/firewall; for keys see the rows below |
| `login failed: … failed adding new peer: account not found` | the setup key is unknown to this server: mistyped, deleted, or created on another server or account | check `diag.config` `managementUrl`; create or copy a key from this server's Setup Keys |
| `login backoff cycle failed: … couldn't add peer: setup key is invalid` | the key exists but is expired, revoked, or over its usage limit (printed after about 30 s of retries) | create a new key in Setup Keys, or raise the limit (`references/24-peers-and-setup-keys.md`) |
| `peer is not registered` in the client log during a live session | management no longer knows this peer's key because the peer was deleted in the dashboard | re-enrol: `netzilo up --setup-key <KEY>` or SSO |
| `invalid setup-key format` | key mistyped | copy the key exactly (UUID-like) |
| `invalid PAT token` / `PAT token expired` / `PAT token has expired on …` | bad or expired PAT | new PAT; delete `pat.dat`; unset `NETZILOPAT` |
| `no SSO provider returned from management. Please proceed with setting up this device using setup keys` | self-hosted server has no IdP configured for device login | use `--setup-key` or fix server `management.json` auth flows |
| `no available port found from configured redirect URLs` | localhost 53000/54000 busy during PKCE | free the port or run on a host with a browser; the CLI falls back to device-code flow when no desktop is detected |
| `authentication timeout after N seconds` / `waiting for browser login failed` | user did not finish the browser login | run `netzilo up` again and complete login promptly |
| `sso user code is invalid` / `oauth flow is not initialized` | stale flow | rerun `netzilo up` |
| `user is blocked` | account admin blocked the user | unblock in Team → Users |
| `maximum number of personal peers reached` | Free-plan peer limit (100) | remove peers or upgrade |
| `user does not belong to any of the allowed JWT groups` | Settings → Groups → "JWT allow group" excludes this user | fix IdP group membership or the setting |
| Browser shows Zitadel error after SSO redirect | see `04-identity-and-sso.md` §5 | |

Headless servers: `netzilo up` prints a URL and a code (device flow); complete it in any
browser, or prefer a setup key.

---

## 3. Connected to management but peers unreachable

For a full source-to-destination investigation (including hosts behind routing peers and
exit nodes) follow `11-connectivity-diagnosis.md`; the table below covers the quick
single-peer reads. Read `netzilo status -d` for the affected peer.

| Observation | Meaning | Fix |
|---|---|---|
| Peer `Status: Disconnected`, `Last WireGuard handshake: -` | no path found (ICE failed), or the remote never answered the offer (offline, login expired, not in its map) | check both sides have `Relays: n/n Available`; open outbound UDP; if relays are 0 see §4. To tell the two causes apart from the log lines for that peer's key, use `38-device-diagnosis-method.md` §4.9 |
| `Connection type: Relayed` | direct UDP blocked (symmetric NAT, corporate firewall) — works but slower | allow outbound UDP (any port) from the client; on servers behind 1:1 NAT set `netzilo up --external-ip-map <public-ip>` |
| `Connected` but no traffic, handshake older than ~3 min | tunnel stale / packets dropped | PSK mismatch (`--preshared-key` on one side only)? MTU is fixed at 1280 so MTU is rarely the cause; raise the log level to `debug` and read the ICE and handshake lines (§11) |
| Peer not listed at all | policy does not connect these two groups | Dashboard → Network → Policies: both peers must be in groups covered by an enabled policy; remember only `accept` rules exist and TCP/UDP one-way rules need ports |
| Peer listed, `ping` works, service port refused | policy allows the protocol but not the port, or the target's OS firewall | check policy ports; check local firewall on the target |
| Everything worked, then all peers dropped after a network change | network monitor restarted the engine (`Network monitor: default route changed`); the monitor is on by default on Windows and macOS only; on Linux it runs only when `--network-monitor` was set, so each peer recovers only when ICE fails and reconnects, which can take tens of seconds | wait 10–20 s and read `diag.status` `{"full": true}` again. `netzilo refresh` (`mod.refresh`) re-syncs but does not rebuild tunnels. `netzilo down`, `netzilo service stop` and `netzilo service restart` all log the device out; use them only with a re-enrolment plan (a setup key, or the person present for an SSO sign-in). Repeated drops: `38-device-diagnosis-method.md` §4.9 |
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
`disconnected from the Management service but will retry silently` and the matching
`disconnected from the Signal service but will retry silently` (transient; the client
keeps retrying management and signal with backoff for up to 3 months, so no restart is
needed once the path is fixed), `error while connecting to the Signal Exchange Service`.

---

## 5. Interface / driver problems

| Log message | Platform | Fix |
|---|---|---|
| `failed creating tunnel interface` / `failed to create interface` / `interface wt0 don't have an ipv4 address` | Linux | `modprobe tun`; in containers add `--cap-add=NET_ADMIN` and `/dev/net/tun`; another interface named `wt0`? use `--interface-name` |
| `couldn't access device /dev/net/tun … add flag --cap-add=NET_ADMIN` | container | add the capability / device |
| `Interface type: Userspace` on Linux | no `wireguard` kernel module (or `NB_WG_KERNEL_DISABLED`) | functional; install `wireguard` module for performance |
| `invalid interface name … Please use the prefix utun followed by a number on MacOS` | macOS | `--interface-name utun100` |
| wintun errors / no adapter | Windows | `wintun.dll` must sit next to `netzilo.exe` in `%ProgramData%\Netzilo Client\`; reinstall; AV quarantine? (`references/40-windows-hosts.md`) |
| `no firewall manager found, trying to use userspace packet filtering firewall` | Linux without nft/iptables | install `nftables` (or `iptables`) — policies still enforced by the userspace filter |
| `Default route is configured but sysctl operations failed … NB_USE_LEGACY_ROUTING=true or setting net.ipv4.conf.*.rp_filter to 2` | Linux exit-node client on hardened kernel | set the env var in the service or the sysctl |

A client that is not root (Linux, macOS) or SYSTEM (Windows) is silently forced into
**netstack** mode: no TUN device, only the local SOCKS5 proxy on `127.0.0.1` can reach
peers, and Netzilo names do not resolve through the host's resolver (they do through the
proxy with `socks5h`). This includes a Windows non-administrator install and `up -F` from
an elevated but non-SYSTEM Windows shell. The proxy port is `--socks5-port`, and without it
a run that cannot reach the system daemon uses a per-user port derived from the home
directory, not `41339`. Netstack mode is not shown by `netzilo status` or `diag.status`
(`Interface type: Userspace` / `kernelInterface: false` only means userspace WireGuard,
which is normal on macOS and Windows), and `diag.probe` / `diag.dns` test the host network
rather than the tunnel in this mode. If the symptom is "connected but nothing routes",
check whether the client runs as root/SYSTEM and whether the host has the Netzilo
interface. Used on purpose, the same mode is a quick probe peer:
`11-connectivity-diagnosis.md` §8.

---

## 6. DNS

| Symptom / log | Fix |
|---|---|
| `peer.netzilo.network` does not resolve | `netzilo status` → `Nameservers` line; Linux: first read which manager the client chose (row below), then `resolvectl status` (systemd-resolved), `nmcli device show wt0` (NetworkManager) or `/etc/resolv.conf` (resolvconf/file; should list the Netzilo resolver); macOS `scutil --dns \| grep -A3 Netzilo`; Windows `Get-DnsClientNrptRule` shows `Netzilo-Match` |
| Linux: which DNS backend is in use | `diag.grep` `{"pattern": "System DNS manager discovered"}` → `System DNS manager discovered: <networkManager\|systemd\|resolvconf\|file\|netzilo>`. The client picks it at start from the comment header of `/etc/resolv.conf`: a NetworkManager header counts only if NetworkManager answers on D-Bus in a supported version and mode; a systemd-resolved header counts only if its `127.0.0.53` stub is on (stub off → `file`); a resolvconf header → `resolvconf`; anything else → `file` (the client rewrites `/etc/resolv.conf` itself). `netzilo` means the header is the client's own from an earlier run that did not shut down cleanly | a distribution that manages `/etc/resolv.conf` by hand or with a tool the client does not recognise ends up in `file` mode, which works but is overwritten by the next tool that edits the file (`broken params` row below) |
| `the DNS manager of this peer doesn't support custom port. Disabling primary DNS setup.` | port 53 occupied on a host whose resolver cannot use a custom port | free port 53 (e.g. stop dnsmasq) or use `--dns-resolver-address 127.0.0.1:5053` with a system resolver that supports ports |
| Match-domain nameservers not applied | match domains work on macOS, Windows, and Linux with the `systemd` or `networkManager` backend; the `resolvconf` and `file` backends cannot express them, so match-only nameserver groups are ignored there | provide one primary (no match domains) nameserver group for `All`, or move the host to systemd-resolved / NetworkManager |
| `broken params in resolv.conf, repairing it...` | another tool rewrote resolv.conf | expected self-heal; consider NetworkManager/systemd-resolved |
| `restoring unclean shutdown` | previous crash left DNS altered | automatic; verify resolution afterwards |
| Windows: DNS broken after uninstall | leftover NRPT rule `Netzilo-Match` | reinstall the client and run `netzilo service uninstall` (which removes the rule), or remove the rule with `Get-DnsClientNrptRule` / `Remove-DnsClientNrptRule` |
| macOS: stale DNS after crash | `sudo netzilo service uninstall` cleans `State:/Network/Service/Netzilo-*` keys; then reinstall |
| Peer name conflict | names are made unique with a numeric suffix (`peer-1`) | rename in dashboard |

In netstack mode the host resolver is not changed, so Netzilo names do not resolve for
ordinary applications; the SOCKS5 proxy resolves them through Netzilo DNS when the client
passes names to it (`socks5h://127.0.0.1:<port>`, not `socks5://`).

---

## 7. Routes and exit nodes

| Symptom | Fix |
|---|---|
| Client does not see the route | `netzilo routes list`; the peer must be in a **distribution group** of the route; the route must be enabled; run `netzilo refresh` |
| Route present but traffic fails | policy from the client's group to the **routing peer's** group must allow the traffic; masquerade must be on unless the LAN routes back to `100.64.0.0/10`; the routing peer must be Linux with IP forwarding (the client enables it) |
| Overlapping routes (same CIDR via two networks) | `netzilo routes select <id>` to pin one; `select all` restores default |
| Exit node: no Internet | IPv6 is blocked by design (no `::/0`); add a DNS server without match domains to the same distribution group; check the exit node's own egress |
| Log `This agent version: <v>, doesn't support default routes, received <prefix>, skipping this prefix` | the client received a very wide prefix (`/7` or wider, including `0.0.0.0/0`) and refused to install it: either the client is too old for exit nodes, or it runs with `NB_DISABLE_CUSTOM_ROUTING=true` in its service environment | upgrade the client, or remove the variable (both need a service restart, which logs the device out — `06-client-cli-reference.md` §2) |
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
| `MITM: CA trust install failed (manual trust may be required)` / `MITM: no supported CA trust tool found` (Linux) | install manually: macOS `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain /etc/netzilo/netzilo-ca.pem`; Debian `sudo cp /etc/netzilo/netzilo-ca.pem /usr/local/share/ca-certificates/netzilo-mitm-ca.crt && sudo update-ca-certificates`; RHEL `… /etc/pki/ca-trust/source/anchors/ && sudo update-ca-trust extract` |
| `MITM: certutil -addstore failed` (Windows) | the CA did not reach the Local Machine Root store; from an elevated or SYSTEM shell run `certutil -addstore -f Root "%ProgramData%\Netzilo\netzilo-ca.pem"` and check that security software did not block it (`references/40-windows-hosts.md`) |
| Node-based tools (Claude Code, Codex, other CLIs) fail TLS on Windows although browsers work | the client sets `NODE_EXTRA_CA_CERTS` machine-wide, but processes started from a desktop session that already existed keep their old environment | the person signs out of Windows and back in (a new terminal is not enough), then starts the tool again |
| `MITM: existing CA files invalid (…) — regenerating` | the client created a **new** CA; every trust that was copied by hand from the old one (Firefox profiles, Java `cacerts`, Python or other CA bundles, copies of the file that `NODE_EXTRA_CA_CERTS` or `SSL_CERT_FILE` point at) is now stale | redo each manual trust step above with the new `netzilo-ca.pem`; the OS trust store is updated by the client itself |
| `MITM: user cancelled the authorization dialog — CA not installed` (macOS) | run the manual macOS command above; `sudo netzilo service restart` shows the dialog again but also logs the device out |
| `WSS server: could not load CA cert (WSS on port 41337 disabled)` | delete `netzilo-ca.pem`/`netzilo-ca-key.pem` in the config dir and restart the service (regenerates the CA, so redo manual trust as in the row above; the restart logs the device out, see `06-client-cli-reference.md` §2) |
| `MacFilter: NetziloFilterManager not found alongside daemon binary; extension must be installed manually` | the binary is not running from `/Applications/Netzilo.app`; reinstall the pkg |
| `MacFilter: manager exited with error` | approve the system extension: System Settings → General → Login Items & Extensions → Network Extensions |
| `NWFilter: init failed` / `nwfilter.exe not found` (Windows) | reinstall; check AV quarantine of `nwfilter.exe` |
| `unified proxy stopped with error` / `MCP gateway failed to start` | port 41339 / 41338 in use → `netzilo up --socks5-port <p>` / `--mcp-gateway-port <p>` |
| Node-based tools fail TLS after uninstall | leftover `NODE_EXTRA_CA_CERTS` pointing to a deleted file → remove from `/etc/environment`, `/etc/zshenv`, `/etc/profile`, or on Windows `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment` (then sign out and back in) |

More in `10-ai-security-aidr.md` §9.

---

## 10. Upgrade / install problems

| Symptom | Fix |
|---|---|
| Linux one-liner: `netzilo: command not found` afterwards | script needs `sudo` and `wget`; check `/usr/bin/netzilo` exists |
| After Linux one-liner the peer appears twice / asks to log in | the script runs `netzilo down` (logout + key reset); delete the stale peer in the dashboard, re-enrol. Replacing the binary and restarting the service does the same (a service stop is a full logout), so plan re-enrolment for every upgrade: a setup key for servers, the person present for SSO devices |
| Windows: `Admin mode is already installed, please uninstall Netzilo Client and try again.` | a per-user (non-administrator) install was attempted over an administrator install | install elevated, or uninstall first (`references/40-windows-hosts.md`) |
| Windows: `netzilo` is not recognised in a terminal | the installer adds `%ProgramData%\Netzilo Client\` to the PATH, but terminals opened before the install keep the old PATH | open a new terminal, or call `"%ProgramData%\Netzilo Client\netzilo.exe"` directly |
| macOS: CLI not on PATH | new terminal or full path; PATH line is appended to `~/.zshrc` of the installing user only |
| Dashboard says "Update available" but tray shows no update | in-app version feed is currently unavailable (404); download from the links in `05-client-install-and-deploy.md` |
| Version mismatch between "GUI" and "Service" in tray | UI and daemon from different installs; reinstall |

---

## 11. Verbose diagnostics

```bash
# runtime, no restart, reverts when the daemon restarts (device tool: mod.loglevel)
netzilo debug log level debug        # or trace
```

`debug` is enough for ICE and NAT traversal: the connection library's lines appear at
`debug`, tagged `[pion: …]`, and are suppressed below it. No environment variable and no
foreground run is needed. Reproduce, read with `diag.grep` or bundle, then set the level
back to `info`.

A **persistent** level means changing the service definition, and every way of doing that
stops the service, which logs the device out (`06-client-cli-reference.md` §2):

```bash
# any OS: bake the level into the service arguments
sudo netzilo service uninstall && sudo netzilo service install --log-level debug && sudo netzilo service start
```

Do it only when the runtime level is not enough and re-enrolment is planned (a setup key,
or the person present for SSO). The same applies to a userspace WireGuard test on Linux
(`NB_WG_KERNEL_DISABLED=true` in the service environment), which also needs a restart.
Windows service environment variables and SYSTEM-only foreground runs:
`references/40-windows-hosts.md`.

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

## 13. Environment problems that look like product faults

Four causes produce symptoms indistinguishable from a broken client. Rule them out before
deeper diagnosis, because none of them appears as a useful error message.

**Another VPN is running.** A second VPN client competing for the default route is the
most common. The client ignores a fixed list of virtual interfaces so it does not mistake
another VPN's adapter for its own, but that does not resolve contention over the default
route. Compare the routing table against the interfaces present: if another VPN holds the
default route or a more specific route to the same destination, that is the cause.
Disconnect the other client and retest. Where both must coexist, scope them to
non-overlapping destinations.

**The clock is wrong.** A device whose time is off cannot complete certificate validation
or sign-in, and the resulting errors point at TLS rather than at the clock. Check the
system time and that automatic time synchronisation is on before investigating
certificates.

**A captive portal has not been completed.** Hotel, airport and guest networks intercept
traffic until their sign-in page is completed. The symptom is identical to an unreachable
control plane. Open a browser, complete the portal, then reconnect.

**A proxy or inspection appliance sits in the path.** Corporate middleboxes that
terminate TLS will break the client's own connections. Confirm whether the customer runs
one, and exempt the control-plane hostnames.

None of these are product faults, and all four are fixed by the user in under a minute
once identified. `17-end-user-guide.md` §2 carries them in language for employees.
