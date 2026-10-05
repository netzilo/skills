---
id: '22'
title: Admin Skill — Network Routes, Routing Peers and Exit Nodes
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 14723
sections:
- id: '1'
  title: Model
  chars: 1929
- id: '2'
  title: Field reference
  chars: 2771
- id: '3'
  title: API
  chars: 835
- id: '4'
  title: Procedures
  chars: 2818
- id: '5'
  title: What the routing peer does (for verification)
  chars: 899
- id: '6'
  title: Diagnosis
  chars: 5006
---
# Admin Skill — Network Routes, Routing Peers and Exit Nodes

**Dashboard:** Network → **Routes** (`/network-routes`); also Peers → peer → Network
Routes / **Add Exit Node**. **API:** `/api/routes`.

Routes publish networks that do not run the Netzilo client (office LANs, cloud VPCs,
domain-based SaaS endpoints, or the whole Internet) through one or more **routing
peers**. This skill covers design, every field, HA, the routing peer itself, and
diagnosis.

---

## 1. Model

- A **route** = network identifier + destination (**Network Range** CIDR or **Domains**)
  + **routing peer** (a single Linux peer) or **peer group** (Linux peers → HA) +
  **distribution groups** (which peers receive the route) + metric, masquerade, enable.
- Routes with the same **Network Identifier** form one *network*; several routes in a
  network with different routing peers give **high availability** — each client picks
  one by metric and connection quality and fails over automatically.
- **Only Linux peers can route.** The peer selector lists Linux peers only; a peer group
  used as routing group must contain Linux peers.
- **Masquerade** (default on): the routing peer NATs client traffic to its own LAN IP,
  so the target network needs no return route. Off: targets must route
  `100.64.0.0/10` back via the routing peer.
- **Exit node** = a route for `0.0.0.0/0` (IPv4 only; IPv6 is blocked). Masquerade is
  always on for exit nodes.
- **Domain routes**: the client resolves the domains through the host's resolver about
  every minute and installs routes for the returned IPs; "Keep Routes" retains previously
  resolved IPs.
- Routed traffic is still subject to **policies**: the client's group must be allowed to
  reach the routing peer's group for the protocol/ports; a rule's **Routes** field and the
  route's **Policy Groups** narrow which CIDRs are reachable. The client computes this on
  the device: a route whose routing peer it may not connect to, by policy or because the
  client fails a posture check, is not given to it at all.
- Clients can override selection with `netzilo routes select`. *Selected* is only that
  choice. A selected route with no connected routing peer is removed from the client's
  OS, and traffic for it falls back to the client's own default route: routes **fail
  open**. For an exit node that means the person quietly uses their local internet.

---

## 2. Field reference

**Create Route** (Routes → Add Route) — tabs Route / Name & Description / Additional Settings.

| Field | UI help | Notes |
|---|---|---|
| Route Type | "Select your route type to add either a network range or a list of domains." | **Network Range** or **Domains** |
| Network Range | "Add a private IPv4 address range" | CIDR e.g. `172.16.0.0/16`; error "Please enter a valid CIDR" |
| Domains | "Add domains that dynamically resolve to one or more IPv4 addresses" | list; **Keep Routes** toggle: "Retain previously resolved routes after IP address updates to maintain stable connections." Domains force masquerade on |
| Routing Peer | "Assign a single peer as a routing peer for the network route." | Linux peers only |
| Peer Group | "Assign a peer group with Linux machines to be used as routing peers." | exactly one group; automatic HA |
| Distribution Groups | "Advertise this route to peers that belong to the following groups" | who gets the route |
| Policy Groups (Optional) | "Policy groups are used in policies while specifying access control rules on this route such as IP based filtering" | groups to reference in policies' Routes rules |
| Network Identifier | "Add a unique network identifier that is assigned to each device." | ≤40 chars; same identifier = same network (HA) |
| Description | | |
| Enable Route | "Use this switch to enable or disable the route." | |
| Masquerade | "Allow access to your private networks without configuring routes on your local routers or other devices." | hidden for exit nodes |
| Metrics | "A lower metric indicates higher priority routes." | 1–9999, default 9999 |

**Update route**: network range/domains and identifier are **not editable** — delete and
recreate to change them. Editable: routing peer / peer group, distribution groups, policy
groups, description, enable, masquerade, metric.

**Add New Routing Peer** ("When you add multiple routing peers, Netzilo enables high
availability for this network."): pick the network, a Linux peer not yet routing it,
distribution groups → creates another route in the same network (metric 9999,
masquerade on).

**Exit node** (Peers → ⋮ → Add Exit Node, or Routes → Add Exit Node / Set Up Exit Node):
description "Route all internet traffic through a peer"; choose routing peer or Linux peer
group, distribution groups; network fixed to `0.0.0.0/0`.

**Table**: outer rows per network (Name = identifier, Network = CIDR / domain badges /
"Exit Node", Type = peer group badge or "Routing Peers", High Availability = "n Peer(s)"
or "Disabled" with Add Peer / Go to Peers, Delete network); expand for inner routes
(routing peer with online dot, Metric, Active toggle, Distribution Groups, Policy Groups,
Edit, Delete). Filter Enabled/All.

---

## 3. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/routes ; GET/PUT/DELETE /api/routes/{id}
```
```json
{"network_id":"dc-1","description":"Datacenter LAN","enabled":true,
 "peer":"<peer-id>",              // or "peer_groups":["<group-id>"]
 "network":"10.20.0.0/16",        // or "domains":["erp.example.com"],"keep_route":true
 "metric":100,"masquerade":true,
 "groups":["<distribution-group-id>"],
 "access_control_groups":["<policy-group-id>"]}
```
Exit node: `"network":"0.0.0.0/0"`. Exactly one of `peer` / `peer_groups`, one of
`network` / `domains`.

---

## 4. Procedures

### 4.1 Publish a LAN/VPC
1. Deploy a Linux routing peer inside the network (`05-client-install-and-deploy.md`
   §8.6) with a setup key whose auto-group is e.g. `dc-routers`. Size: 2 vCPU / 4 GB is
   fine for small sites; the documentation recommends 4 vCPU / 8 GB / 50 GB for busy ones.
2. Routes → Add Route: range `10.20.0.0/16`, routing peer (or peer group `dc-routers`),
   distribution group `employees`, identifier `dc-1`, masquerade on, metric 100.
3. Policy: `employees → dc-routers`, protocol/ports the users need (or ALL to start).
4. On a client: `netzilo routes list` shows `dc-1 … Selected`; `ip route get 10.20.5.7`
   exits via `wt0`; connect to a host.
5. Cloud: the routing peer's security group must allow egress to the VPC; target hosts'
   security groups must allow ingress from the routing peer's private IP (masquerade on)
   — or from `100.64.0.0/10` with masquerade off plus a VPC route back to the routing
   peer.

### 4.2 Add high availability
Routes → network → High Availability → **Add Peer** (second Linux peer) or switch the
route to a **Peer Group** with two or more Linux peers. Keep metrics equal for active
failover; give one a lower metric to prefer it.

### 4.3 Restrict what is reachable inside the routed network
Create route with **Policy Groups** `dc-db`; policy rule `analysts → dc-db`, TCP 5432,
**Routes** `10.20.5.0/24`. Analysts can then only reach that subnet on that port even
though the route publishes `/16`.

### 4.4 Domain (SaaS / dynamic IP) route
Route type Domains, e.g. `erp.example.com`, Keep Routes on, routing peer with static
egress IP that the SaaS allow-lists. Clients re-resolve every minute
(`--dns-router-interval` on the client changes it).

### 4.5 Exit node for a group
Peers → Linux peer → ⋮ → **Add Exit Node** → distribution group `travellers`. Then
Network → DNS Servers → add a resolver **without match domains** for `travellers` so DNS
also leaves through the exit node. Policy `travellers → <exit-node group>` ALL.
IPv6 is dropped by design on exit-node clients. While no exit node in the network is
connected to a client, that client uses its local internet connection (§1); give the
network two exit nodes (§4.2) where that matters.

### 4.6 Split overlapping networks
Two sites both using `192.168.1.0/24`: give them different identifiers and distribution
groups; clients in both groups must pick with `netzilo routes select <id>`. Better:
renumber or publish narrower ranges. The same collision happens with a client's own
network: a home LAN numbered like the office route keeps its traffic local (§6.1).

### 4.7 Decommission a routing peer
Add a replacement first (§4.2), confirm clients fail over (`netzilo status -d` →
`Routes` shown for the new peer), then delete the old route (inner row) and the peer.

---

## 5. What the routing peer does (for verification)

On a Linux routing peer the client enables `net.ipv4.ip_forward`, installs a policy
routing rule (priority 110, fwmark) pointing at routing table **7120**, and creates
firewall chains: nftables table `netzilo` with `netzilo-rt-fwd` (allowed forwarded
traffic) and `netzilo-rt-nat` (masquerade), or iptables chains `NETZILO-RT-FWD` and
`NETZILO-RT-NAT` (plus `NETZILO-ACL-INPUT/OUTPUT` for its own policies). Inspect with
`sudo nft list table inet netzilo` or `sudo iptables -S | grep NETZILO` and
`sudo iptables -t nat -S NETZILO-RT-NAT`. Do not edit these chains by hand; they are
rebuilt on every network-map update.

Host firewalls with a default `FORWARD DROP` (ufw, firewalld) must allow forwarding
between `wt0` and the LAN interface: `sudo ufw route allow in on wt0 out on <lan>` (and
back), or firewalld zone forwarding/masquerade.

---

## 6. Diagnosis

Full procedure: `11-connectivity-diagnosis.md` §4–§5. Quick table:

| Symptom | Likely cause | Check / fix |
|---|---|---|
| Client does not list the route (`netzilo routes list`) | client not in a distribution group; route disabled; not yet synced | groups; Active toggle; `netzilo refresh` |
| Route listed as "Not Selected" | overlapping network with lower metric selected, or user deselected | `netzilo routes select <id>` / `select all` |
| Route selected, packets never leave the client via `wt0` | conflicting local route on the client, or no routing peer connected (fail open) | §6.1 |
| Exit node set, but the client's public IP is still its own | no exit node connected to the client (fail open), or the client does not program default routes in its current mode | §6.1 |
| Client reaches the routing peer but not the LAN host | forwarding blocked on the router (host firewall / `ip_forward`), target firewall, masquerade off without return route, cloud security group | `sysctl net.ipv4.ip_forward`; tcpdump on `wt0` and the LAN interface; SG rules |
| Works for some clients only | policy differs between groups; posture checks (a client failing one does not receive the route at all) | resolve rules per client (`20` §6); on the client, grep the log for `Posture check .* FAILED` |
| Whole network unreachable | routing peer offline / login expired / deleted | Peers page dot & badges; `netzilo status` on the router |
| Exit node: browsing fails, ping works | DNS not routed | add resolver without match domains for the group |
| Exit node: IPv6 sites unreachable | IPv6 blocked by design | disable IPv6 on the client or accept |
| HA shows "Disabled" | only one routing peer/route in the network | add a peer or use a group with ≥2 Linux peers |
| Cannot select a peer as router | not Linux, or already routing this network | pick a Linux peer |
| Delete network fails | referenced by a policy's Policy Groups? | remove the reference first (group deletion rules) |
| Route update refuses CIDR change | by design | delete and recreate (clients converge within ~30 s) |

Events: `route.add/update/delete`, `peer.access.blocked`, `peer.access.target(.blocked)`.
`peer.access.blocked` is recorded only while a destination peer is connected; its
absence does not show that posture passed.

### 6.1 Reading a route on the client

The account says which routes a client should get; the client decides what it uses.
Read it there (`netzilo status -d`, `netzilo routes list`, the client log, or the device
tools `diag.routes`, `diag.route_match` and `diag.status {full: true}`):

- **Is it given to the client?** `netzilo routes list` lists it. If not: distribution
  groups, route disabled, or the client may not connect to the routing peer (policy, or a
  failing posture check: `❌ Posture check '<name>' (ID=…) FAILED` in the log).
- **Which routing peer carries it right now?** `Routes:` per peer in `netzilo status -d`
  (`peers[].routes` in `diag.status`). The log records each choice: `New chosen route is
  <id> with peer <key> with score … for network [<id>] (latency=…, direct=…,
  relayed=…)`.
- **None does.** `The network [<id>] has not been assigned a routing peer as no peers
  from the list [<keys>] are currently connected`: the route is out of the OS and the
  traffic takes the client's default route. The keys are the routing peers' WireGuard
  public keys; find them in the Peers list and go to `11-connectivity-diagnosis.md` §2
  for why they are not connected.
- **Two networks claim the prefix.** `Prefix [<cidr>] is already routed by peer [<key>].
  HA routing disabled` (for domain routes, `IP [<ip>] for domain [<domain>] is already
  routed by peer [<key>]. HA routing disabled`).
- **Domain route not resolving.** `Failed to resolve domains for route [<id>]: …`: the
  client resolves the domains through its host resolver about every minute and retries
  sooner after a failure; the host resolver must be able to answer for them.
- **Exit node ignored.** `This agent version: <v>, doesn't support default routes,
  received <prefix>, skipping this prefix`: the client does not program default routes
  in its current mode: an older client, or one whose service environment sets
  `NB_DISABLE_CUSTOM_ROUTING=true`. Update the client, or remove that setting.
- **A local route wins.** Check the chosen path on the client: Linux `ip route get
  <ip>`, macOS `route -n get <ip>`, Windows `Find-NetRoute -RemoteIPAddress <ip>`. It
  must name `wt0` (`utun100` on macOS). On Linux Netzilo's routes are in table 7120
  (`netzilo`) and rule 100 (`lookup main suppress_prefixlength 0`) is consulted before rule
  110 (`not fwmark 0x1bd00 lookup netzilo`), so any main-table route covering the target
  other than the default route wins, however broad. On macOS and Windows an identical
  existing prefix is skipped: `Skipping adding a new route for network <cidr> because it
  already exists`. The usual case is a home LAN numbered like the office route (§4.6).
