---
id: '23'
title: Admin Skill — DNS Management
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 6826
sections:
- id: '1'
  title: Model
  chars: 1359
- id: '2'
  title: Field reference
  chars: 1226
- id: '3'
  title: API
  chars: 871
- id: '4'
  title: Procedures
  chars: 1329
- id: '5'
  title: Diagnosis
  chars: 1667
---
# Admin Skill — DNS Management

**Dashboard:** Network → **DNS Servers** (`/dns/nameservers`) and **DNS Settings**
(`/dns/settings`). **API:** `/api/dns/nameservers`, `/api/dns/settings`.

Netzilo gives every peer a name and can push resolvers to peers. This skill covers the
built-in peer DNS, nameserver groups, split DNS, search domains, exclusions, and
diagnosis.

---

## 1. Model

- Every peer has a **DNS label** (its name, unique, numeric suffix on collisions) under
  the network domain: `<label>.netzilo.network` (self-hosted servers use the domain set
  at installation; the default is `netzilo.network`). Resolution is served by a local
  resolver inside the client on each peer.
- A **nameserver group** (called **DNS Server** in the UI) is up to **3** upstream
  servers (IP + port, UDP) plus **distribution groups** (which peers receive it),
  optional **Match Domains** (split DNS) and **Mark match domains as search domains**.
- **No match domains** = the group is the peer's **primary** resolver for everything
  that is not a Netzilo name.
- **With match domains** = only those domains go to these servers (split DNS). Works on
  macOS, Windows 10+, and Linux with systemd-resolved; other Linux resolvers cannot do
  per-domain routing, so always ship one primary group for `All`.
- **Search domains**: with `example.corp` marked as search domain, `ping host-a` resolves
  `host-a.example.corp`.
- **DNS Settings → Disable DNS management for these groups**: peers in those groups keep
  their OS DNS untouched (no peer names, no pushed resolvers).
- Resolvers that live in a private network need a **route** to them and a **policy**
  allowing UDP/TCP 53 from the clients' group to the routing peer's group.

---

## 2. Field reference

**Add DNS Server** → template chooser: **Google DNS** (8.8.8.8, 8.8.4.4), **Cloudflare
DNS** (1.1.1.1, 1.0.0.1), **Quad9 DNS** (9.9.9.9, 149.112.112.112), **Custom DNS**.

Tabs:

| Tab | Field | UI help / rule |
|---|---|---|
| DNS Server | IP (prefix "IP") + Port (prefix "Port", default 53) | up to 3; "Please enter a valid IP"; **Add DNS Server** button disabled at 3 |
| DNS Server | Distribution Groups | "Advertise this DNS server to peers that belong to the following groups" — ≥1 required |
| DNS Server | Enable DNS Server | "Use this switch to enable or disable the DNS server." |
| Domains | Match Domains | "Add domain if you want to have a specific one resolved by this nameserver." |
| Domains | Mark match domains as search domains | "E.g., 'peer.example.com' will be accessible with 'peer'" — only available when match domains exist |
| Name & Description | DNS Name | "Enter a name for this nameserver." ≤40 chars |

Table: Name, Active toggle, Match Domains, DNS Servers (IP badges), Distribution Groups,
Delete. Filter Enabled/All.

**DNS Settings**: "Disable DNS management for these groups" — "Peers in these groups will
require manual domain name resolution" → Save Changes.

---

## 3. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/dns/nameservers ; GET/PUT/DELETE /api/dns/nameservers/{id}
GET/PUT /api/dns/settings
```
```json
{"name":"Office resolver","description":"",
 "nameservers":[{"ip":"192.168.0.32","ns_type":"udp","port":53}],
 "enabled":true,"groups":["<group-id>"],
 "primary":false,"domains":["berlinoffice.corp"],"search_domains_enabled":true}
```
`primary` must be `true` when `domains` is empty and `false` otherwise;
`search_domains_enabled` may only be true when `domains` is non-empty.
DNS settings body: `{"disabled_management_groups":["<group-id>"]}`.

---

## 4. Procedures

### 4.1 Baseline for every account
One **primary** group (no match domains) for `All`, e.g. Cloudflare or the corporate
resolver. Without it, peers whose OS cannot do split DNS have no working resolver for
Netzilo names on some platforms.

### 4.2 Split DNS for an office/VPC domain
Custom DNS: internal resolver IP (reachable via a route), distribution group
`employees`, Match Domains `corp.example.com`, search domain on. Add route to the
resolver's subnet and policy `employees → <router group>` UDP 53 (and TCP 53).

### 4.3 Exit-node users
Add a primary group (no match domains) for the exit-node distribution group so all DNS
leaves via the exit node; otherwise local DNS may be unreachable or leak location.

### 4.4 Exclude servers from DNS management
DNS Settings → add the `servers` group. Those peers keep their own resolv.conf/NRPT;
they cannot resolve peer names.

### 4.5 Rename a peer / fix a collision
Peers → peer → pencil → new name; the preview shows the resulting DNS label (lowercase,
punycode; duplicates get `-1`, `-2`).

### 4.6 Test on a peer
Linux `resolvectl query host.netzilo.network` or `dig host.netzilo.network`; macOS
`dscacheutil -q host -a name host.netzilo.network`; Windows
`Resolve-DnsName host.netzilo.network`. `netzilo status` shows `Nameservers: n/m Available`.

---

## 5. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| `Nameservers: 0/1 Available` on a peer | upstream unreachable through the tunnel (route/policy for port 53 missing), or resolver down | test `dig @<resolver-ip> example.com` from the peer; add route/policy |
| Peer names never resolve | peer is in a disabled-management group; OS resolver integration failed (`07-client-troubleshooting.md` §6); on Linux `/etc/resolv.conf` overwritten by another tool | check DNS Settings; check backend; `broken params in resolv.conf, repairing it...` in log |
| Internal names resolve to public IPs | split-DNS group missing the domain, or the OS ignores match domains | add domain; ship a primary group |
| Only some peers resolve internal names | distribution groups | add the group |
| `the DNS manager of this peer doesn't support custom port. Disabling primary DNS setup.` | something else owns port 53 on the peer | free port 53 or `netzilo up --dns-resolver-address 127.0.0.1:5053` where the OS resolver supports custom ports |
| Search domain ignored | toggle off, or no match domains | enable "Mark match domains as search domains" |
| Save fails: "Name should be less than 40 characters" / invalid IP | validation | fix |
| Peers lose DNS after `netzilo down` or crash | client restores OS DNS on shutdown; unclean shutdown repaired on next start | `sudo netzilo service restart`; macOS `service uninstall` cleans stale entries |
| Domain routes not following DNS changes | resolved every minute; "Keep Routes" retains old IPs | wait; adjust interval on clients |

Events: `nameserver.group.add/update/delete`, `dns.setting.disabled.management.group.add/delete`.
