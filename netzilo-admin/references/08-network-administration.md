---
id: 08
title: Netzilo — Network Administration (Peers, Policies, Routes, DNS, Posture, Activity)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 20414
sections:
- id: '1'
  title: Peers (Endpoint → Peers, `/peers`)
  chars: 2796
- id: '2'
  title: Setup keys (Endpoint → Setup Keys, `/setup-keys`)
  chars: 975
- id: '3'
  title: Groups
  chars: 592
- id: '4'
  title: Policies (Network → Policies, `/access-control`)
  chars: 3417
- id: '5'
  title: Routes and exit nodes (Network → Routes, `/network-routes`)
  chars: 2562
- id: '6'
  title: DNS (Network → DNS Servers `/dns/nameservers`, DNS Settings `/dns/settings`)
  chars: 2809
- id: '7'
  title: Posture checks (Endpoint → Posture Checks, `/posture-checks`)
  chars: 2519
- id: '8'
  title: Activity, reports, integrations
  chars: 2891
- id: '9'
  title: Multi-tenant / self-service (cloud and MSP servers)
  chars: 759
---
# Netzilo — Network Administration (Peers, Policies, Routes, DNS, Posture, Activity)

**Audience:** an AI operator configuring a customer's Netzilo network in the dashboard
or via API. UI labels are quoted as they appear in the dashboard. Dashboard paths are relative to `https://<domain>` (cloud:
`https://go.netzilo.com`).

Mental model:

- A **peer** is a device. It belongs to **groups**. Every peer is automatically in the
  immutable group **All**.
- **Policies** (Network → Policies, URL `/access-control`) are the only thing that allows
  traffic between peers. There are only *allow* rules; anything not allowed is dropped.
  A new account has a **Default** policy `All → All, all protocols, bidirectional`.
- **Posture checks** attach to policies (and to profiles/filters) and gate the *source*
  peer.
- **Routes** publish external networks (LAN/VPC/Internet) through Linux **routing
  peers**; **DNS** distributes nameservers and gives every peer `<name>.<dns-domain>`.
- Changes reach peers within ~30 s (peers pull the network map); `netzilo refresh` on a
  peer forces it.

---

## 1. Peers (Endpoint → Peers, `/peers`)

List columns: Name (green dot = online, owner e-mail), Security Score (A–F), Address
(DNS label + IP, copyable), Groups, Last seen, OS, Version ("Update available" tooltip),
status badges (**Approval required** + **Approve**, **Expiration disabled**, red
**Login required**), actions. Filters: All / Online / Offline, Pending Approvals, group
selector, search "by name, IP, owner or group".

Per-peer actions (⋮ or detail page `/peer?id=`):

| Action | Effect | API |
|---|---|---|
| Rename | new DNS label preview shown; duplicates get a numeric suffix | `PUT /api/peers/{id}` `{"name":…}` |
| Assigned Groups | membership for policies/routes/DNS | `PUT /api/groups/{id}` `{name,peers}` per group |
| Login Expiration on/off | only SSO-enrolled peers (setup-key peers show "Login expiration is disabled for all peers added with an setup-key.") | `login_expiration_enabled` |
| SSH Access | enable the embedded SSH server (confirm "Experimental feature…"); the peer must also run with `--allow-server-ssh` | `ssh_enabled` |
| Add Exit Node / Add Route | Linux peers only | see §5 |
| Approve | clears `approval_required` | `PUT /api/peers/{id}` `{"approval_required":false}` |
| Delete | removes the peer; the device must re-enrol to return | `DELETE /api/peers/{id}` |
| Bulk: Assign Groups (add or **Overwrite**), Sync Peers (`POST /api/peers/sync`), Delete All (`POST /api/peers/bulk-delete`, max 1000) | | |

Detail page shows Device ID, Netzilo IP, Public IP, Domain Name, AD Domain, Hostname,
Region, OS, Security Score with posture indicators (firewall, antivirus, disk encryption,
OS updates, virtual device, screen lock, device integrity, Enterprise Workspace,
Enterprise Browser), Last seen, Agent/UI version, and (admins) **Available Snapshots**
(AI session snapshots) and the peer's **Network Routes**.

Peer lifecycle facts:

- **Login expiration** (Settings → Authentication): SSO peers must re-authenticate after
  the period (default 24 h); they show **Login required** when expired. Setup-key peers
  never expire.
- **Inactivity expiration**: SSO peers disconnected longer than the period are expired.
- **Ephemeral** peers (from ephemeral setup keys) are deleted 10 minutes after going
  offline.
- **Approval required** (Cloud): new peers are flagged for an admin to review and
  **Approve**. Treat it as a review queue: do not rely on peer approval to keep a device
  off the network. To keep a device out, block its user (Team → Users) or delete the
  peer.
- Free plan limits: 5 users / 100 peers. The device is refused with the exact text
  `maximum number of personal peers reached`; a refusal with any other text is not the
  plan (`24-peers-and-setup-keys.md` §6). Self-hosted Enterprise/MSP deployments are
  unlimited.

---

## 2. Setup keys (Endpoint → Setup Keys, `/setup-keys`)

Create Setup Key modal: **Name**; **Make this key reusable** (off = one-off, usage 1);
**Usage limit** (blank = unlimited); **This key expires** (off = never) + **Expires in**
1–365 days (default 7); **Ephemeral Peers** ("Peers that are offline for over 10 minutes
will be removed automatically"); **Auto-assigned groups**. The key is displayed once.

Table shows usage `x of N Peers`, last used, groups (editable), Ephemeral badge,
Expires, copy (copies the key), Delete. States: valid, overused, expired, revoked.
Revoking/deleting **does not** disconnect already-enrolled peers; delete the peers
instead. Auto-groups apply only to newly enrolled peers.

API: `POST /api/setup-keys` `{name, type: "reusable"|"one-off", expirable, expires_in (seconds, 86400–31536000), revoked:false, auto_groups:[ids], usage_limit (0=unlimited), ephemeral}`;
revoke via `PUT … {"revoked":true}`; `DELETE /api/setup-keys/{id}`.

---

## 3. Groups

Created implicitly anywhere a group selector accepts a typed name + Enter, or via
`POST /api/groups {name, peers}`. Managed in **Settings → Groups** (table with usage
counts across Setup Keys, Peers, DNS, Access Controls, Network Routes, Users, Profiles,
Filters; **Delete** only when unused). `All` cannot be edited or deleted.

Sources of membership: manual assignment, setup-key auto-groups, user auto-groups
propagated to the user's peers (**Enable user group propagation**), JWT claim sync
(**Enable JWT group sync**, name-matched, never auto-created), integrations.

---

## 4. Policies (Network → Policies, `/access-control`)

Netzilo policies hold **multiple rules** (Duplicate / Move Up / Move Down / Delete per
rule). Each rule:

| Field | UI | Semantics |
|---|---|---|
| Protocol | ALL / TCP / UDP / ICMP | ALL and ICMP force bidirectional and no ports |
| Source / Destination | group selectors | groups, not peers; same group both sides = intra-group traffic |
| Direction | arrows between Source and Destination | `bi` (both directions), or one-way for TCP/UDP **with at least one port** |
| Ports | single ports or ranges `start-end`, 1–65535 | empty = all (only allowed when bidirectional) |
| Routes | "Allow network traffic and access only to specified targets" (CIDRs) | Netzilo-specific `allowed_routes`: restricts which routed networks this rule may reach |
| Enable Policy | toggle | disables policy and all rules |

Tabs: **Policy**, **Posture Checks** (attach checks; **Posture Check Evaluation**
All / Any → `any_check_must_pass`), **Name & Description**. A JSON editor view
(`Policy Rules (JSON Format)`) allows bulk editing rules as an array with
`protocol, sources, direction (IN|OUT|BOTH), destinations, ports, routes`. Note the JSON
direction is inverted relative to the UI arrows (`in` in the UI is written as `OUT`);
when in doubt use the UI arrows and verify with a test connection.

One-way TCP/UDP semantics: for a non-bidirectional rule the dashboard sends
`bidirectional:false` and, for the UI's `in` arrow, swaps sources/destinations. Reloading
an existing one-way rule always displays the `out` arrow. Operationally: "source group
may initiate to destination group on these ports; return traffic is allowed".

Enforcement detail: the initiating peer enforces OUT rules; the receiving peer accepts
all inbound over the tunnel (an implicit `ALLOW ALL IN` is appended on every peer). So
a policy edit takes effect on the *source* peers.

API: `POST /api/policies` `{name, description, enabled, any_check_must_pass, source_posture_checks:[ids], rules:[{name, description, enabled, action:"accept", protocol:"all|tcp|udp|icmp", bidirectional, sources:[groupIds], destinations:[groupIds], ports:["443","8000-8100"], port_ranges:[{start,end}], allowed_routes:[cidrs]}]}`;
`PUT /api/policies/{id}`, `DELETE`.

Validation refusals (HTTP 400) and what they mean:

| Message | Cause | Fix |
|---|---|---|
| `for ALL or ICMP protocol ports is not allowed` | a rule with protocol `all` or `icmp` carries `ports` or `port_ranges` | remove the ports, or switch the rule to `tcp`/`udp` |
| `for ALL or ICMP protocol type flow can be only bi-directional` | a rule with protocol `all` or `icmp` has `bidirectional:false` | set `bidirectional:true`, or use `tcp`/`udp` with at least one port for a one-way rule |

Recipes:

- **Move from open mesh to least privilege:** create the needed policies first (they
  have no effect while Default exists), then disable/delete **Default**.
- **Servers reachable by developers on 22/443 only:** groups `developers`, `servers`;
  rule TCP, source `developers` → destination `servers`, one-way, ports `22,443`.
- **Block a compromised device:** remove it from all groups except All and make sure no
  policy uses All → All; or block its user (Team → Users) which disconnects its peers.

Access decisions are logged as `peer.access.granted` / `peer.access.blocked` (with the
policy, posture check and reason) — Activity → Events.

---

## 5. Routes and exit nodes (Network → Routes, `/network-routes`)

Requirements: routing peers are **Linux** peers (the selector lists only Linux); they
must reach the target network; masquerade is on by default (turn off only if the target
network routes `100.64.0.0/10` back to the routing peer).

Create Route: **Route Type** Network Range (`172.16.0.0/16`) or Domains (list; "Keep
Routes" retains previously resolved IPs; forces masquerade); **Routing Peer** (single
Linux peer) or **Peer Group** (Linux peers → automatic HA); **Distribution Groups** (who
receives the route); **Policy Groups (Optional)** (`access_control_groups`, used by
policies' Routes field); **Network Identifier** (≤40 chars; routes with the same
identifier form one network for HA); Description; **Enable Route**; **Masquerade**;
**Metrics** 1–9999 (lower = preferred, default 9999).

HA: add more routing peers to the same network (**Add Peer** in the High Availability
column) or use a peer group with several Linux peers. Clients pick by metric and
connection quality; users can pin with `netzilo routes select`.

Exit node (Internet egress): Peers → Linux peer → ⋮ → **Add Exit Node** (or Routes →
**Add Exit Node**) → distribution groups. Creates route `0.0.0.0/0`. IPv6 default
routes are blocked. Pair with a DNS server (no match domains) for the same groups so
DNS also leaves via the exit node.

Policies still apply: the client's group must be allowed to reach the routing peer's
group for the routed protocol/ports. Use **Policy Groups** + rule **Routes** to restrict
which CIDRs a group may reach through the router.

Update modal cannot change the CIDR/domains or identifier — delete and recreate.
Deleting the network deletes all its routes.

API: `POST /api/routes` `{network_id, description, enabled, peer | peer_groups:[id], network | domains:[…], keep_route, metric, masquerade, groups:[dist], access_control_groups:[…]}`.

Validation refusals (HTTP 400): `only one of 'peer' or 'peer_groups' should be provided`
and `either 'peer' or 'peers_group' should be provided` (exactly one routing source);
`only one of 'network' or 'domains' should be provided` and `either 'network' or
'domains' should be provided` (exactly one target); `metric should be between 1 and 9999`;
`identifier should be between 1 and 40 characters`; `invalid Prefix` (the CIDR does not
parse). Each names the field to fix.

Kubernetes routing peers: ephemeral reusable key with auto-group → Deployment (3
replicas, `NET_ADMIN`, `SYS_ADMIN`, `SYS_RESOURCE`) → route via that peer group.

---

## 6. DNS (Network → DNS Servers `/dns/nameservers`, DNS Settings `/dns/settings`)

Every peer gets `<dns-label>.<dns-domain>` (self-hosted servers use `netzilo.network`
from the management `--dns-domain` flag; cloud uses `netzilo.network`). The client runs a
local resolver that answers peer names and forwards other queries to the nameserver
groups distributed to it.

Add DNS Server: template (Google `8.8.8.8/8.8.4.4`, Cloudflare `1.1.1.1/1.0.0.1`, Quad9
`9.9.9.9/149.112.112.112`) or Custom; up to **3** servers (IP + port, UDP);
**Distribution Groups**; **Enable DNS Server**; **Match Domains** (split DNS — leaving it
empty makes the group the *primary* resolver for all other names); **Mark match domains
as search domains** (`host` instead of `host.corp.example.com`); Name/Description.

Rules: match-domain groups work on macOS, Windows 10+, and Linux with systemd-resolved;
always provide one primary group (no match domains) for `All`. A private resolver behind
a routing peer needs a route to it and a policy allowing UDP 53 from the clients' group
to the routing peer's group.

DNS Settings: **Disable DNS management for these groups** — peers in those groups keep
their own OS DNS (`disabled_management_groups`).

API: `POST /api/dns/nameservers` `{name, description, nameservers:[{ip, ns_type:"udp", port}], enabled, groups, primary, domains, search_domains_enabled}`; `PUT /api/dns/settings` `{disabled_management_groups}`.

Validation refusals (HTTP 400) — `primary` and `domains` are mutually exclusive, and the
messages say so:

| Message | Cause | Fix |
|---|---|---|
| `nameserver group primary status is true and domains are not empty, you should set either primary or domain` | `primary:true` together with match domains | either clear `domains` (primary resolver) or set `primary:false` (split DNS) |
| `nameserver group primary status is false and domains are empty, it should be primary or have at least one domain` | neither primary nor any match domain | add a domain, or make it primary |
| `nameserver group primary status is true and search domains is enabled, you should not set search domains for primary nameservers` | `search_domains_enabled:true` on a primary group | turn search domains off, or make the group a match-domain group |
| `the list of nameservers should be 1 or 3, got <n>` | 0, 2 or more than 3 servers | provide one or three |
| `nameserver group got an invalid domain: <domain> …` / `the list of group IDs should not be empty` / `a nameserver group with name <name> already exist` | malformed domain; no distribution group; duplicate name | fix the named field |

Test from a peer: Linux `resolvectl query peer-a.netzilo.network` / `dig`, macOS
`dscacheutil -q host -a name peer-a.netzilo.network`, Windows `Resolve-DnsName peer-a.netzilo.network`.

---

## 7. Posture checks (Endpoint → Posture Checks, `/posture-checks`)

A check is a named bundle of conditions evaluated on the **source** peer; attach it to
policies (and to profiles / Edge filters). Free-plan tenants cannot create/edit checks
("Upgrade Plan"); self-hosted Enterprise/MSP can. A check cannot be deleted while any
policy, profile or filter uses it: `DELETE /api/posture-checks/{id}` answers HTTP 412
`posture checks have been linked to policy: <policy name>` — detach it from the named
policy (Posture Checks tab) and retry; the dashboard disables the delete control instead.

| Card | Field | Semantics |
|---|---|---|
| Netzilo Client Version | `nb_version_check.min_version` | minimum client version (semver) |
| Country & Region | `geo_location_check {locations[{country_code, city_name}], action allow\|deny}` | by public IP via GeoLite2; **allow** list blocks everything else, **block** list allows everything else; requires the server's geo DB |
| Date & Time (Netzilo) | `date_time_checks.rules[]` | time windows with recurrence (daily/weekly/monthly), start/end dates, timezone |
| Peer Network Range | `peer_network_range_check {ranges[], action}` | source IP ranges (CIDR) |
| Operating System | `os_version_check {linux,windows:{min_kernel_version}; darwin,ios,android:{min_version}}` | per-OS allow all / ≥ version / block (omitted key = blocked) |
| Peer Domain Membership (Netzilo) | `netzilo_check.peer_domain_check {action, domains}` | AD/domain-joined check |
| Endpoint Security Settings (Netzilo) | `netzilo_check.security_settings_check {antivirus_check (Win), firewall_check (Win/mac), disk_encryption_check, screen_lock_check, os_updates_check}` | all enabled items must pass |
| Advanced Endpoint Settings (Netzilo) | `netzilo_check.advanced_settings_check {netzilo_workspace_check (Win), netzilo_browser_check (Win/mac), virtual_device_check, device_integrity_check, registry_check{action all\|any, registry[{dir HKLM…,key,value}]}, file_folder_check{action, check{windows\|darwin\|linux:[{path,content}]}}, processes_check{action, check{…:[paths]}}}` | regex in key/path/content |

Attach: Policies → policy → **Posture Checks** tab → **Browse Checks** / **New Posture
Check** → choose **All** or **Any** evaluation → Save. Failures show as
`peer.access.blocked` events with the check name and reason.

API: `POST /api/posture-checks` `{name, description, checks:{…}}`; countries/cities for
geo: `GET /api/locations/countries`, `GET /api/locations/countries/{cc}/cities`.

---

## 8. Activity, reports, integrations

**Activity → Events** (`/activity`): server-side paginated (`GET /api/events/paginated?limit&offset&user=<email>&code=…&date_from&date_to&q=`), default last 14 days, 25 rows. Filters: date range, event types (grouped by category: Administration, Access Control, Data Exfiltration, Policy Violation, Suspicious, Investigation, AI Edge), user (incl. "Netzilo System"). Keyword search is BM25 ranked; with an OpenAI/Anthropic integration the sparkle button runs **AI Smart Search** and stores the answer as an `ai.insight` event. **Download CSV** exports the *current page* (Timestamp, User, Email, Event code, Source, Target, More Information). Event rows for `session.recorded` play recordings; `aidr.graph` opens the session snapshot; events with a kill chain open **Kill Chain**.

Key event codes: `user.peer.add`, `setupkey.peer.add`, `peer.remove`, `peer.rename`,
`peer.login.expire`, `peer.access.granted/blocked`, `policy.add/update/remove`,
`group.add/update/delete`, `route.add/update/remove`, `nameserver.group.*`,
`setupkey.add/revoke/overuse/deleted`, `user.invite/join/block/unblock/delete`,
`user.login/failedlogin/logout` (imported from the IdP), `account.setting.*`,
`profile.*`, `tool.*`, `scanner.*`, `filter.*`, `semantic.event`, `aidr.graph`,
`browser.*`, `workspace.*`, `session.recorded`, `report.*`.

**Activity → Reports** (`/reports`): **Create Report** → type **User Activity**,
**Authentication Activity**, or **AI Activity** → date range → groups (or all) →
generated as PDF; view/download/delete. Contains sensitive data — restrict access.

**Integrations** (`/integrations`, admins; Free plan sees "Upgrade Plan"):

| Tab | Card | Purpose | Config |
|---|---|---|---|
| Event Streaming | Amazon S3 | stream every event as a JSON object to a bucket (also enables workspace recording storage) | region, bucket, access key, secret (IAM needs `s3:PutObject`, `s3:PutObjectAcl` on the bucket) |
| Event Streaming | Min.io | same, S3-compatible | endpoint, bucket, access key, secret |
| Networking | Twilio / Cloudflare | managed TURN instead of the built-in relay | account SID + auth token / token id + API token |
| Networking | TURN/STUN Servers | your own STUN/TURN (`static`) with a browser-side **Test Connection** | STUN `host:port` UDP/TCP; TURN `host:port` UDP/TCP/DTLS/HTTPS + username/password |
| Artificial Intelligence | OpenAI / Anthropic | AI Smart Search, AI rule generation, discovered-tool risk analysis | API key, usage Assistant / Log Analysis / All |

Only one of Twilio / Cloudflare / static TURN can be active. Disabling an integration
deletes its settings.

**Dashboard home** (`/dashboard`): Security Score (A ≥ 80 … F < 20, computed from peer
posture), Users, Agents (AI agent applications seen in 7 days), Devices, AI Activity
(top agents/models, policy violations), OS and score distribution.

---

## 9. Multi-tenant / self-service (cloud and MSP servers)

Tenants are subdomains of the dashboard host. `/login` on `acme.<base>` looks up the
organization; unknown subdomains show **No Such Organization**. `/register` (base
domain, reCAPTCHA-protected) creates a company subdomain + owner. Settings → Tenant shows
Tenant Name, Tenant ID (for support), Company Logo upload (PNG/JPG/SVG ≤ 500 KB), and
**Delete Tenant** (irreversible; removes peers, users, groups, policies, routes; logging in
again creates a fresh account).

Plans (Settings → Plans & Billing, owner only; hidden on MSP/self-hosted Enterprise):
Free (5 users / 100 peers), Professional, Enterprise (14-day trial; Enterprise required
for Profiles and premium scanners). Counts refresh daily.
