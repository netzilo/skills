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
chars: 13955
sections:
- id: '1'
  title: Facts you take as given
  chars: 1704
- id: '2'
  title: The loop
  chars: 1579
- id: '3'
  title: The OS matrix
  chars: 1696
- id: '4'
  title: Decision trees
  chars: 7505
- id: '5'
  title: What the device cannot tell you
  chars: 405
- id: '6'
  title: Reporting
  chars: 416
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

- **Policy is evaluated on the server.** A device cannot tell you whether A may reach B;
  the account can (`references/20-policies-access-control.md`). The device tells you what
  it *received*: peers in `diag.status`, routes in `diag.routes`. Empty is a policy
  result, not a connectivity fault.
- **A peer sees only what policy gives it.** `peers: []` with management Connected means
  no policy joins this device to anything, or every counterpart is offline.
- **Routes exist twice.** Once in the account, once as *selected* on the device.
  `diag.route_match` reports both; an unselected route carries nothing.
- **DNS is two resolvers.** The tunnel's nameserver groups, and the host's resolver
  which the client installs itself into. `diag.dns` tests both; `diag.probe` in `dns`
  mode tests only the host's.
- **Posture is probed locally, with platform-specific heuristics, and enforced
  remotely.** `diag.posture` shows the probe; `references/21-posture-checks.md` shows
  what the account enforces. Only the pair explains a denial.
- **The client log is the record.** Anything the device did, tried, or failed at in the
  last hours is in `client.log`, and `diag.grep` searches it on the device. If you find
  yourself guessing what happened, you have not searched yet.
- **Management refusing to dispatch is not a device finding.** A line beginning
  `the command did not run:` means the device never saw the request
  (`references/36-device-tools.md` §11).

## 2. The loop

Every device problem is narrowed the same way. Write the ledger as you go; it is what
you report at the end and what stops you from repeating a read.

1. **State the symptom in the person's words**, and translate it into which of the trees
   in §4 it is. "VPN is broken" is not a symptom; "I can ping the server but cannot open
   the app" is.
2. **Read the account first**, from the API: is the peer connected and approved, is its
   login expired, which groups is it in, what policy and routes should it have. Two
   minutes here prevents twenty on the device.
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

Two habits that separate a diagnosis from a fishing trip: never change anything before
the read-only path is exhausted, and never conclude from one signal what needs two. "It
is relayed" is a fact; "it is slow because it is relayed" needs the latency too.

## 3. The OS matrix

The client is one code base, but the places it touches differ. When a tree says "check
X on the device", this is what X is on each platform.

| | macOS | Linux | Windows |
|---|---|---|---|
| reported as | `Darwin <version>` | distribution name | `Windows <edition>` |
| daemon identity | `root` via launchd (`Netzilo`) | `root` via systemd (`netzilo`) | `SYSTEM` service (`Netzilo`) |
| config | `/etc/netzilo/config.json` | same | `%PROGRAMDATA%\Netzilo\config.json` |
| log | `/var/log/netzilo/client.log` | same | `%PROGRAMDATA%\Netzilo\client.log`, **same folder as config** |
| tunnel interface | `utun100` | `wt0` | `wt0` adapter |
| host DNS installed via | system configuration (`scutil --dns`) | NetworkManager → systemd-resolved (`127.0.0.53`) → resolvconf → `/etc/resolv.conf`, auto-detected at start | per-adapter DNS on `wt0` |
| routes programmed via | `route` | netlink, policy rules (table 100) | `route` (System32) |
| `shell.run as:user` | drop to console user | drop to console user | duplicate session token; needs SYSTEM |
| shell for pipelines | `sh -c` | `sh -c` | `powershell -NoProfile -NonInteractive -Command` |
| posture blind spots | few | screen lock only GNOME/KDE; AV only ClamAV; OS-updated only apt | few |
| what a hand-started `-F` client changes | runs as the user; no log file unless `--log-file`; disconnect exits the process | same | same |

Two Windows facts change how you search: the log directory also holds `config.json` and
`token.dat`, so `diag.grep` with `all_files` scans them (named secrets are redacted, but
prefer the default log), and the service has no user `PATH`, so shell commands need
absolute paths or PowerShell.

## 4. Decision trees

Each tree starts after §2 steps 1–3. `→` is the next read; **stop** is where the cause
is established and further reads add nothing.

### 4.1 "Not connected" / "the client shows disconnected"

1. `diag.status` → `status` and `fullStatus.managementState`.
   - management **Disconnected**: → `diag.config` for `managementUrl`. Wrong server:
     **stop**, that is the cause. Right server: → `diag.probe {mode: http, target:
     <managementUrl>}`. Unreachable from the device: **stop**, network path or proxy on
     that machine (`references/07-client-troubleshooting.md` §4). Reachable: → `diag.grep
     {pattern: "login|auth|expired|denied", ignore_case: true, max_matches: 20}`;
     `LoginExpired` or an auth error: **stop**, the person must sign in
     (`references/07-client-troubleshooting.md` §2). Account side: is the peer approval
     pending or login-expired in `GET /api/peers`?
   - management Connected, signal **Disconnected**: peers cannot negotiate. → `diag.grep
     {pattern: "signal", ignore_case: true}`. Signal is a server or firewall matter
     (`references/03-server-troubleshooting.md`, `references/07-client-troubleshooting.md` §4). **stop**.
2. Both connected and the person still says "disconnected": they mean a peer. Go to 4.2.

### 4.2 "Connected but I cannot reach host X"

1. Classify X: address or name. Name → 4.3 first, then return here with the address.
2. `diag.route_match {target: X}`.
   - `matched: false`: X is not a Netzilo destination on this device. Either it is a
     peer you should reach directly (continue at 3) or there is no route for it in the
     account (`references/22-network-routes-and-exit-nodes.md`). **stop** on the second.
   - matched, `best.selected: false`: **stop**, the route is not enabled on this device;
     enabling it is an account or client setting, not a device tool.
   - matched and selected: → 3 for the peer that serves it.
3. `diag.status {full: true}` → find the peer or routing peer in `peers[]`.
   - absent: policy does not join them, or it is offline. Account: policy between the
     groups (`references/20-policies-access-control.md` §3 of `11-connectivity-diagnosis.md`). **stop**.
   - present, `connStatus` not Connected: → `diag.grep {pattern: "<peer IP>|<peer
     fqdn>", max_matches: 30, context: 1}` for handshake and ICE lines. Both sides need
     signal and a relay or a direct path; `references/07-client-troubleshooting.md` §3. **stop**
     at the first line that names the failure.
   - Connected, `relayed: true`: reachable but via relay; if the complaint is "slow",
     go to 4.4.
   - Connected and direct: → `diag.probe {mode: tcp, target: "X:port"}` from the device.
     Refused or timeout with the tunnel healthy: the service on X, or a firewall on X or
     on the routing peer (`references/11-connectivity-diagnosis.md` §5). **stop**.

### 4.3 "Names do not resolve" / "works in the browser, not in the app"

1. `diag.dns {name: X}`. Read the verdict; it is one of four.
   - neither resolves: the zone or the name. Account: nameserver groups
     (`references/23-dns-management.md`). **stop**.
   - host yes, tunnel no: the nameserver group cannot answer. → `diag.status {full:
     true}` for `dns_servers[].error`. **stop**; server-side DNS.
   - tunnel yes, host no: **the client's DNS is not installed on this device.** This is
     the platform branch. macOS: → `shell.run scutil --dns` and look for the Netzilo
     resolver entries. Linux: → `diag.grep {pattern: "dns|resolv|systemd-resolved|
     NetworkManager", ignore_case: true, max_matches: 30}` to see which manager the
     client chose and whether it failed; then `resolvectl status` or `cat
     /etc/resolv.conf` via shell. Windows: → `shell.run powershell
     Get-DnsClientServerAddress -InterfaceAlias wt0`. **stop** at the layer that does
     not carry the client's server.
   - both, different addresses: split horizon or caching. → `diag.dns` for the same
     name with `server` set to the public resolver to compare; browsers cache too.
2. Only after the tunnel resolver is proven right, go to 4.2 with the address.

### 4.4 "It is slow"

1. `diag.status {full: true}` → for the peer in question, `relayed`, `direct`,
   `latency`, `lastWireguardHandshake`.
   - `relayed: true` and latency in the hundreds of ms: relay path. Why direct failed
     is in the log: → `diag.grep {pattern: "ICE|candidate|relay", max_matches: 30}`.
     Typical: symmetric NAT on both ends, UDP blocked (`references/07-client-troubleshooting.md` §4). **stop**.
   - `direct: true` with high latency: the network between the two devices, not
     Netzilo. **stop**; report the measured latency.
   - handshake older than two minutes while "Connected": the tunnel is stale. →
     `mod.refresh`, then re-read. If it recurs: log around the handshake failures.
2. If everything is direct and low-latency, the slowness is the application or the
   routing peer's own capacity (`references/11-connectivity-diagnosis.md` §5).

### 4.5 "Access denied" / "I can see it but I am blocked"

Two mechanisms produce this and they are distinguished before anything else.

1. Account: does a policy allow this peer to the target at all? If no policy joins
   them, **stop**; that is the answer and the device is irrelevant.
2. Policy exists and carries posture checks: → `diag.posture`. Compare `failing[]`
   against the checks the policy enforces (`references/21-posture-checks.md`).
   - a match: **stop**, name the signal and, from §3, whether the platform can even
     see it. On Linux, a "screen lock" failure on a non-GNOME desktop or an "OS
     updated" failure on a non-apt distribution is a probe blind spot; say so.
   - no match: → `mod.refresh` (the device may hold stale policy) and re-read
     `diag.status`; if still blocked, the target's own firewall (4.2 step 3).

### 4.6 "It worked yesterday"

The answer is in the log; the job is to find the moment it changed.

1. `diag.grep {pattern: "warn|erro", ignore_case: true, max_matches: 40}` → the shape of
   the last hours. Most recent first is what you want.
2. Narrow on the first family that appears: `handshake .* did not complete`, `relay dial
   failed`, `sync .* failed`, `login`, `dns`. Use `context: 3` to see what preceded the
   first occurrence; use `from_start: true` with a tighter pattern to find when it began.
3. `all_files: true` when yesterday has rotated. `total` tells you whether it is a burst
   or a constant.
4. Cross-check the moment against the account's activity events for the same window
   (`references/30-activity-reports-and-integrations.md`): a policy edit, a route change,
   a peer removal. **stop** when a log line and an account event line up.

### 4.7 After an upgrade or reinstall

1. `diag.system` → `client_version` versus what the account shows for the peer.
2. `diag.config` → `configFile` and `managementUrl`; a reinstall that created a fresh
   config appears as a *new* peer in the account and the old one goes stale.
3. `diag.grep {pattern: "migrat|config|version", ignore_case: true}`.
4. If the device is too old for tools (management says so before dispatching), every
   step here is by hand: `references/05-client-install-and-deploy.md`.

### 4.8 "The agent cannot reach my device"

This is about the tools themselves. Read `references/36-device-tools.md` §11: offline,
too old, not this node, no access, did not answer. None is a device fault to diagnose
with device tools; each names its own fix.

## 5. What the device cannot tell you

Say these plainly rather than running another tool:

- whether a policy permits something (server);
- what another device sees (you are on one device);
- whether a change took effect on the network (read the device back, and the account);
- the content of the debug bundle it wrote (nothing uploads it);
- anything about a device whose client is too old for tools.

## 6. Reporting

Report the ledger, in the product's words. For each finding: the symptom as stated, the
platform, what you read and what it showed (quote verdicts), the cause in one sentence,
what you changed and how to undo it, and what remains open. If a posture signal is
involved, say whether the platform can see it. If you ran anything on a device the
caller does not own, list it even when it was read-only.
