---
id: '13'
title: Reading Netzilo Logs — Client and Management
requires:
- server-shell
- client-device
executable_on:
- netzilo-harness
- human-operator
chars: 58338
sections:
- id: '1'
  title: Method
  chars: 806
- id: '2'
  title: Line anatomy (same on client and management)
  chars: 1957
- id: '3'
  title: Profile a log in one minute
  chars: 1697
- id: '4'
  title: The client log
  chars: 37692
- id: '5'
  title: The management log
  chars: 10660
- id: '6'
  title: Correlating client and server
  chars: 1342
- id: '7'
  title: Worked readings (from real logs, identifiers replaced)
  chars: 2614
- id: '8'
  title: When the log does not explain it
  chars: 371
---
# Reading Netzilo Logs — Client and Management

> **Getting the lines.** From the dashboard assistant and the harness, the client log of a
> connected peer is read directly with `diag.logs` (tail) and `diag.grep` (regex search on
> the device, most recent matches first, with `context` lines, across rotated `.gz` logs
> with `all_files: true`). Search on the device and read excerpts; never pull a whole log.
> Tool cards: `references/37-device-tool-reference.md` §9; the "it was working
> yesterday" playbook: `references/38-device-diagnosis-method.md` §4.6.

**Use this when you are handed a log and asked "what went wrong?"** — the reverse of the
troubleshooting runbooks, which start from a symptom. Everything here is observable
output: the strings the software writes into the customer's own log files, the order
they appear in on a healthy system, and what each family means. The examples are taken
from real client and management logs with identifiers replaced by placeholders.

Companion files: `07-client-troubleshooting.md` §9 (error string → fix),
`03-server-troubleshooting.md` §2/§4a (server strings → fix),
`12-escalation-package.md` (collecting logs for code-level analysis).

---

## 1. Method

1. **Profile before reading.** A client log is dominated by a handful of repeating lines;
   40,000 lines usually collapse to 30 templates. Count first, read second (§3).
2. **Find the last healthy state, then the first thing that broke after it.** Healthy
   states are recognisable sequences (§4.3, §5.2); the first deviation is the lead. When
   the server refused the device (an `rpc error: code = … desc = <reason>` on a login or
   on the live session), go straight to the reason table in §4.8.
3. **Separate noise from signal.** Several loud `WARN`/`ERRO` families are benign or
   cosmetic (§4.6, §5.4). Ruling them out first prevents chasing the wrong line.
4. **Then correlate** across client and server on the WireGuard public key and on
   timestamps converted to UTC (§6).

---

## 2. Line anatomy (same on client and management)

```
2026-09-12T07:42:51-04:00 INFO <source>: gRPC Management connection established - State: READY
2026-09-12T06:37:52Z INFO [accountID: <account-id>, context: GRPC, peerID: <key>] <source>: peer <key> authenticated via client session flow (dashboard)
```

| Field | Meaning | Pitfalls |
|---|---|---|
| Timestamp | RFC 3339 in the **host's local time with its UTC offset**. Containers usually run in UTC and print `Z`. | The offset can **change within one file** when a laptop moves time zones (observed: `+03:00` then `-04:00`). Convert everything to UTC before comparing client and server. Event payloads shown in the dashboard are UTC. |
| Level | `PANC` `FATL` `ERRO` `WARN` `INFO` `DEBG` `TRAC` | `ERRO` is not always an incident (§4.6). |
| `[key: value, …]` | present on management lines that belong to a request: `context` (`GRPC`, `HTTP`, `SYSTEM`), `requestID`, `accountID`, `peerID` (= the peer's WireGuard public key), `userID`. Some client lines carry `[upstream: …, error: …]`, `[nameservers: …]` or `[key: …]`. | Not every line has it; lines without a bracket cannot be attributed to a request. `requestID` exists only server-side. **The order of the fields inside the bracket is not fixed** and changes from line to line: never grep for a fixed sequence such as `context: GRPC, requestID`; grep for one field at a time (`peerID: <key-prefix>`). |
| `<source>` | a source-location prefix (file and line) the software prints on every line | useful only for the vendor; ignore it when reading and strip it before grouping (§3) |
| Message | free text; identifiers inside are often **truncated** (8- or 20-character key prefixes) | match keys by prefix, take full values from `netzilo status -d` |

macOS system-extension logs (`netzilofilter.log`, `netzilosecurity.log`) use a different
layout: `[YYYY-MM-DD HH:MM:SS.mmm] [LEVEL] Component: message`, local time **without** an
offset.

---

## 3. Profile a log in one minute

Works on `client.log`, `docker compose logs management`, or a `kubectl logs` capture.
The sanitiser collapses IPs, keys, UUIDs and numbers so identical events group together
and nothing sensitive ends up in your notes.

```bash
F=client.log   # or: docker compose logs --no-color --since 24h management > mgmt.log
SAN='s/^[0-9T:.+Z-]+ //; s/\[[^]]*\] //; s/[A-Za-z0-9_\/.-]+\.go:[0-9]+: /<source>: /; s/[0-9]{1,3}(\.[0-9]{1,3}){3}(:[0-9]+)?/<ip>/g; s/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/<uuid>/g; s/[A-Za-z0-9+\/=_-]{40,}/<key>/g; s/(^|[^a-z0-9])[a-z0-9]{20}([^a-z0-9]|$)/\1<id>\2/g; s/[^ ]+@[^ ]+/<email>/g; s/[0-9]+/N/g'

# span and volume
wc -l "$F"; head -1 "$F" | cut -c1-60; tail -1 "$F" | cut -c1-60
# level mix
grep -oE '^[0-9T:.+Z-]+ (TRAC|DEBG|INFO|WARN|ERRO|FATL|PANC)' "$F" | awk '{print $2}' | sort | uniq -c | sort -rn
# what the log is mostly saying
cut -c1-400 "$F" | sed -E "$SAN" | sort | uniq -c | sort -rn | head -40
# only the problems
grep -E '^[0-9T:.+Z-]+ (WARN|ERRO|FATL|PANC)' "$F" | cut -c1-400 | sed -E "$SAN" | sort | uniq -c | sort -rn | head -30
# a window around an anchor (first occurrence), noise filtered
NOISE='ingest queue full|enrichment slots|MITM BYPASS pipe closed|MCP event: type=llm'
A=$(grep -n 'Network monitor detected network change' "$F" | head -1 | cut -d: -f1)
sed -n "${A},$((A+300))p" "$F" | grep -vE "$NOISE" | head -60
```

Read the template list top-down: the top entries tell you what mode the system is in
(steady state, reconnect loop, AI traffic heavy, DNS trouble). Then read the WARN/ERRO
list against §4.6 / §5.4 and discard the benign ones. What remains is the story.

---

## 4. The client log

### 4.1 Files

| File | Where | Contents |
|---|---|---|
| `client.log` | `/var/log/netzilo/` (Linux, macOS), `%PROGRAMDATA%\Netzilo\` (Windows) | the daemon log; rotates at 5 MB into `client-<UTC timestamp>.log.gz`, 10 backups, 30 days. **Rotated file names are UTC** even though lines inside are local time. |
| `netzilofilter.log`, `netzilosecurity.log` | same directory, macOS only | the two system extensions (network filter, endpoint security). Different format (§2). Included in the debug bundle because they share the directory. |
| `Netzilo.err.log`, `Netzilo.out.log` | `/var/log/` on macOS (outside the bundle); inside `/var/log/netzilo/` on Linux | service stdout/stderr. `err.log` is normally dominated by `http: TLS handshake error from 127.0.0.1:… client sent an HTTP request to an HTTPS server` and `remote error: tls: unknown certificate` — local tools probing the daemon's TLS port with plain HTTP or without trusting its certificate. High volume, not a fault. A **panic traceback** would also land here. `out.log` carries browser-policy and macOS `Failed to kickstart … preferences daemon` messages — cosmetic. |

The directory is readable only by root on macOS (`drwxr--r--`); the debug bundle or
`sudo` is required.

### 4.2 Healthy daemon start (observed order)

```
Starting netzilo service
Starting netzilo service unix:///var/run/netzilo.sock
NWFilter: pipe server started (service-level)                 ← Windows helper channel, logged on every OS
Starting MCP gateway in daemon mode...
Starting MCP Gateway on port 41338...
Database path: … mcp.db  /  Mode: <mode>
MCP Gateway IPC service started / Gateway IPC service started
Posture scanner filter initialized … cache duration: 5m0s
Static scanner filter initialized (awaiting rules via IPC)
[analysis] dataflow handler added / posture scanner added / static scanner added / semantic classifier added
MITM: WASM LLM parser hot-loaded (N bytes) / MITM: embedded WASM parser loaded
MCP gateway started successfully on port 41338
OAuth token refresh service started
MITM: loaded CA from <configdir>/netzilo-ca.pem
starting Netzilo client version <version> on <os>/<arch>       ← the version line
started daemon server: <socket>
[aidr] started
Starting WSS server on <addr>                                      ← the browser-extension channel, normally localhost:41337
MITM: TLS interception enabled (configDir="…")
MITM engine ready on 127.0.0.1:<port> (HTTP/2-capable) / MITM: proxy initialized successfully
MITM: wired to MCPGateway agent chain (Register)
unified proxy starting on 127.0.0.1:41339
WASM [semantic-classifier]: updated to <version> / WASM [parser]: updated to <version>   ← hot-loaded bundles from the download server
```

Anything missing from this list at boot (for example no `MCP gateway started`, or
`WSS ListenAndServeTLS() failed … bind: address already in use`) points at a port
conflict or a second daemon instance.

### 4.3 Healthy connect (observed order)

```
using Management URL https://<domain>:443
new Admin Panel URL provided, updated to "https://<admin>:443"
generated new Wireguard key / generated new SSH key                ← only on first login or after logout
using default Wireguard port 51820 / Sock5Port 41339 / WebServPort 41336 / interface utun100|wt0
filling in interface blacklist with defaults: […]
using default DNS route interval 1m0s / MCP Gateway port 41338
loginToManagement DNS <hostname>.<dns-domain>
peer has been successfully registered on Management Service      ← registration (first time)
Routing setup complete
DNS loopback listener started on 127.0.0.1:53 / dns service listening on: <addr>
Upstream nameserver <ip> with type udp                             ← one per distributed resolver
added N search domains to the state. Domain list: "" <dns-domain>
connected to the Signal Service stream
gRPC Signal connection established - State: READY
connected to the Management Service stream
gRPC Management connection established - State: READY
Building network map: N policies, N groups, N peers
Policy evaluation complete: N connectable peers found
peer <key> ICE connection state changed to Connected - ICE layer established
peer <key> WireGuard peer configured: endpoint=<ip:port>, allowedIPs=<overlay-ip>/32, type=host->host
peer <key> connection established successfully [<overlay-ip>]: direct=true, relayed=false, ice=host->host
Sync triggered with forceSync=false / Sync completed successfully
```

Where the sequence stops tells you the layer that failed: no `READY` for management →
control plane unreachable; management `READY` but no signal `READY` → signal path;
both `READY` but no `ICE … Connected` → NAT/relay; `connection established` but the
user still cannot reach the host → policy, route, or the target (see
`11-connectivity-diagnosis.md`).

The `connection established` line carries the verdict in one place: `direct=true,
relayed=false, ice=host->host` is a direct path; `relayed=true` means TURN is carrying
the traffic; `ice=…` shows candidate types (`host`, `srflx`, `relay`) on each side.

A logout or `netzilo down` shows `can't remove file …/token.dat: no such file or
directory` when the device never logged in with SSO — harmless.

### 4.4 The network-change cycle (normal on laptops)

Every Wi-Fi switch, VPN toggle, sleep/wake or docking produces this block. It is loud
and full of `ERRO`, and it is **expected**:

```
Network monitor: default route changed: via <ip>, interface <nil>
Network monitor detected network change, restarting engine
SecurityFilter: disconnected, retrying in 3s                          ← macOS extension IPC drops during restart
Posture check '<name>' FAILED at NetziloChecks  (repeated per check)  ← re-evaluated on every rebuild, see §4.5
Policy evaluation complete: N connectable peers found
Network monitor: stopped
removing search domains from the system / removing match domains from the system   ← macOS
Routing cleanup complete
stopped Netzilo Engine
exiting the Signal service connection retry loop due to the unrecoverable error: context canceled
exiting the Management service connection retry loop due to the unrecoverable error: context canceled
failed while getting Management Service public key: rpc error: code = Canceled desc = context canceled
Stopping previous engine before creating new one
Routing setup complete → DNS loopback listener started → … → gRPC … READY → peer … connection established
```

The `context canceled` errors are the old engine being torn down while the new one
starts. They are a problem only if the sequence **does not** end in `READY` lines.
The same `exiting the … retry loop due to the unrecoverable error:` text followed by
`rpc error: code = PermissionDenied desc = <reason>` instead of `context canceled` is
**not** teardown: the server ended the session. Read the reason in §4.8.

Two macOS-only lines appear in bursts around route changes and are cosmetic:
`Network monitor: error parsing routing message: parse RIB: invalid address` and
`Network monitor: read from routing socket returned less than expected: N bytes`.

### 4.5 Message families and what they mean

Peer lines are keyed by the **WireGuard public key** of the other peer (full, or an
8/20-character prefix), never by its name or overlay IP. Map a key to a device with
`netzilo status -d` on this device or `GET /api/peers` (match on the key prefix).

**Management connection**

| Line | Meaning |
|---|---|
| `Failed to resolve host <domain>: lookup <domain>: no such host` | the host has no working DNS at that moment (usually mid network change). Persistent → the device's resolver or the domain is wrong |
| `failed creating connection to Management Service: <error>` (ERRO) | the client could not even set up the connection (bad management URL, TLS or certificate problem, proxy). The engine start then fails with `failed connecting to Management Service : <error>`. Check the URL and that `https://<domain>` opens from the device |
| `failed while getting Management Service public key: rpc error: code = Unavailable desc = …` | TCP/TLS to the management endpoint failed (connection reset, read error) |
| `… code = DeadlineExceeded desc = context deadline exceeded` | timed out — firewall, proxy, or the server not answering |
| `… code = Canceled …` / `exiting the Management service connection retry loop due to the unrecoverable error: context canceled` | teardown during restart; benign unless nothing reconnects |
| `exiting the Management service connection retry loop due to the unrecoverable error: rpc error: code = PermissionDenied desc = <reason>` (WARN) | **not teardown**: the server ended this device's live session (login expired, peer deleted, user blocked). The device goes to *Needs login*. Look the reason up in §4.8 |
| `failed to login to Management Service: rpc error: code = <code> desc = <reason>` (ERRO) | the server refused a login or registration. The reason text is the diagnosis, §4.8. The daemon repeats it as `failed login: …` (WARN for `InvalidArgument`/`PermissionDenied`, ERRO otherwise) |
| `failed to login to Management Service: rpc error: code = PermissionDenied desc = no peer auth method provided, please use a setup key or interactive SSO login` | the device's key is not registered (deleted peer, reset config, or first run). Follows on `netzilo up` right before SSO/registration; persistent → re-enrol |
| `gRPC Management connection disconnected - State: <state>, Error: <error>` then `gRPC disconnect details - Code: <code>, Message: <message>` (both WARN) | the management connection dropped; the second line carries the gRPC code and the server's message. `Unavailable` / `EOF` = network or server restart, reconnects on its own; `PermissionDenied` + a reason = §4.8 |
| `disconnected from the Management service but will retry silently. Reason: EOF` | server closed the stream (restart, deploy); the client reconnects on its own |
| `could not sync meta with reply: …` / `Error pushing events: …` | side effects of the management connection being down; not separate faults |
| `connected to the Management Service stream` → `gRPC Management connection established - State: READY` | healthy |

**Engine start and tunnel interface**

| Line | Meaning |
|---|---|
| `error while starting Netzilo Connection Engine: <error>` (ERRO) | umbrella line: the engine did not start. **The inner text is the cause** (for example `create wg interface: …`, `up wg interface: …`, `enable server router: …`); read the lines just before it for the detail. The client retries |
| `failed to pull up wgInterface [<name>]: <error>` (ERRO) | the tunnel interface was created but could not be brought up (permissions, a conflicting interface or VPN, a leftover interface from a crashed daemon). Restart the service; if it persists, look for another VPN or tunnel software on the device |
| `failed creating firewall manager: <error>` (ERRO), on Linux preceded by `failed to create nftables manager: <error>` or `failed to create iptables manager: <error>` | the client could not program the host's packet filter. Access rules and routing on this device will not work as expected. Typical causes: a container without `NET_ADMIN`, missing kernel modules, or a host firewall tool holding the tables. Fix the backend, then restart the service |

**Signal**

| Line | Meaning |
|---|---|
| `connected to the Signal Service stream` → `gRPC Signal connection established - State: READY` | healthy |
| `failed to connect to the signalling server: <error>` (ERRO) / `error while connecting to the Signal Exchange Service <uri>: <error>` | the signal endpoint is unreachable or its TLS failed; the engine cannot negotiate peer connections. Check that the signal URL received from management is reachable from the device (`11` §2) |
| `gRPC Signal connection disconnected - State: <state>, Error: <error>` (WARN) / `disconnected from the Signal service but will retry silently. Reason: <error>` (WARN) | the signal stream dropped and the client reconnects on its own. Established tunnels keep working; new peer connections wait until it is back. Continuous → network or proxy between device and signal |
| `disconnected from the Signal Exchange due to an error: didn't receive a registration header from the Signal server whille connecting …` | the stream opened but registration did not complete — typically the network dropped mid-handshake |
| `error while handling message of Peer [key: <key>] error: [wrongly addressed message <key>]` | the key is the **sender**: a peer that has this device in its network map sent it a connection offer, but that peer is **not in this device's map**. The two sides see policy differently (a rule, group or posture check admits the pair on one side only, or one side holds a stale map). Occasional right after a policy or group change: harmless, the next auto-sync fixes it. **Repeating for the same key**: find that peer by key, then compare what the policies and posture checks allow for the two devices (`20` §6); `netzilo status -d` on both shows whether each lists the other |
| `🔄 Auto-sync triggered for unknown peer <8-char prefix>` → `✅ Auto-sync completed for unknown peer …` | a message came from a peer not in the local network map; the client pulled a fresh map. Normal when peers are added; a tight loop means the map never includes that peer (policy/group) |

**Peer connections**

| Line | Meaning |
|---|---|
| `peer <key> ICE connection state changed to Connected - ICE layer established` | a path was found |
| `peer <key> ICE connection state changed to Disconnected - waiting for recovery` | a transient loss; the connection may recover by itself |
| `peer <key> ICE connection state changed to Failed - connection lost` | the path to that peer is gone (network change, the far side went offline). The client retries; recurring for one peer → `11` §2 |
| `peer <key> WireGuard peer configured: endpoint=…, allowedIPs=…, type=host->host` | tunnel endpoint set; `type` shows candidate pairing |
| `peer <key> connection established successfully [<overlay-ip>]: direct=…, relayed=…, ice=…` | the verdict line (§4.3) |
| `failed to establish connection to peer <key>: connection to peer <key> timed out after <duration>` (WARN) | no path was negotiated in time; the client keeps retrying. For one peer only → that peer is offline or does not answer over signal; for every peer → UDP blocked and no working relay (`11` §2) |
| `failed to establish connection to peer <key>: disconnected from peer <key>` | ICE gave up or the far side went away; recurring for one peer → that peer is offline or both sides lack a usable path (`11` §2) |
| `Connection has been already closed or attempted closing not started connection <key>` | cleanup of a connection that never completed; benign on its own |
| `Building network map: N policies, N groups, N peers` / `Policy evaluation complete: N connectable peers found` | how many peers this device is *allowed* to talk to after policies and posture. `0 connectable peers` with peers present = policy or posture blocks everything |
| `Posture check '<name>' FAILED at <check>` where `<check>` is `NBVersionCheck`, `OSVersionCheck`, `GeoLocationCheck`, `NetworkRangeCheck`, `NetziloChecks` or `DateTimeCheck`; and `❌ Posture check '<name>' (ID=…) FAILED` | this device fails that check; the policies/filters using it are excluded for this device. The suffix names the failing condition: client version, OS version, country, source network range, endpoint-security items, or time window (`08` §7). Logged at `ERRO` although it is a policy outcome, not a fault |

**Relays (STUN/TURN configuration)**

| Line | Meaning |
|---|---|
| `failed to parse TURN URI '<uri>': <error> - skipping this server` (ERRO) | one relay entry sent by management is malformed; the others are used. Fix the entry in Integrations → Networking → TURN/STUN Servers (`08` §8) |
| `no valid TURN servers received, keeping existing configuration` (WARN) | every relay entry in the update was unusable; the device keeps its previous relays. A new device in this state has no relay: fix the relay configuration on the server |

**Routes**

| Line | Meaning |
|---|---|
| `The network [<id>] has not been assigned a routing peer as no peers from the list [<keys>] are currently connected` (WARN) | the route exists, but none of its routing peers is connected to this device right now. Check that the routing peers are online and that a policy lets this device reach them (`22`) |
| `Prefix [<prefix>] is already routed by peer [<key>]. HA routing disabled` / `IP [<ip>] for domain [<domain>] is already routed by peer [<key>]. HA routing disabled` (WARN) | the same prefix is published by two routes through different routing peers that are not one network; only one path is used and failover between them is off. Give them the same network identifier (or one peer group) if they are meant to be HA (`08` §5) |
| `Failed to resolve domains for route [<route>]: <error>` (ERRO) | a domain route could not be resolved on this device; traffic for those names is not routed. Check DNS on the device and that the domains exist |
| `This agent version: <v>, doesn't support default routes, received <prefix>, skipping this prefix` (WARN) | an exit-node (`0.0.0.0/0`) or other very wide route is ignored on this device. Two causes: the client is too old for default routes (upgrade it, `05` §7), or the service runs with custom routing switched off (`NB_DISABLE_CUSTOM_ROUTING=true` in its environment, common in containers). Other routes still work |

**DNS**

| Line | Meaning |
|---|---|
| `DNS loopback listener started on 127.0.0.1:53` / `dns service listening on: <addr>` | local resolver up |
| `binding dns on <addr> is not available, error: <error>` (WARN) | the preferred listen address is taken (another resolver on port 53); the client tries the next address. Only a problem if no `dns service listening on` follows |
| `dns server running with <port> port returned an error: <error>. Will not retry` (ERRO) | the local resolver stopped and will not restart by itself; peer names stop resolving. Restart the service; find what else holds the port |
| `Upstream nameserver <ip> with type udp` | distributed nameserver groups received |
| `skipping nameserver <ip> with type <type>, this peer supports only udp` (WARN) | a nameserver in the group is not a UDP resolver; it is ignored on this device |
| `received a nameserver group with an invalid nameserver list` (ERRO) | after skipping, a group had no usable nameserver; its domains get no resolver. Fix the group in Network → DNS |
| `got an error while connecting to upstream` with `read udp …: i/o timeout` | the upstream did not answer through the tunnel — route/policy to the resolver, or resolver down |
| `got other error while querying the upstream` with `network is unreachable` / `destination address required` / `socket is not connected` / `operation was canceled` | no network at that moment (transition) — benign in bursts around network changes |
| `all queries to the upstream nameservers failed with timeout` (ERRO) | one query failed on every server of the group; each upstream has a 15-second timeout |
| `Temporarily deactivating nameservers group due to timeout` (with `[nameservers: …]` in the bracket) → `Upstream resolving is Disabled for 5s` | after **five consecutive** failed queries the group is deactivated. The `5s` is only the probe interval: the group stays off **until one of its upstreams answers again**, then `upstreams [<list>] are responsive again. Adding them back to system` is logged. While it is off its domains are removed from the host's DNS configuration, so those queries fall to the operating system's other resolvers (and names only the private resolver knows fail). A group that never comes back → route/policy to the resolver, or the resolver is down |
| `not applying the dns configuration update as there is nothing new` | benign |
| `Unable to get system DNS configuration` / `unable to update record of System's DNS config: couldn't get current DNS config: couldn't find the primary service key` | macOS resolver state not readable during transition; persistent → `07` §6 |

**AI security (MITM, gateway, scanners)**

| Line | Meaning |
|---|---|
| `MITM: loaded CA from …` / `MITM: TLS interception enabled` / `MITM engine ready` / `MITM: proxy initialized successfully` / `unified proxy starting on 127.0.0.1:41339` | interception stack up |
| `MITM: existing CA files invalid (<error>) — regenerating` (WARN) | the local interception CA on disk could not be read or no longer matches; the client creates a new one. **Browsers and tools that trusted the old CA will show certificate errors** until the new CA is trusted again (`07` §9). One-off after a corrupted or hand-edited config directory; repeating on every start → the directory is not writable or is being reset |
| `MITM: engine init failed (<error>) — falling back to HTTP/1.1-only interception` (WARN) | the HTTP/2-capable interception engine did not start; interception continues over HTTP/1.1 only. AI traffic is still inspected, but HTTP/2-only clients may bypass or fail. Restart the service; persistent → collect per `12` |
| `WASM [parser]: updated to <version>` / `WASM [semantic-classifier]: updated to <version>` | parser bundles refreshed from the download server |
| `WASM [<name>]: download HTTP <code> from <url>` (WARN) | the bundle download server answered with an error status; the client keeps the embedded or previously downloaded bundle. `403`/`404` = wrong download URL or bundle not published; repeated `5xx` = the download server. Connectivity from the device to that URL is the check |
| `WASM [<name>]: checksum mismatch (got …, want …) — skipping update` (WARN) | the downloaded bundle does not match its published checksum (truncated download, a proxy rewriting the file, or a half-published release); the client keeps the bundle it has. Recurring → look at what sits between the device and the download server |
| `Gateway IPC: updating static rules (version: mgmt-sync-N, N rules, N filter profiles)` → `[scanner] Rules updated: N loaded, N failed …` → `✓ Successfully updated MCP Gateway filters: N filters applied` | rules and filters delivered from management. `0 filters applied` = no filter matches this device (`29` §5). `N failed` > 0 = a rule did not parse |
| `Failed rules: [<rule ids>]` (WARN) | the rules named did not load on this device (bad YAML or an unsupported field); every other rule is active. Fix those rules in the scanner catalogue (`28` §7) — the device cannot repair them |
| `Gateway static rules update failed: <error>` (ERRO) | the whole rule push to the local gateway failed; the device keeps the previous rule set. Usually the local gateway process is not running (no `MCP gateway started` at boot, §4.2) — restart the service |
| `[OAuth Refresh] Token for server <server> expired <duration> ago and cannot be refreshed (max window: 24h). Re-authorization required.` (WARN) | a stored OAuth token for a remote MCP server has been expired for more than a day and the client will not refresh it; calls to that server fail with authentication errors until the user authorises it again from the client (`27` §5). Not a network fault |
| `MCP event: type=llm.request server=<host> tool=llm_request status=success action= duration_ms=N` (and `llm.response`) | an intercepted LLM call; `action=` empty = allowed |
| `MCP event: type=security.staticscanner.detect … action=redact` / `action=detect` / `action=block` | a rule fired; `detect` = report-only |
| `[scanner] Scan [tool_output] blocked=false triggered=N loaded=N version=mgmt-sync-N time=N.Nms` | one evaluation; `blocked=true` would be a block |
| `MITM BYPASS pipe closed: client=… upstream=<ip:port> client→upstream=N bytes upstream→client=N bytes duration=…` | a flow that was passed through without inspection (excluded domain, non-HTTP, or not an intercepted app) — informational |
| `[aidr] ingest queue full, dropping event` | back-pressure in the behaviour-graph ingester; events are being lost. Bursts of thousands during heavy AI traffic. Cosmetic for connectivity; matters if session snapshots look incomplete |
| `enrichment slots saturated (N), skipping URL enrichment for <url>` | metadata enrichment skipped under load; cosmetic |
| `SecurityFilter: connected to extension at <addr>` / `SecurityFilter: disconnected, retrying in 3s` / `MacFilter: extension IPC disconnected, retrying in 3s` | macOS system-extension link; reconnects on its own. Never connecting → extension not approved (`07` §9) |
| `WSS ListenAndServeTLS() failed: listen tcp 127.0.0.1:41337: bind: address already in use` | another process (or a second daemon) holds the local TLS port; the browser-extension channel is down |

**Windows network filter helper (NWFilter)**

On Windows the per-application network filter runs as a helper process that the service
starts and supervises. Its lines are prefixed `NWFilter:`.

| Line | Meaning |
|---|---|
| `NWFilter: pipe server started (service-level)` / `NWFilter: pipe server started` | the channel to the helper is up (the first form is logged on every OS at service start, the second by the engine) |
| `NWFilter: nwfilter.exe (PID=<n>) exited unexpectedly — restarting in <duration>` (WARN) | the helper crashed or was killed and the service restarts it with a growing back-off. Once after an upgrade or a security product scan is harmless. **Repeating** → the helper is being terminated (endpoint-protection software, a driver conflict); check the Windows event log for `nwfilter.exe` and exclude it in the security product |
| `NWFilter: timeout waiting for initial proxy ACK` (WARN) | the helper started but never confirmed that it is redirecting traffic; application filtering and interception on this device are not active until the next successful start. Restart the service; persistent → the helper's driver is not loaded (a reboot after install is the usual fix) |
| `NWFilter: rule push failed: <error>` (WARN) | the current rule set could not be delivered to the helper; it keeps the previous rules. Appears together with the two lines above when the helper is down; alone → restart the service |

### 4.6 Noise you can rule out immediately

`[aidr] ingest queue full, dropping event` · `enrichment slots saturated` ·
`MITM BYPASS pipe closed` · `Network monitor: error parsing routing message` /
`read from routing socket returned less than expected` (macOS) · the `context canceled`
family inside a restart cycle · `got other error while querying the upstream` with
`network is unreachable` during a network change · `can't remove file …/token.dat` ·
`Posture check … FAILED` when the device is *supposed* to fail that check · everything in
`Netzilo.err.log` matching `TLS handshake error`.

### 4.7 What more verbosity adds

`netzilo debug log level debug` (in memory only; lost on restart) adds three things you
cannot get otherwise: **all ICE/STUN/TURN negotiation detail** (at `info` there is none),
a **full dump of the received network map** (every policy, rule, group, peer with IDs
and connected/login-expired flags), and **`Buffered event: {…}`** — the exact JSON of
every event later shown in the dashboard. `trace` adds little beyond per-connection
state churn. WireGuard's own handshake log is a separate switch (`NB_WG_DEBUG=true`,
restart required).

### 4.8 The server refused the device: the reason table

When management rejects a device, the **reason text** is the diagnosis. It reaches the
log in one of three shapes; recognise the shape first, then look the reason up below.

| Shape | Where | What it tells you |
|---|---|---|
| `failed to login to Management Service: rpc error: code = <code> desc = <reason>` (ERRO), repeated by the daemon as `failed login: rpc error: …` (WARN when the code is `InvalidArgument` or `PermissionDenied`, ERRO otherwise) | client log, during `netzilo up`, at service start, and on every reconnect | a **login or registration** attempt was refused |
| `exiting the Management service connection retry loop due to the unrecoverable error: rpc error: code = PermissionDenied desc = <reason>` (WARN), usually right after `gRPC Management connection disconnected - State: …, Error: …` and `gRPC disconnect details - Code: PermissionDenied, Message: <reason>` | client log, while the device was **already connected** | the server ended a **live session**. The device goes to *Needs login*. Only `context canceled` in this position is teardown (§4.4); a `PermissionDenied` reason never is |
| `login failed: rpc error: code = <code> desc = <reason>` | what `netzilo up` / `netzilo login` print on the terminal | the server answered with `InvalidArgument`, `PermissionDenied`, `NotFound` or `Unimplemented`: the command stops **immediately** — retrying will not help until the cause is fixed |
| `login backoff cycle failed: rpc error: code = <code> desc = <reason>` | same commands | any other code (`Unavailable`, `DeadlineExceeded`, `Internal`, **`FailedPrecondition`**): the command retried for about half a minute and gave up. `Unavailable`/`DeadlineExceeded` = the server was not reachable; `FailedPrecondition` = a definite refusal that merely took the retry path (invalid setup key, registration race — see below) |

Codes as the client sees them: authentication and permission problems arrive as
`PermissionDenied`; "the object is not right" problems as `FailedPrecondition`; "the
object does not exist" as `NotFound`. A reason the server does not translate arrives as
`code = Internal desc = failed handling request`: the real text is then only in the
management log, on a line `got an unhandled error: <reason>` at the same second (§6).

| Reason (`desc = …`) | Code | What happened | What to do |
|---|---|---|---|
| `no peer auth method provided, please use a setup key or interactive SSO login` | `PermissionDenied` | the server does not know this device's key and the request carried neither a setup key nor a login token. **Normal once** at the start of `netzilo up` on a fresh device (the SSO or registration step follows). Persistent, or on a device that used to work → the peer was deleted, or the config was reset | let the login finish; otherwise re-enrol (`netzilo up` with SSO or a setup key). Server side this is the WARN `failed logging in peer <key>: no peer auth method provided…` (§5.4) |
| `peer login has expired, please log in once more` | `PermissionDenied` | an SSO-enrolled peer passed the account's login-expiration (or inactivity) period. On the live session the device is disconnected at that moment; the peer shows **Login required** | the user runs `netzilo up` (or logs in from the tray). To stop it recurring on a server, enrol with a setup key or disable login expiration for that peer (`24` §1). The management log shows one ERRO `failed checkIFPeerNeedsLoginWithoutLock <key>: peer login has expired, please log in once more` per attempt — expected, not a fault |
| `peer is not registered` | `PermissionDenied` (live session) | the peer was **deleted on the server while the device was running** (admin delete, bulk clean-up, user deleted, ephemeral peer expired) | the device must re-enrol: `netzilo up` with SSO or a new setup key. Subsequent automatic attempts show `no peer auth method provided…` until then. Check Activity for `user.peer.delete` / `peer.remove` on that peer |
| `user is blocked` | `PermissionDenied` | the peer's owner is blocked in Team → Users; every peer of that user is refused | intended for offboarding. If not intended, unblock the user (`25` §6) |
| `failed adding new peer: account not found` | `NotFound` | the **setup key is not known to this server at all**: a typo, a key created on another server, or the client points at the wrong management URL | check `netzilo status` / the client config for the management URL; create a new key on the right server (`24` §6). Where the server can attribute the attempt to an account it records `user.failedlogin` with `error_type` `key_not_found` |
| `couldn't add peer: setup key is invalid` | `FailedPrecondition` (so: `login backoff cycle failed`) | the key exists but is **expired, revoked or over its usage limit** | Activity → Events shows `user.failedlogin` with `auth_method: setup_key`, `setup_key_name`, `peer_hostname`, and `error_type` = `expired`, `revoked` or `over_used` (with `usage_limit` and `used_times`); `reason` reads `Setup key expired: <key>`, `Setup key revoked: <key>` or `Setup key usage limit exceeded: <key>`. Create a new key or raise the limit (`24` §3) |
| `maximum number of personal peers reached` | `PermissionDenied` | the account is on the Free plan and already has its 100 devices | remove stale peers or upgrade (`31` §2). Treat the plan as the cause **only** when this exact text is present |
| `peer has been already registered` | `FailedPrecondition` (so: `login backoff cycle failed`) | two registrations of the same key crossed: `netzilo up` run twice at once, or a retry overtaking the first attempt that had already succeeded | run `netzilo status`; the device is usually registered. If it is not, `netzilo down` then `netzilo up` once |
| `invalid jwt token: Error parsing token: Token is expired` / `… Token is not valid yet` / `… Token used before issued` | `PermissionDenied` | the login token's time claims do not fit the server's clock. `is expired` on a token obtained seconds earlier, or `not valid yet` / `used before issued` = **the device or the server clock is wrong**; `is expired` after a long SSO dialogue = the token aged out before the client used it | fix the clock (device first, then server), run `netzilo up` again |
| `invalid jwt token: invalid audience` / `invalid jwt token: invalid issuer` | `PermissionDenied` | the token was issued for a different application or by a different issuer than the server accepts: the server's authentication settings and the identity-provider client the device used disagree | `04` §5.1 (self-hosted: `03` §3). Always a configuration mismatch, never the user |
| `invalid jwt token: Error parsing token: … unable to find appropriate key` | `PermissionDenied` | the token is signed with a key the server cannot find at its configured key location (the server points at another identity provider, or the provider rotated keys and the server has not yet reloaded) | check the identity configuration (`04` §8); the management log carries a WARN `token signed with a key the IdP does not publish` |
| `invalid jwt token: token has been revoked` | `PermissionDenied` | the token was revoked (a logout) before the device used it | run `netzilo up` again |
| `invalid jwt token: token is invalid` | `PermissionDenied` | the token parsed but failed validation for another reason (malformed claims) | `04` §5.1; collect `12` if it persists for one identity provider |
| `unable to fetch account with claims: <error>` | `Internal` (so: `login backoff cycle failed`) | the token was valid but no Netzilo account could be found or created for that user | check that the user exists in Team → Users (or that same-domain auto-join applies, `04` §1); the inner text names the reason |
| `user does not belong to any of the allowed JWT groups` | `PermissionDenied` | Settings → Groups → *JWT allow group* is set and the user's token claim does not contain it | `25` §7 (fix the group in the identity provider, or clear the allow group) |
| `invalid user` / `can't login with this credentials` | `PermissionDenied` | the SSO user who logged in is **not the owner of this peer** (the device was enrolled by another user) | log in as the owner, or delete the peer and re-enrol as the new user. The management log has a WARN `user mismatch when logging in peer <id>: peer user <a>, login user <b>` |
| `client session authentication not configured` | `Unimplemented` | the dashboard tried to log this device in through the browser session, but the server has no client-session audience configured | self-hosted: `03` §3. Meanwhile `netzilo up` (SSO or setup key) works |
| `no pkce authorization flow information available` / `no device authorization flow information available` | `NotFound` | the server has no interactive-login flow configured for this hostname. The client logs `server couldn't find pkce flow, contact admin: …` or `server couldn't find device flow, contact admin: …` (WARN) first | a server configuration problem (`03` §3, `04` §8); use a setup key until fixed |
| `the management server, <url>, does not support SSO providers, please update your server or use Setup Keys to login` (client-side text, no `rpc error` prefix) | — | the server does not offer interactive login at all (very old or minimal server) | upgrade the server or enrol with a setup key |
| `validate access token failed with error: invalid JWT token audience field` (client-side text) | — | the token the identity provider issued does not carry the audience the login flow told the client to expect | identity-provider application configuration vs the server's flow settings (`04` §5.1) |
| `Connection already in progress...` (from the daemon, no `rpc error`) | — | `netzilo up` was called while the service was already connecting | wait, then `netzilo status`; if it stays there for minutes, restart the service |
| `failed handling request` | `Internal` | an untranslated server error | read `got an unhandled error: <reason>` in the management log at that second, then use this table on the inner reason |

Some reasons reach the client **only** in this last form. Whenever the desc is
`failed handling request`, or the code is `Internal`, the management log is the source
of truth (§6).

---

## 5. The management log

### 5.1 Where and how it is attributed

Self-hosted: the container logs to stdout — `docker compose logs --timestamps management`.
Bracketed context appears on request-bound lines: `context: GRPC` (peer RPCs, carries
`peerID` = WireGuard public key and `accountID`), `context: HTTP` (dashboard/API calls,
carries `requestID`, `accountID`, `userID`), `context: SYSTEM` (background jobs). Lines
without a bracket are background work and cannot be tied to a request.

Three reading rules:

- **Management runs at `info` by default.** A quiet server at `info` prints very little
  per peer; the per-peer explanations (`NOOP`, `FILTER_DIAG`, tenant resolution, JWT
  claim errors, §5.3) exist only at `debug`. If you do not see them, that is the level,
  not the absence of the event.
- **Match case-insensitively.** Error bodies returned to the API and repeated in the
  log are lowercased in places; grep with `-i` and never rely on capitalisation to tell
  two messages apart. Inside `[…]` the field order is not fixed (§2).
- **Debug output can contain secrets** (tokens, setup keys, e-mail addresses). Treat a
  debug capture as sensitive: review it and strip credentials before it leaves the
  customer's machine, and turn the level back to `info` when the reproduction is done.

### 5.2 Healthy start (observed order)

```
loading OIDC configuration from the provided IDP configuration endpoint https://<domain>/.well-known/openid-configuration
loaded OIDC configuration …
overriding HttpConfig.AuthIssuer / AuthKeysLocation / DeviceAuthorizationFlow.* / PKCEAuthorizationFlow.* / ClientAuthorizationFlow.* with a new value …   ← normal: endpoints taken from discovery
enabled application metrics and exposing on http://<addr>
using Redis store engine (cached)  |  using Postgres store engine  |  using SQLite store engine
using Postgres as persistent backend for Redis cache                 ← only with the Redis engine
GORM Config: …
Database connection pool configured: MaxOpen=N, MaxIdle=N, MaxLifetime=…, MaxIdleTime=…
starting cache warmup...
backfill graph correlations: normalising N graph run(s)
backfill graph correlations: run <uuid>: insert failed: … duplicate key value violates unique constraint …   ← WARN, benign on every restart
backfill event correlation_id: N rows updated / backfill graph correlations: done
could not initialize geo location service: …                         ← WARN; geo posture checks and /api/locations unavailable until fixed
Using Redis for sync cache / set account request buffer interval to Nms
single account mode disabled, accounts number N
Static TURN service configured with N STUN servers and N TURN servers  |  generating cloudflare turn server with url: …   ← which relay source is active
TrustedPeers are configured to default value '0.0.0.0/0', '::/0'. This allows connection IP spoofing.   ← WARN, expected on single-host installs
Using Redis for token revocation cache
cache warmup completed: N accounts in Nms
client session authentication enabled with audience: <client-id>
Sync rate limiter enabled: max_concurrent=N, max_jitter=Nms
running gRPC backward compatibility server: [::]:33073
management server version <version>
running HTTP server and gRPC server on the same port: [::]:<port>      ← serving
loaded N users for org <id> from IDP                                    ← identity provider reachable; repeats on every periodic sync
```

A start that ends before `running HTTP server and gRPC server` failed; the last line
names the reason (`03-server-troubleshooting.md` §2).

### 5.3 Steady-state families

Rows marked **debug** appear only with `--log-level debug` (§5.5).

| Line | Meaning |
|---|---|
| `NOOP: peer <key-prefix> (update meta only)` / `NOOP: peer <key-prefix>, serial N (unchanged)` — **debug** | a peer synced and nothing in its network map changed; the most common line on a quiet server at debug |
| `FILTER_DIAG: peer=<peer-id> account.Filters count=N` → `FILTER_DIAG:   [i] id=<filter-id> enabled=… groups=[…] OS=[…]` → `FILTER_DIAG:     group <group-id> name=<name> peers=[…] containsPeer=<true or false>` → `FILTER_DIAG: collectPeerFiltersFromAccount returned N filters for peer=…` — **debug** | the server explaining, per peer, which AI-security filters apply and why (group membership, OS). The direct answer to "why is the filter not applying" (`29` §5): find the peer's block and look for `containsPeer=true` |
| `found matching tenant with subdomain='…', orgID='…'` / `GetPKCEAuthorizationFlow: new client - hostname='<host>', extracted subdomain=''` / `using root domain organization ID: <id>` — **debug** | login-flow tenant resolution; on single-domain servers the subdomain is always empty |
| `hostname '<host>' doesn't match primary domain '<domain>', treating as no subdomain` — **debug** | a client used a different hostname than the dashboard domain; benign when the management and dashboard hostnames differ by design |
| `Token revoked by user <id>, expires at: …` (INFO) / `token has been revoked` and `Error when validating JWT claims: token has been revoked` — **debug** | a dashboard logout followed by a stale request from the same browser; benign |
| `ephemeral manager: deleting N expired ephemeral peer(s): […]` | ephemeral setup-key peers cleaned up |
| `generating cloudflare turn server with url: …` / `Static TURN service configured …` | relay credentials being issued; tells you which relay source peers receive |
| `loaded N users for org <id> from IDP` | periodic identity-provider sync |

### 5.4 WARN / ERRO families

| Line | Meaning |
|---|---|
| `failed logging in peer <key>: <reason>` (WARN, `peerID` set) | every refused login, with the reason from §4.8. By far the most common reason is `no peer auth method provided, please use a setup key or interactive SSO login`: a device presented a key the server does not know. At volume (hundreds per hour) it is background noise from stale or uninstalled clients. **The same key repeating** = one device that needs `netzilo up` with a setup key or SSO |
| `failed checkIFPeerNeedsLoginWithoutLock <key>: peer login has expired, please log in once more` (ERRO) | an SSO peer past its login expiration tried to reconnect. **Expected**, one per attempt per expired peer, until the user logs in again; not a fault, despite the level |
| `user mismatch when logging in peer <id>: peer user <a>, login user <b>` (WARN) | a different user than the peer's owner logged in on that device; the client receives `invalid user` or `can't login with this credentials` (§4.8) |
| `token signed with a key the IdP does not publish: …` (WARN) | a login token whose signing key is unknown at the configured key location; the client receives `invalid jwt token: … unable to find appropriate key` (§4.8). Points at the server's identity configuration, or at a token from another identity provider |
| `got an unhandled error: <reason>` (ERRO) | the reason behind a client-side `code = Internal desc = failed handling request` (§4.8); the only place the real text appears |
| `got a handler error: <message>` (ERRO for a `5xx` answer, **debug** for `4xx`) | the reason behind an API error response. At `info` you therefore see **only server-side failures**; refusals such as `401` `no valid authentication provided` / `token invalid`, `403` for an insufficient role, `404` for an unknown object or tenant, `409`/`412` validation refusals are **not logged** at that level — a customer's "the API returns an error" is not answered by the log unless debug is on. `412` with `Geo location database is not initialized` = geo database missing (see start-up WARN) |
| `JWT groups are enabled but no claim name is set` (ERRO) | Settings → Groups has JWT group sync on with an empty claim name; no groups are synced for anyone. Set the claim (`25` §4) or turn sync off |
| `failed sending SyncResponse rpc error: code = Unavailable desc = transport is closing` | the client disconnected while the server was pushing an update; benign |
| `failed to update sync cache for peer …: context canceled` / `failed to cache account in redis: context canceled` | request cancelled mid-flight (client went away); benign unless constant |
| `error when getting account <id> from the store: record not found` (ERRO), followed by an `account not found` answer | something referenced an account id that does not exist on this server (a token from another server, a stale integration, a deleted tenant) |
| `auto migrate: …` / `failed creating Store` / `failed retrieving a new idp manager` / `unsupported store type` at start | fatal start-up problems — `03` §2 |

Because API refusals are not logged at `info` and server failures are, a healthy server
under load can look "all errors" at a glance while a misbehaving dashboard produces no
lines at all. Judge by *which* messages appear, not by the count, and switch to `debug`
(§5.5) to see the `4xx` reasons.

### 5.5 What `debug` and `trace` add

`--log-level debug` (in the management `command:`; restart the container) adds
`Login request from peer [<key>] [<ip>]` and `Sync request from peer [<key>] [<ip>]`,
the `NOOP:` and `FILTER_DIAG:` families and the tenant-resolution lines of §5.3,
`got a handler error: …` for every `4xx` API answer, `Error when validating JWT claims:
…` for every rejected dashboard token, update-stream open/close per peer, initial-sync
sizing with the map serial, which token path (JWT vs personal token) authenticated a
request, and TURN credential refreshes per peer. Only `trace` adds the **per-request
REST access log** and store lock hold durations — use it for "who called what" and for
slow-sync/lock-contention questions. Debug output can carry tokens and keys: apply the
handling rule in §5.1 and return to `info` afterwards.

### 5.6 Signal server

Quiet by design. Start: `signal server version <v>`, `running without TLS` (TLS is
terminated in front of it), `running signal server: [::]:<port>`, `started Signal Service`.
Steady state produces two WARN lines: `peer [<key>] is already registered [new streamID N,
previous StreamID N]. Will override stream.` and `attempted to remove newer registered
stream of a peer … Ignoring.` — a peer reconnected before its old stream closed. In
bursts after network changes this is normal; **continuous** for one peer means that
device reconnects without pause (a restart loop or a flapping network — read its client
log), or two devices run with a copy of the same configuration and take turns. This is a
different fault from the client's `wrongly addressed message` (§4.5), which is about
network-map disagreement, although a flapping peer can produce both.

---

## 6. Correlating client and server

| Key | Client | Server | Notes |
|---|---|---|---|
| **WireGuard public key** | full in `netzilo status -d` / `status.txt`; **prefix-truncated** in log lines | `peerID` bracket field on every peer RPC line; full in `Login/Sync request from peer [<key>]` at debug | the primary join. Survives anonymisation |
| Overlay IP / FQDN | `connection established … [<overlay-ip>]`, `loginToManagement DNS <fqdn>` | peer record via API | survive anonymisation |
| `requestID` | — | groups all lines of one request | server-only; never reaches the client |
| `accountID` | — | bracket field | get it from the server or API, then join on the key |
| Timestamps | local + offset | usually `Z` | convert to UTC; dashboard event times trail the client log by up to ~30 s because events are batched |
| AIDR `correlation_id`, `run_id`, `rule_name`, `filter_name` | `Buffered event: {…}` at debug; `MCP event:` lines | dashboard event metadata; snapshot API | joins a dashboard row to the client line that produced it |

Procedure: take the affected device's public key from `netzilo status -d`; on the
server `grep '<first-20-chars>' mgmt.log`; convert the client's failing timestamp to UTC
and read the server lines within ±1 minute; on the client grep the key prefix and the
overlay IP around the same UTC time.

---

## 7. Worked readings (from real logs, identifiers replaced)

**A. "The VPN keeps dropping" on a laptop.** Template profile: 18× `Network monitor:
default route changed`, 18× `detected network change, restarting engine`, 37× `stopped
Netzilo Engine`, and each cycle ends in both `READY` lines within two seconds. Reading:
the device changes networks often (Wi-Fi/dock/sleep); the client restarts cleanly every
time. Not a fault — the user is seeing the reconnect. Only escalate if a cycle fails to
reach `READY`.

**B. `Failed to resolve host <management-domain>` followed by `no such host` for the
dashboard domain too.** Both names failing at the same second, followed by `default route
changed`, then a restart cycle ending in `READY`: the host lost DNS during a network
transition. Benign. If it persisted with a stable network it would be the device's
resolver.

**C. `wrongly addressed message <key>` every ~42 seconds for hours,** with the signal
server showing `peer [<key>] is already registered … Will override stream` for the same
key over the same period. Reading: the key is the *sender*. That device reconnects to
signal without pause and, on every reconnect, offers a connection to this device — which
does not have it in its own network map, so the offer is refused. Two things to check,
in this order: the sender's client log for why it restarts (network flapping, a crash
loop, or two machines running a copied configuration and taking turns), and the two
devices' policies and posture checks for why only one side lists the other (`20` §6). A
re-login on the receiving device changes nothing.

**D. "I cannot reach host X" and the log shows `Posture check 'Enterprise Browser'
FAILED`, `Posture check 'Enforce Workspace' FAILED`, `Policy evaluation complete: 1
connectable peers found`.** Reading: the device fails two posture checks attached to the
policies that would have allowed X; only one peer remains connectable. Not connectivity
— policy design (`21` §5, `20` §6).

**E. `WSS ListenAndServeTLS() failed: … bind: address already in use` at boot, ten times
across restarts.** Reading: something else owns 41337 whenever the daemon starts —
typically a leftover daemon or a developer tool. The tunnel works; the browser extension
channel does not. Find the holder (`lsof -i :41337`).

**F. Management log: 500+ `failed logging in peer … no peer auth method provided` per
12 h, spread across many keys.** Reading: stale clients (uninstalled without logout,
deleted peers still running) knocking. Noise. If one key dominates, that device needs
re-enrolment; nothing to do server-side.

---

## 8. When the log does not explain it

If the sequence stops in an unexpected place, or the same failing line repeats with no
cause in either log, raise verbosity (§4.7, §5.5), reproduce within one daemon lifetime,
and collect per `12-escalation-package.md`. State in the summary which template you
consider the first anomaly, with its UTC time and the peer key prefix.
