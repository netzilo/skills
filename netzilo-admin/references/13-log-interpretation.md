---
id: '13'
title: Reading Netzilo Logs — Client and Management
requires:
- server-shell
- client-device
executable_on:
- netzilo-harness
- human-operator
chars: 32193
sections:
- id: '1'
  title: Method
  chars: 646
- id: '2'
  title: Line anatomy (same on client and management)
  chars: 1658
- id: '3'
  title: Profile a log in one minute
  chars: 1697
- id: '4'
  title: The client log
  chars: 15452
- id: '5'
  title: The management log
  chars: 7589
- id: '6'
  title: Correlating client and server
  chars: 1342
- id: '7'
  title: Worked readings (from real logs, identifiers replaced)
  chars: 2239
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
   states are recognisable sequences (§4.3, §5.2); the first deviation is the lead.
3. **Separate noise from signal.** Several loud `WARN`/`ERRO` families are benign or
   cosmetic (§4.6, §5.4). Ruling them out first prevents chasing the wrong line.
4. **Then correlate** across client and server on the WireGuard public key and on
   timestamps converted to UTC (§6).

---

## 2. Line anatomy (same on client and management)

```
2026-09-12T07:42:51-04:00 INFO <source>: gRPC Management connection established - State: READY
2026-09-12T06:37:52Z INFO [context: GRPC, requestID: <uuid>, accountID: <account-id>] <source>: NOOP: peer <key-prefix> (update meta only)
```

| Field | Meaning | Pitfalls |
|---|---|---|
| Timestamp | RFC 3339 in the **host's local time with its UTC offset**. Containers usually run in UTC and print `Z`. | The offset can **change within one file** when a laptop moves time zones (observed: `+03:00` then `-04:00`). Convert everything to UTC before comparing client and server. Event payloads shown in the dashboard are UTC. |
| Level | `PANC` `FATL` `ERRO` `WARN` `INFO` `DEBG` `TRAC` | `ERRO` is not always an incident (§4.6). |
| `[key: value, …]` | present on management lines that belong to a request: `context` (`GRPC`, `HTTP`, `SYSTEM`), `requestID`, `accountID`, `peerID` (= the peer's WireGuard public key), `userID`. Some client lines carry `[upstream: …, error: …]` or `[key: …]`. | Not every line has it; lines without a bracket cannot be attributed to a request. `requestID` exists only server-side. |
| `<source>` | a source-location field the software prints on every line | useful only for the vendor; ignore it when reading |
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
Database path: … mcp.db  /  Mode: development
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
Starting WSS server on localhost:41337
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
removing search domains from system / removing match domains from system
Routing cleanup complete
stopped Netbird Engine
exiting the Signal service connection retry loop due to the unrecoverable error: context canceled
exiting the Management service connection retry loop due to the unrecoverable error: context canceled
failed while getting Management Service public key: rpc error: code = Canceled desc = context canceled
Stopping previous engine before creating new one
Routing setup complete → DNS loopback listener started → … → gRPC … READY → peer … connection established
```

The `context canceled` errors are the old engine being torn down while the new one
starts. They are a problem only if the sequence **does not** end in `READY` lines.

Two macOS-only lines appear in bursts around route changes and are cosmetic:
`Network monitor: error parsing routing message: parse RIB: invalid address` and
`Network monitor: read from routing socket returned less than expected: N bytes`.

### 4.5 Message families and what they mean

**Management connection**

| Line | Meaning |
|---|---|
| `Failed to resolve host <domain>: lookup <domain>: no such host` | the host has no working DNS at that moment (usually mid network change). Persistent → the device's resolver or the domain is wrong |
| `failed while getting Management Service public key: rpc error: code = Unavailable desc = …` | TCP/TLS to the management endpoint failed (connection reset, read error) |
| `… code = DeadlineExceeded desc = context deadline exceeded` | timed out — firewall, proxy, or the server not answering |
| `… code = Canceled …` / `exiting the Management service connection retry loop due to the unrecoverable error: context canceled` | teardown during restart; benign unless nothing reconnects |
| `failed to login to Management Service: rpc error: code = PermissionDenied desc = no peer auth method provided, please use a setup key or interactive SSO login` | the device's key is not registered (deleted peer, reset config, or first run). Follows on `netzilo up` right before SSO/registration; persistent → re-enrol |
| `disconnected from the Management service but will retry silently. Reason: EOF` | server closed the stream (restart, deploy); the client reconnects on its own |
| `could not sync meta with reply: …` / `Error pushing events: …` | side effects of the management connection being down; not separate faults |
| `connected to the Management Service stream` → `gRPC Management connection established - State: READY` | healthy |

**Signal**

| Line | Meaning |
|---|---|
| `connected to the Signal Service stream` → `gRPC Signal connection established - State: READY` | healthy |
| `disconnected from the Signal Exchange due to an error: didn't receive a registration header from the Signal server whille connecting …` | the stream opened but registration did not complete — typically the network dropped mid-handshake |
| `error while handling message of Peer [key: <key>] error: [wrongly addressed message <key>]` | a signal message arrived for a key this daemon does not hold. Occasional: harmless. **Repeating every ~40 s for the same key**: another device (or an old instance of this one) is registered under a key the server still associates with this peer. Correlate with the signal server's `peer [<key>] is already registered … Will override stream` (§5.6). Re-login the affected device |
| `🔄 Auto-sync triggered for unknown peer <8-char prefix>` → `✅ Auto-sync completed for unknown peer …` | a message came from a peer not in the local network map; the client pulled a fresh map. Normal when peers are added; a tight loop means the map never includes that peer (policy/group) |

**Peer connections**

| Line | Meaning |
|---|---|
| `peer <key> ICE connection state changed to Connected - ICE layer established` | a path was found |
| `peer <key> WireGuard peer configured: endpoint=…, allowedIPs=…, type=host->host` | tunnel endpoint set; `type` shows candidate pairing |
| `peer <key> connection established successfully [<overlay-ip>]: direct=…, relayed=…, ice=…` | the verdict line (§4.3) |
| `failed to establish connection to peer <key>: disconnected from peer <key>` | ICE gave up or the far side went away; recurring for one peer → that peer is offline or both sides lack a usable path (`11` §2) |
| `Connection has been already closed or attempted closing not started connection <key>` | cleanup of a connection that never completed; benign on its own |
| `Building network map: N policies, N groups, N peers` / `Policy evaluation complete: N connectable peers found` | how many peers this device is *allowed* to talk to after policies and posture. `0 connectable peers` with peers present = policy or posture blocks everything |
| `Posture check '<name>' FAILED at NetziloChecks` and `❌ Posture check '<name>' (ID=…) FAILED` | this device fails that check; the policies/filters using it are excluded for this device. Logged at `ERRO` although it is a policy outcome, not a fault |

**DNS**

| Line | Meaning |
|---|---|
| `DNS loopback listener started on 127.0.0.1:53` / `dns service listening on: <addr>` | local resolver up |
| `Upstream nameserver <ip> with type udp` | distributed nameserver groups received |
| `got an error while connecting to upstream` with `read udp …: i/o timeout` | the upstream did not answer through the tunnel — route/policy to the resolver, or resolver down |
| `got other error while querying the upstream` with `network is unreachable` / `destination address required` / `socket is not connected` / `operation was canceled` | no network at that moment (transition) — benign in bursts around network changes |
| `Temporarily deactivating nameservers group due to timeout` → `Upstream resolving is Disabled for Ns` | the client stopped using a failing group for a while; names in its match domains will not resolve until it retries |
| `not applying the dns configuration update as there is nothing new` | benign |
| `Unable to get system DNS configuration` / `unable to update record of System's DNS config: couldn't get current DNS config: couldn't find the primary service key` | macOS resolver state not readable during transition; persistent → `07` §6 |

**AI security (MITM, gateway, scanners)**

| Line | Meaning |
|---|---|
| `MITM: loaded CA from …` / `MITM: TLS interception enabled` / `MITM engine ready` / `MITM: proxy initialized successfully` / `unified proxy starting on 127.0.0.1:41339` | interception stack up |
| `WASM [parser]: updated to <version>` / `WASM [semantic-classifier]: updated to <version>` | parser bundles refreshed from the download server |
| `Gateway IPC: updating static rules (version: mgmt-sync-N, N rules, N filter profiles)` → `[scanner] Rules updated: N loaded, N failed …` → `✓ Successfully updated MCP Gateway filters: N filters applied` | rules and filters delivered from management. `0 filters applied` = no filter matches this device (`29` §5). `N failed` > 0 = a rule did not parse |
| `MCP event: type=llm.request server=<host> tool=llm_request status=success action= duration_ms=N` (and `llm.response`) | an intercepted LLM call; `action=` empty = allowed |
| `MCP event: type=security.staticscanner.detect … action=redact` / `action=detect` / `action=block` | a rule fired; `detect` = report-only |
| `[scanner] Scan [tool_output] blocked=false triggered=N loaded=N version=mgmt-sync-N time=N.Nms` | one evaluation; `blocked=true` would be a block |
| `MITM BYPASS pipe closed: client=… upstream=<ip:port> client→upstream=N bytes upstream→client=N bytes duration=…` | a flow that was passed through without inspection (excluded domain, non-HTTP, or not an intercepted app) — informational |
| `[aidr] ingest queue full, dropping event` | back-pressure in the behaviour-graph ingester; events are being lost. Bursts of thousands during heavy AI traffic. Cosmetic for connectivity; matters if session snapshots look incomplete |
| `enrichment slots saturated (N), skipping URL enrichment for <url>` | metadata enrichment skipped under load; cosmetic |
| `SecurityFilter: connected to extension at <addr>` / `SecurityFilter: disconnected, retrying in 3s` / `MacFilter: extension IPC disconnected, retrying in 3s` | macOS system-extension link; reconnects on its own. Never connecting → extension not approved (`07` §9) |
| `WSS ListenAndServeTLS() failed: listen tcp 127.0.0.1:41337: bind: address already in use` | another process (or a second daemon) holds the local TLS port; the browser-extension channel is down |

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

---

## 5. The management log

### 5.1 Where and how it is attributed

Self-hosted: the container logs to stdout — `docker compose logs --timestamps management`.
Bracketed context appears on request-bound lines: `context: GRPC` (peer RPCs, carries
`peerID` = WireGuard public key and `accountID`), `context: HTTP` (dashboard/API calls,
carries `requestID`, `accountID`, `userID`), `context: SYSTEM` (background jobs). Lines
without a bracket are background work and cannot be tied to a request.

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
loaded N users for account <account-id> from IDP                        ← one per account, identity provider reachable
```

A start that ends before `running HTTP server and gRPC server` failed; the last line
names the reason (`03-server-troubleshooting.md` §2).

### 5.3 Steady-state families

| Line | Meaning |
|---|---|
| `NOOP: peer <key-prefix> (update meta only)` | a peer synced and nothing in its network map changed; the most common line on a quiet server |
| `Peer has no userID` | a setup-key-enrolled peer (no owner) touched a code path that looks for a user; informational |
| `FILTER_DIAG: peer=<peer-id> account.Filters count=N` → `FILTER_DIAG: [i] id=<filter-id> enabled=… groups=[…] OS=[…]` → `FILTER_DIAG:     group <group-id> name=<name> peers=[…] containsPeer=true|false` → `collectPeerFiltersFromAccount returned N filters for peer=…` | the server explaining, per peer, which AI-security filters apply and why (group membership, OS). The direct answer to "why is the filter not applying" (`29` §5): find the peer's block and look for `containsPeer=true` |
| `found matching tenant with subdomain=''` / `GetPKCEAuthorizationFlow: new client - hostname='<host>', extracted subdomain=''` / `using root domain organization ID:` | login-flow tenant resolution; on single-domain servers the subdomain is always empty |
| `hostname '<host>' doesn't match primary domain '<domain>', treating as no subdomain` (WARN) | a client used a different hostname than the dashboard domain; benign when the management and dashboard hostnames differ by design |
| `Token revoked by user <id>, expires at: …` / `token has been revoked` / `Error when validating JWT claims: token has been revoked` | a dashboard logout followed by a stale request from the same browser; benign |
| `ephemeral manager: deleting N expired ephemeral peer(s)` | ephemeral setup-key peers cleaned up |
| `generating cloudflare turn server with url: …` / `Static TURN service configured …` | relay credentials being issued; tells you which relay source peers receive |
| `loaded N users for org … from IDP` | periodic identity-provider sync |

### 5.4 WARN / ERRO families

| Line | Meaning |
|---|---|
| `failed logging in peer <key>: no peer auth method provided, please use a setup key or interactive SSO login` (WARN, `peerID` set) | a device presented a key the server does not know. At volume (hundreds per hour) it is background noise from stale or uninstalled clients. **The same key repeating** = one device that needs `netzilo up` with a setup key or SSO |
| `HTTP response <uuid>: <METHOD> <path> status <code>` (ERRO) | only non-success API responses are logged. `401` = missing/invalid token (also `got a handler error: no valid authentication provided` / `token invalid`); `403` = insufficient role; `404` = unknown object or tenant; `412` with `got a handler error: Geo location database is not initialized` = geo database missing (see start-up WARN) |
| `got a handler error: <message>` | the reason for the `HTTP response` line with the same `requestID` |
| `failed sending SyncResponse rpc error: code = Unavailable desc = transport is closing` | the client disconnected while the server was pushing an update; benign |
| `failed to update sync cache for peer …: context canceled` / `failed to cache account in redis: context canceled` | request cancelled mid-flight (client went away); benign unless constant |
| `error when getting account <id> from the store: record not found` / `got a handler error: account not found` | a token or webhook referencing an account that does not exist here |
| `auto migrate: …` / `failed creating Store` / `failed retrieving a new idp manager` / `unsupported store type` at start | fatal start-up problems — `03` §2 |

Because only failures are logged for the REST API, a healthy server can look "all
errors" at a glance. Judge by *which* endpoints and codes, not by the count.

### 5.5 What `debug` and `trace` add

`--log-level debug` (in the management `command:`; restart the container) adds
`Login request from peer [<key>] [<ip>]` and `Sync request from peer [<key>] [<ip>]`,
update-stream open/close per peer, initial-sync sizing with the map serial, which token
path (JWT vs personal token) authenticated a request, and TURN credential refreshes per
peer. Only `trace` adds the **per-request REST access log** and store lock hold
durations — use it for "who called what" and for slow-sync/lock-contention questions.

### 5.6 Signal server

Quiet by design. Start: `signal server version <v>`, `running without TLS` (TLS is
terminated in front of it), `running signal server: [::]:<port>`, `started Signal Service`.
Steady state produces two WARN lines: `peer [<key>] is already registered [new streamID N,
previous StreamID N]. Will override stream.` and `attempted to remove newer registered
stream of a peer … Ignoring.` — a peer reconnected before its old stream closed. In
bursts after network changes this is normal; **continuous** for one peer means two
devices share a key or one device flaps, and it pairs with the client's `wrongly
addressed message` (§4.5).

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
Netbird Engine`, and each cycle ends in both `READY` lines within two seconds. Reading:
the device changes networks often (Wi-Fi/dock/sleep); the client restarts cleanly every
time. Not a fault — the user is seeing the reconnect. Only escalate if a cycle fails to
reach `READY`.

**B. `Failed to resolve host <management-domain>` followed by `no such host` for the
dashboard domain too.** Both names failing at the same second, followed by `default route
changed`, then a restart cycle ending in `READY`: the host lost DNS during a network
transition. Benign. If it persisted with a stable network it would be the device's
resolver.

**C. `wrongly addressed message <key>` every ~42 seconds for hours,** with the signal
server showing `peer [<key>] is already registered … Will override stream` for the same period.
Reading: two registrations fight over one identity — a second device using a copied
config, or a stale instance. Fix on the device that should not own the key (`netzilo
down`, re-enrol).

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
