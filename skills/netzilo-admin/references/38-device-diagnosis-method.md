---
id: '38'
title: Netzilo — Root-Cause Method for Device Problems (with the OS matrix)
requires:
- api
- device-tools
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 31596
sections:
- id: '1'
  title: Facts you take as given
  chars: 4780
- id: '2'
  title: The loop
  chars: 2525
- id: '3'
  title: The OS matrix
  chars: 4056
- id: '4'
  title: Decision trees
  chars: 18576
- id: '5'
  title: What the device cannot tell you
  chars: 535
- id: '6'
  title: Reporting
  chars: 474
---
# Netzilo — Root-Cause Method for Device Problems (with the OS matrix)

Device tools make it cheap to look, and cheap looking produces sloppy diagnosis: a
tool is called, a number is read, a conclusion is drawn that the number does not
support. This file is the discipline. It gives the fixed facts you must not rediscover,
the order in which a device problem is narrowed, the decision trees for the symptoms an
operator actually reports, and the per-platform differences that change the next step.
Tool contracts are in `references/37-device-tool-reference.md`; the consent rule and
the mechanics of calling are in `references/36-device-tools.md`.

## 1. Facts you take as given

These are how the product works. Do not spend a tool call establishing them, and do not
let a single odd result talk you out of them; if a result contradicts one, suspect the
reading before the fact.

- **Policy and posture are computed on the device.** A current client receives from
  management the policies, groups, peers, routes and posture checks that concern it, and
  decides on the device which peers it may connect to and which routes it may use. The
  account (`references/20-policies-access-control.md`) says what policy *should* allow;
  the device's log says what it *computed*. Every sync writes
  `Building network map: N policies, N groups, N peers` and
  `Policy evaluation complete: N connectable peers found`; at debug level the full input
  and the list of connectable peers follow.
- **The initiating side enforces; the receiving side accepts.** A device that is a
  *destination* of a rule lists the rule's sources without checking their posture; a
  device that is a *source* lists the destinations only if its own posture checks pass.
  So the two ends of one rule can disagree about whether they belong together.
- **A posture failure makes things disappear; nothing says "denied".** When the source
  device fails a check, the peers and routes that policy would give it are simply absent:
  not in `diag.status` peers, not in `diag.routes`, and `diag.route_match` says no route
  covers the target. That is not an account fault by itself. The log names it:
  `❌ Posture check '<name>' (ID=<id>) FAILED`, and
  `Posture check '<name>' FAILED at <NBVersionCheck | OSVersionCheck | GeoLocationCheck |
  NetworkRangeCheck | NetziloChecks | DateTimeCheck>`. `diag.posture` shows the probe
  behind it; `references/21-posture-checks.md` shows what the account enforces.
- **A peer sees only what policy gives it.** `peers: []` with management Connected means
  no policy joins this device to anything it can currently satisfy (policy, or its own
  posture). A remote whose login has expired is not listed once the account has marked it
  expired.
- **One-sided maps leave a signature.** When a peer has this device in its map but this
  device does not have that peer, the peer keeps sending connection offers and this
  device logs `error while handling message of Peer [key: <key>] error: [wrongly
  addressed message <key>]` followed by `Auto-sync triggered for unknown peer <first 8
  characters of the key>`. The key is the **sender's**. Repeating every 30–45 s for the
  same key means the two sides see policy differently (typically: this device is the
  source and fails a posture check; the other is the destination and accepts).
- **`peer.access.blocked` is not proof either way.** The account records it only when a
  source is blocked by posture *and* a destination peer is connected at that moment. Its
  absence proves nothing; the device log line above is the evidence.
- **Routes exist twice.** Once in the account, once as *selected* on the device.
  `diag.route_match` reports both; an unselected route carries nothing. *Selected* is
  only the person's choice: a selected route with no connected routing peer is removed
  from the OS (§4.2).
- **Peer addresses are not routes.** Traffic to another peer's Netzilo IP goes through
  the tunnel without any route; `diag.route_match` reports `matched: false` for it. A miss
  there says nothing about direct peer traffic.
- **DNS is two resolvers.** The client's own resolver on the device (peer names, custom
  zones, and forwarding to the nameserver groups), and the host's resolver, which the
  client installs itself into. `diag.dns` compares the nameserver group's upstream with
  the host; `diag.probe` in `dns` mode tests only the host's.
- **Peer-connection log lines are keyed by WireGuard public key**, not by IP or name.
  Take the peer's `pubKey` from `diag.status {full: true}` and grep a prefix of it.
- **Device tools ride the device's live management connection.** The client starts its
  engine only once it has management and signal, so a device whose management or signal
  is down, or whose login has expired, shows *offline* and cannot be diagnosed with device
  tools. Every tree below says what to use instead.
- **The client log is the record.** Anything the device did, tried, or failed at in the
  last hours is in `client.log`, and `diag.grep` searches it on the device. If you find
  yourself guessing what happened, you have not searched yet. WireGuard's own logging is
  off by default: there are no handshake lines to find, only the client's.
- **Management refusing to dispatch is not a device finding.** A line beginning
  `the command did not run:` means the device never saw the request
  (`references/36-device-tools.md` §9).

## 2. The loop

Every device problem is narrowed the same way. Write the ledger as you go; it is what
you report at the end and what stops you from repeating a read.

1. **State the symptom in the person's words**, and translate it into which of the trees
   in §4 it is. "VPN is broken" is not a symptom; "I can ping the server but cannot open
   the app" is.
2. **Read the account first**, from the API: is the peer `connected`, when was it
   `last_seen`, is its login expired (`login_expired`), which groups is it in, what policy
   and routes should it have. Two minutes here prevents twenty on the device. If the peer
   is not connected, device tools will not reach it; go to §4.1 step 0.
3. **Fix the platform.** Read the `device_tools` line: macOS (shown as Darwin), Linux,
   or Windows. Every branch below has a platform column; pick it now.
4. **One hypothesis, one tool.** Name what you expect the result to show if the
   hypothesis is right, then call. A result that neither confirms nor refutes means the
   hypothesis was too vague.
5. **Record the evidence** as `tool → what it showed → what that rules in or out`. Quote
   the `verdict` field where a tool gives one.
6. **Stop when the cause is established**, not when the tools run out. The stop
   condition for each tree is written into it.
7. **Confirm the fix the same way you found the fault.** If the fault showed in
   `diag.dns`, the fix shows in `diag.dns`.

Label every ledger entry with what it is, and name what backs it:

| Label | Means | Needs |
|---|---|---|
| **observation** | what a tool or the person reported, verbatim | the tool and its output |
| **hypothesis** | what would explain the observation | the reading that would refute it |
| **confirmed cause** | the hypothesis survived a test that could have refuted it | two independent signals, or one signal plus a change that removed the fault |
| **verified recovery** | the symptom is gone | the same read that showed the fault, now showing it absent |

Habits that separate a diagnosis from a fishing trip: never change anything before
the read-only path is exhausted, and never conclude from one signal what needs two. "It
is relayed" is an observation; "it is slow because it is relayed" needs the latency too.
Two log lines with the same timestamp are a hypothesis, not a cause. When tools cannot
reach the device, the same trees apply with the person's own `netzilo status -d` output,
the API, and a local shell where the surface has one; label that evidence as reported.

## 3. The OS matrix

The client is one code base, but the places it touches differ. When a tree says "check
X on the device", this is what X is on each platform. Windows-specific behaviour in more
depth: `references/40-windows-hosts.md`.

| | macOS | Linux | Windows |
|---|---|---|---|
| reported as | `Darwin <version>` | distribution name | `Windows <edition>` |
| daemon identity | `root` via launchd (`Netzilo`) | `root` via systemd (`netzilo`) | `SYSTEM` service (`Netzilo`) |
| installed in | — | — | `%ProgramData%\Netzilo Client\` |
| config | `/etc/netzilo/config.json` | same | `%ProgramData%\Netzilo\config.json`; non-admin mode `%ProgramData%\netzilo\usservice<N>.json` |
| log | `/var/log/netzilo/client.log` | same | `%ProgramData%\Netzilo\client.log` (and `service.log` for service crashes), **same folder as config**; non-admin mode `%ProgramData%\netzilo\usservice<N>.log` |
| tunnel interface | `utun100` | `wt0` | `wt0` adapter |
| host DNS installed via | system configuration (`scutil --dns`) | chosen at start from `/etc/resolv.conf` (see below); log `System DNS manager discovered: <x>` | primary resolver on the `wt0` adapter; match domains as NRPT rules under `HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\DnsPolicyConfig\Netzilo-Match` |
| match domains (split DNS) | yes | systemd-resolved and NetworkManager: yes; resolvconf and direct file: no | yes, unless a GPO-pushed NRPT policy overrides local rules (`Get-DnsClientNrptPolicy`) |
| custom DNS port | yes | systemd-resolved only | no; UDP 53 must be free for the local resolver |
| routes programmed via | `route` | netlink: routes in table 7120 (`netzilo`); rule 100 `lookup main suppress_prefixlength 0`, rule 110 `not fwmark 0x1bd00 lookup netzilo` | `route` (System32) |
| a local route for the same destination | an identical prefix is skipped (`Skipping adding a new route for network … because it already exists`); a more specific local route wins by longest match | any main-table route covering the target, other than the default route, wins (rule 100), however broad | as macOS |
| check the chosen path | `route -n get <ip>` | `ip route get <ip>`; `ip rule`; `ip route show table 7120` | `Find-NetRoute -RemoteIPAddress <ip>` |
| reconnect on network change | network monitor on by default | no monitor by default; each peer recovers when ICE fails and reconnects (tens of seconds) | network monitor on by default |
| `shell.run as:user` | drop to console user | drop to console user | duplicate session token; needs SYSTEM |
| shell for pipelines | `sh -c` | `sh -c` | `powershell -NoProfile -NonInteractive -Command` |
| posture signal caveats | `references/21-posture-checks.md` | screen lock only GNOME/KDE; AV only ClamAV; OS-updated only apt; `references/21-posture-checks.md` | real caveats per signal: `references/21-posture-checks.md` and `references/40-windows-hosts.md` |
| what a hand-started `-F` client changes | runs as the user; no log file unless `--log-file`; disconnect exits the process | same | same |

**Linux DNS manager.** The client reads `/etc/resolv.conf` at start. Header comments
identify the owner: a file owned by NetworkManager is handed to NetworkManager only when
it runs in a supported mode; systemd-resolved is used only when `resolv.conf` points at
its `127.0.0.53` stub; a `resolvconf` header uses resolvconf; anything else, or no header,
is edited directly (logged as `file`, or `netzilo` once the client has written it). In
resolvconf or file mode without a primary nameserver group (one with no match domains)
the client logs `unable to configure DNS for this peer using file manager without a
nameserver group with all domains configured` (or `… using resolvconf manager …`), and
even peer names stop resolving.

Two Windows facts change how you search: the log directory also holds `config.json` and
`token.dat`, so `diag.grep` with `all_files` scans them (named secrets are redacted, but
prefer the default log), and the service has no user `PATH`, so shell commands need
absolute paths or PowerShell.

## 4. Decision trees

Each tree starts after §2 steps 1–3. `→` is the next read; **stop** is where the cause
is established and further reads add nothing.

### 4.1 "Not connected" / "the client shows disconnected"

0. **Tools cannot reach the device** (`device_tools` says offline, or the API peer has
   `connected: false`). This is the normal state for this symptom; use other evidence.
   - `login_expired: true` in the API: **confirmed cause** when the person's client shows
     `NeedsLogin` or the log has `peer login has expired, please log in once more`. The
     client stops retrying in that state. Recovery: the person runs `netzilo up` or
     presses Connect in the app and signs in (`references/07-client-troubleshooting.md`
     §2). **Verified** when the API shows `connected: true`, `login_expired: false`.
   - not expired: ask the person for `netzilo status -d` output (or run it through a
     local shell if the surface has one). Read `Management:`, `Signal:`, `Relays:` and
     `Daemon status:`.
     - Management Disconnected: the path from that machine to the management URL on 443.
       A TLS-inspecting proxy shows as an `x509: certificate signed by unknown authority`
       error; a network that breaks gRPC over HTTP/2 is worked around automatically
       (`grpc: connected to … via WebSocket fallback` in the log is a success, not a
       fault). `references/07-client-troubleshooting.md` §4 and §9. **stop** at the first
       failing hop.
     - Management Connected, Signal Disconnected: signal is also on 443; same checks for
       the signal address (`references/03-server-troubleshooting.md` §4a). **stop**.
     - `last_seen` a few seconds old: the device may be mid-reconnect; read the API again
       in a minute before concluding.
1. Tools reach the device: `diag.status {full: true}` → `status` and `fullStatus.managementState`.
   - management Connected, signal **Disconnected** (dropped after the engine started):
     peers cannot negotiate. → `diag.grep {pattern: "signal", ignore_case: true}`. Signal
     is a server or firewall matter (`references/03-server-troubleshooting.md` §4a,
     `references/07-client-troubleshooting.md` §4). **stop**.
   - `managementUrl` in `diag.config` is not the customer's server: **stop**, that is the
     cause.
2. Both connected and the person still says "disconnected": they mean a peer. Go to 4.2
   or 4.9.

### 4.2 "Connected but I cannot reach host X"

1. Classify X: address or name. Name → 4.3 first, then return here with the address.
   X is another peer (its Netzilo IP or `<name>.netzilo.network`): skip to 3; peer
   traffic needs no route.
2. `diag.route_match {target: X}`.
   - `matched: false`: no route on this device covers X. That is an **observation**, not
     an account finding: the route may not exist, the device may not be in its
     distribution groups, or the route may have been withheld because its routing peer is
     not connectable by policy or by this device's posture (§1). → `diag.grep {pattern:
     "Posture check .* FAILED|Policy evaluation complete", max_matches: 10}`, then the
     account (`references/22-network-routes-and-exit-nodes.md`). **stop** at whichever of
     the three is shown.
   - matched, `best.selected: false`: **stop**, the route is not enabled on this device;
     enabling it is a client setting (`netzilo routes select <id>`), not a device tool.
   - matched and selected: *selected* is only the person's choice. → `diag.status {full:
     true}` and read `peers[].routes` to see which peer carries X's network now. No peer
     lists it: → `diag.grep {pattern: "has not been assigned a routing peer|New chosen
     route is", max_matches: 10}`. `The network [<id>] has not been assigned a routing
     peer as no peers from the list [...] are currently connected` is the **confirmed
     cause** when the list's keys match the routing peers in the account: the route has
     been removed from the OS and traffic to X falls back to the device's own default
     route (for an exit node, the person quietly uses their local internet). Go to 4 with
     the routing peer. A peer lists it: continue at 3.
   - Other route lines to know: `Prefix [<cidr>] is already routed by peer [<key>]. HA
     routing disabled` (two networks overlap); `Failed to resolve domains for route
     [<id>]: …` (a domain route resolves through the host resolver about every minute and
     that failed); `doesn't support default routes … skipping this prefix` (the client
     does not program default routes in its current mode: an older client, or custom
     routing disabled in its service environment).
3. Local route conflict. → `shell.run` with the platform command from §3 (`ip route get
   <X-ip>`, `route -n get <X-ip>`, `Find-NetRoute -RemoteIPAddress <X-ip>`). The answer
   must name the tunnel interface. If it names the LAN or Wi-Fi interface, a local route
   wins: on Linux any main-table route covering X except the default route; on macOS and
   Windows an identical prefix, logged as `Skipping adding a new route for network …
   because it already exists`. The typical case is a home LAN numbered like the office
   route. **stop**; fix by renumbering or publishing a narrower range
   (`references/22-network-routes-and-exit-nodes.md` §4.6).
4. `diag.status {full: true}` → find the peer or routing peer in `peers[]`; note its
   `pubKey`.
   - absent: this device's map does not include it: policy, this device's posture (§1),
     or the remote's expired login. Account: policy between the groups
     (`references/20-policies-access-control.md` §6, `references/11-connectivity-diagnosis.md` §3);
     device: → `diag.grep {pattern: "Posture check .* FAILED", max_matches: 10}`. **stop**.
   - present, `connStatus` not Connected: → 4.9.
   - Connected, `relayed: true`: reachable but via relay; if the complaint is "slow",
     go to 4.4.
   - Connected and direct: → `diag.probe {mode: tcp, target: "X:port"}` from the device.
     Refused or timeout with the tunnel healthy (handshake under ~3 min, bytes received
     growing): the service on X, or a firewall on X or on the routing peer
     (`references/11-connectivity-diagnosis.md` §5). For HTTP, `diag.probe {mode: http}`
     returning any `status_code` (a 401 or 404 comes back with `ok: false`) means the
     server answered and the path works; only an `error` with no status code is a
     reachability failure. **stop**.
   - Connected, but nothing passes in either direction and `bytesRx` does not grow: check
     Rosenpass. `netzilo status -d` showing `Quantum resistance: false (connection won't
     work without a permissive mode)`, or `remote peer with public key … does not support
     rosenpass` in the log, is the **confirmed cause**: one side runs Rosenpass in strict
     mode and the other does not run it. Fix: permissive mode on the strict side, or
     enable Rosenpass on both.

Without tools: ask for `netzilo status -d` and `netzilo routes list` from the device,
and the platform route command from §3.

### 4.3 "Names do not resolve" / "works in the browser, not in the app"

1. **Peer names and custom zones** (`<peer>.netzilo.network` and other names the account
   defines) are answered by the client's local resolver on the device, not by any
   upstream. `diag.dns` without `server` sends the query to the nameserver group's
   upstream, which does not know them, and so falsely suggests the tunnel's DNS is broken.
   → `diag.grep {pattern: "DNS loopback listener started on", max_matches: 1}` and pass
   that address as `server`.
2. `diag.dns {name: X}`. Read the verdict; it is one of four. Each is an
   **observation** about two resolvers, not yet a cause.
   - neither resolves: the zone or the name. Account: nameserver groups
     (`references/23-dns-management.md`). **stop**.
   - host yes, tunnel no: the nameserver group cannot answer. → `diag.status {full:
     true}` for `fullStatus.dnsServers[].error`, and `diag.grep {pattern: "upstream nameservers
     failed|Temporarily deactivating|responsive again", max_matches: 20}`. The upstream is
     unreachable through the tunnel (route or policy for port 53) or down. **stop**;
     server-side DNS.
   - tunnel yes, host no: **hypothesis:** the client's DNS is not installed on this
     device. Confirm on the platform before saying so. macOS: → `shell.run scutil --dns`
     and look for the Netzilo resolver entries. Linux: → `diag.grep {pattern: "System DNS
     manager discovered|nameserver group with all domains|resolv", ignore_case: true,
     max_matches: 30}` for which manager the client chose and whether it failed; then
     `resolvectl status` or `cat /etc/resolv.conf` via shell. Windows: → `shell.run
     powershell Get-DnsClientServerAddress -InterfaceAlias wt0` and
     `Get-DnsClientNrptPolicy`; a GPO-pushed NRPT policy replaces the client's local
     rules. **stop** at the layer that does not carry the client's server.
   - both, different addresses: split horizon, a match domain the OS ignores (Linux in
     resolvconf or file mode, §3), or caching. → `diag.dns` for the same name with
     `server` set to the public resolver to compare; browsers cache too. A disagreement
     alone does not prove the client's DNS is missing.
3. **"Slow" or "intermittent" names.** Each upstream gets 15 s, so a group of three dead
   upstreams can hold one lookup for about 45 s. After 5 failures the group is
   deactivated: `all queries to the upstream nameservers failed with timeout`, then
   `Temporarily deactivating nameservers group due to timeout`. Its match domains are
   removed from the host's configuration and a primary group stops being the catch-all,
   so queries go to the OS's other resolvers and internal names may resolve publicly,
   until `upstreams … are responsive again. Adding them back to system` appears.
   **stop**; the fix is the upstream's reachability.
4. Only after the tunnel resolver is proven right, go to 4.2 with the address.

Without tools: ask for `netzilo status` (`Nameservers: n/m Available`) and the platform
check from step 2.

### 4.4 "It is slow"

1. `diag.status {full: true}` → for the peer in question, `relayed`, `direct`,
   `latency`, `lastWireguardHandshake`.
   - `relayed: true` and latency in the hundreds of ms: relay path. Why direct failed
     is in the log: → `mod.loglevel debug`, reproduce, then `diag.grep {pattern:
     "<pubKey prefix>|pion: ice", max_matches: 40}` (ICE library lines carry a
     `[pion: …]` prefix and appear only at debug). Typical: symmetric NAT on both ends,
     UDP blocked (`references/07-client-troubleshooting.md` §4). Lower the level
     afterwards. **stop**.
   - `direct: true` with high latency: **hypothesis:** the path between the two
     networks. Corroborate by measuring the same two sites outside the tunnel before
     excluding Netzilo; `kernelInterface: false` (userspace stack), a routing peer under
     load, or MTU trouble on the path keep Netzilo in scope. Report the measured latency
     either way.
   - handshake age: a healthy tunnel re-handshakes about every 2 minutes and sends a
     keepalive every 25 s, so ages up to about 2.5 minutes are normal. Older than 3
     minutes while "Connected" is a stale tunnel. `mod.refresh` only requests a sync; it
     does not rebuild existing peer tunnels. → `diag.grep {pattern: "<pubKey prefix>",
     max_matches: 30}` for the peer's last state changes. Recovery the person can do:
     `netzilo down` then `netzilo up` (or Disconnect and Connect in the app). **Verified**
     when the handshake age falls back under 2.5 minutes.
2. If everything is direct and low-latency, the slowness is the application or the
   routing peer's own capacity (`references/11-connectivity-diagnosis.md` §5).

### 4.5 "Access denied" / "I can see it but I am blocked"

Two mechanisms produce this and they are distinguished before anything else: policy
that does not join the two, and posture that the source device fails. Neither produces a
"denied" message; both make the target disappear from the source device.

1. Account: does a policy allow this peer to the target at all? If no policy joins
   them, **stop**; that is the answer and the device is irrelevant.
2. Policy exists and carries posture checks. On the **source** (the device the person
   uses):
   - → `diag.status {full: true}`: the target peer or its routing peer is absent from
     `peers[]` (routes: absent from `diag.routes`). **Observation.**
   - → `diag.grep {pattern: "Posture check .* FAILED|Policy evaluation complete",
     max_matches: 20}`: a `❌ Posture check '<name>' … FAILED` line for a check the policy
     carries, with the `FAILED at <check type>` line naming which part failed.
   - → `diag.posture`: its `failing[]` names the same signal. Two signals agreeing is the
     **confirmed cause**. Name the signal and, from §3, whether the platform can even see
     it; a probe blind spot is a finding, say so.
   - Corroboration from the other end, when you may look at it: the destination still
     lists the source, so the source logs `wrongly addressed message <destination key>`
     and `Auto-sync triggered for unknown peer`. Do not wait for `peer.access.blocked`;
     it is recorded only while a destination peer is connected.
3. No posture failure in the log: → `mod.refresh` (the device may hold a stale map), then
   `diag.grep {pattern: "Policy evaluation complete", max_matches: 1}` for the fresh
   count and re-read `diag.status`. Target now present but traffic still blocked: the
   target's own firewall (4.2 step 4).

Without tools: `netzilo status -d` from the person shows whether the target is listed;
the account's posture check definitions (`references/21-posture-checks.md`) and the
peer's reported metadata say which check it likely fails, labelled as hypothesis.

### 4.6 "It worked yesterday"

The answer is in the log; the job is to find the moment it changed.

1. `diag.grep {pattern: "warn|erro", ignore_case: true, max_matches: 40}` → the shape of
   the last hours. Most recent first is what you want.
2. Narrow on the first family that appears. These are the lines that actually occur:
   `failed to establish connection to peer`, `ICE connection state changed to Failed`,
   `Posture check .* FAILED`, `Policy evaluation complete`, `Sync failed`,
   `login has expired`, `has not been assigned a routing peer`,
   `upstream nameservers failed`, `wrongly addressed message`. Use `context: 3` to see
   what preceded the first occurrence; use `from_start: true` with a tighter pattern to
   find when it began. For ICE detail, `mod.loglevel debug` is enough; lower it after.
3. `all_files: true` when yesterday has rotated. `total` tells you whether it is a burst
   or a constant.
4. Cross-check the moment against the account's activity events for the same window
   (`references/30-activity-reports-and-integrations.md`): a policy edit, a route change,
   a peer removal, a posture check change. A log change and an account event that line
   up are a **hypothesis**. **stop** when the mechanism is shown too (for example the
   event removed a group and the next `Policy evaluation complete` count fell), or when
   reverting the change restores service.

### 4.7 After an upgrade or reinstall

1. `diag.system` → `client_version` versus what the account shows for the peer.
2. `diag.config` → `configFile` and `managementUrl`; a reinstall that created a fresh
   config appears as a *new* peer in the account and the old one goes stale.
3. `diag.grep {pattern: "migrat|config|version", ignore_case: true}`.
4. If the device is too old for tools (management says so before dispatching), every
   step here is by hand: `references/05-client-install-and-deploy.md`.

### 4.8 "The agent cannot reach my device"

This is about the tools themselves. Read `references/36-device-tools.md` §3 and §9:
offline, too old, not this node, no access, did not answer. None is a device fault to
diagnose with device tools; each names its own fix. *Offline* includes every device
whose management or signal connection is down or whose login has expired (§1); for those,
4.1 step 0.

### 4.9 "The peer shows Disconnected" / "the connection keeps dropping"

Find the peer's `pubKey` in `diag.status {full: true}` and grep a prefix of it: the
first 8 characters also match the `Auto-sync` lines. Patterns are regular expressions:
escape `+` as `\+`, or pick a stretch of the key without it.

| Log line for that key | Reading | Next |
|---|---|---|
| `failed to establish connection to peer <key>: connection to peer <key> timed out after 3…s` (30–45 s) | the remote never answered the offer: it is offline, its login expired, its signal is down, or it does not have this device in its map | the remote's `connected` and `login_expired` in the API, then `diag.status` on the remote; there, `wrongly addressed` lines naming this device's key are the policy or posture mismatch of §1 |
| `peer <key> ICE connection state changed to Failed - connection lost`, then `disconnected from peer <key>` | the two ends exchanged offers but no usable path exists, including through the relay: UDP blocked and TURN unreachable on at least one side | `Relays:` on both ends; `references/07-client-troubleshooting.md` §4 |
| `… changed to Disconnected - waiting for recovery` followed by `ICE layer established` | a brief loss that recovered | none, unless it repeats |
| `connection established successfully [...]: direct=…, relayed=…` | the tunnel is up and says which path | 4.4 if slow |
| `error while handling message of Peer [key: <key>] … wrongly addressed message <key>` | that peer has this device in its map; this device does not have it | 4.5 on this device |
| nothing for the key | the remote is not connecting and this device is not either | the remote's state in the API |

A remote whose login has expired carries no flag in `diag.status`: it shows Disconnected,
or is dropped once the account has marked it expired. Check the remote's `login_expired`
and `connected` in the API, then `diag.status` on the remote if it is reachable.

**After a network change** (Wi-Fi switch, sleep, docking): on macOS and Windows the
network monitor restarts the connection on an interface change. On Linux there is no
monitor by default; each peer recovers when ICE fails and reconnects, which can take tens
of seconds. A Linux complaint of "30 seconds dead after switching networks" is that,
not a fault.

Without tools: `netzilo status -d` from both ends shows each side's view of the other.

## 5. What the device cannot tell you

Say these plainly rather than running another tool:

- whether a policy *should* permit something (the account; the device only shows what it
  computed);
- what another device sees or computed (you are on one device; the two ends of a rule
  can disagree, §1);
- whether a change took effect on the network (read the device back, and the account);
- the content of the debug bundle it wrote (nothing uploads it);
- anything about a device whose client is too old for tools, or that is offline.

## 6. Reporting

Report the ledger, in the product's words. For each finding: the symptom as stated, the
platform, what you read and what it showed (quote verdicts), each conclusion with its
label from §2 and what backs it, the cause in one sentence, what you changed and how to
undo it, and what remains open. If a posture signal is involved, say whether the platform
can see it. If you ran anything on a device the caller does not own, list it even when it
was read-only.
