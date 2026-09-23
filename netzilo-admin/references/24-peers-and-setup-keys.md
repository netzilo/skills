---
id: '24'
title: Admin Skill — Peers and Setup Keys
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 13833
sections:
- id: '1'
  title: Peer lifecycle
  chars: 1311
- id: '2'
  title: Peers page — field and action reference
  chars: 2304
- id: '3'
  title: Setup keys — reference
  chars: 2100
- id: '4'
  title: API
  chars: 1406
- id: '5'
  title: Procedures
  chars: 1520
- id: '6'
  title: Diagnosis
  chars: 3666
- id: '7'
  title: Limits that reject a change
  chars: 1081
---
# Admin Skill — Peers and Setup Keys

**Dashboard:** Endpoint → **Peers** (`/peers`, detail `/peer?id=`), Endpoint → **Setup
Keys** (`/setup-keys`). **API:** `/api/peers`, `/api/setup-keys`, `/api/groups`.

Peers are devices; setup keys are the pre-authentication credentials that enrol
devices without a user. This skill covers the peer lifecycle, every peer control, setup
key design, and diagnosis of enrolment and peer-state problems.

---

## 1. Peer lifecycle

| Stage | What happens | Admin control |
|---|---|---|
| Enrolment | device runs `netzilo up` with SSO (bound to a user), a **setup key** (no user; joins the key's auto-groups), or a PAT (bound to the token's user) | setup keys; user auto-groups; group propagation |
| Approval (Cloud) | with peer approval enabled a new peer shows **Approval required** and an admin clears it with **Approve**. Treat this as a review queue, not as a gate: **do not rely on peer approval to keep a device off the network**. To keep a device out, block its user or delete the peer | Peers → Approve; Block User; Delete |
| Active | connected/disconnected status, last seen, security posture | groups, SSH, login expiration, rename |
| Login expiration (SSO peers) | after the account's expiration period the peer needs re-login (**Login required** badge) | Settings → Authentication; per-peer toggle |
| Inactivity expiration (SSO peers) | idle peers are expired after the configured period | Settings → Authentication |
| Ephemeral (setup-key option) | peer is deleted 10 minutes after going offline | key setting |
| Deletion | peer removed; device must re-enrol | Delete / bulk delete; deleting a user deletes their peers |

Peer IPs come from `100.64.0.0/10`; the DNS label derives from the name.

---

## 2. Peers page — field and action reference

List columns: **Name** (green/gray dot = online/offline, owner e-mail; exit-node
indicator), **Security Score** (A–F), **Address** (DNS label + IP, copyable; hover: public
IP, domain, region), **Groups** (click → "Assigned Groups" modal), **Last seen**, **OS**,
**Version** ("Update available" tooltip when behind the latest release), status badges
(**Approval required** + **Approve**; **Expiration disabled**; red **Login required** —
"This peer is offline and needs to be re-authenticated because its login has expired."),
actions ⋮. Filters: All / Online / Offline, **Pending Approvals**, group selector,
search "by name, IP, owner or group".

Row actions: View Details; Enable/Disable **Login Expiration** (disabled for setup-key
peers: "Login expiration is disabled for all peers added with an setup-key."); Enable/
Disable **SSH Access** (confirm "Enable SSH Server for <name>? Experimental feature…");
Add Exit Node (Linux); **Delete** ("Are you sure you want to delete this peer?").

Multi-select bar: **Assign Groups** (add, or **Overwrite Existing Groups** which removes
previous groups; `All` is never touched), **Sync Peers** (forces connected peers to
re-sync; reports "n succeeded, m failed (not connected)"), **Delete All** (up to 1000).

Detail page (`/peer?id=`): rename (pencil; "Domain Name Preview" shows the resulting DNS
label), **Login Expiration** toggle ("Enable to require SSO login peers to
re-authenticate when their login expires."), **SSH Access** toggle ("Enable the SSH
server on this peer to access the machine via an secure shell."), **Assigned Groups**
(typing a new name + Enter creates a group), **Available Snapshots** (AI session
snapshots, admins), information card (Device ID, Netzilo IP, Public IP, Domain Name, AD
Domain Name, Hostname, Region, Operating System, Security Score with nine posture
indicators, Last seen, Agent Version, UI Version), and **Network Routes** for this peer
(Add Exit Node, Add Route → New Network Route / Existing Network).

Security Score indicators (tooltips): Firewall, Antivirus (active and up to date), Disk
Encryption, OS up to date, Virtual device, Screen locked, Device Integrity, Enterprise
Workspace, Enterprise Browser. Grades: A ≥ 80, B ≥ 60, C ≥ 40, D ≥ 20, F below.

---

## 3. Setup keys — reference

Page text: "Setup keys are pre-authentication keys that allow to register new machines
in your network."

**Create New Setup Key** ("Use this key to register new machines in your network"):

| Field | UI help | Semantics |
|---|---|---|
| Name | "Set an easily identifiable name for your key" | required |
| Make this key reusable | "Use this type to enroll multiple peers" | off = **one-off** (usage 1); on = **reusable** |
| Usage limit | "For example, set to 30 if you want to enroll 30 peers" | blank/0 = unlimited |
| This key expires | "Disable to create a key that never expires" | default on |
| Expires in | "Should be between 1 and 365 days." | default 7 days |
| Ephemeral Peers | "Peers that are offline for over 10 minutes will be removed automatically" | for autoscaling/containers |
| Auto-assigned groups | "These groups will be automatically assigned to peers enrolled with this key" | applies to peers enrolled **after** the change |

Success modal: "This key will not be shown again, so be sure to copy it and store in a
secure location."

Table: Name & Key (validity dot, first 5 chars + `****`), Usage (`x of N Peers` /
`One-off`), Last used, Groups (editable), Ephemeral badge, Expires (date or "Never"),
copy, Delete. Filter Valid / All. States: valid, overused, expired, revoked.

Facts: revoking/deleting/expiring a key **does not disconnect** peers already enrolled
with it; a one-off key is consumed by the first device; an ephemeral key marks peers
ephemeral for their lifetime; setup-key peers are exempt from login expiration and have
no owner (they appear as "Setup Key Peers" / "Serverless" in AI reports).

What a device sees when a key is refused (details and the activity fields in §6): a key
that **exists here but is expired, revoked or over-used** is refused with
`couldn't add peer: setup key is invalid`; a key **unknown to this server** (wrong server,
wrong URL, typo) is refused with `failed adding new peer: account not found`. The two are
told apart by that text alone — the dashboard shows nothing for the second case.

---

## 4. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET /api/peers ; GET /api/peers-stream (SSE) ; GET/PUT/DELETE /api/peers/{id}
POST /api/peers/bulk-delete {"peer_ids":[…]} ; POST /api/peers/sync {"peer_ids":[…]}
GET/POST /api/setup-keys ; GET/PUT/DELETE /api/setup-keys/{id}
GET/POST /api/groups ; GET/PUT/DELETE /api/groups/{id}
```
Peer update body: `{"name":"…","ssh_enabled":false,"login_expiration_enabled":true,"inactivity_expiration_enabled":false,"approval_required":false}`.
Setup key body: `{"name":"asg-web","type":"reusable","expirable":true,"expires_in":2592000,"revoked":false,"auto_groups":["<gid>"],"usage_limit":0,"ephemeral":true}` (seconds; 86400–31536000). Revoke: `PUT` with `"revoked":true`.
Group membership: `PUT /api/groups/{id} {"name":"…","peers":["<peer-id>", …]}`.

Peer read fields useful for reports: `connected`, `last_seen`, `last_login`,
`login_expired`, `login_expiration_enabled`, `approval_required`, `os`, `kernel_version`,
`version`, `ui_version`, `hostname`, `dns_label`, `ip`, `connection_ip`, `country_code`,
`city_name`, `serial_number`, `user_id`, `groups[]`, `meta.netzilo_meta.*` posture flags.

---

## 5. Procedures

### 5.1 Key strategy
| Use | Key |
|---|---|
| one server | one-off, 1–7 days, auto-group `servers` |
| fleet / IaC | reusable, usage limit = expected count, 30 days, auto-groups per role |
| autoscaling / Kubernetes / CI | reusable, **ephemeral**, usage unlimited, auto-group `k8s-routers` or `ci` |
| kiosk / shared device | reusable, no expiry (This key expires off), auto-group `kiosks` |
Rotate keys on a schedule (create new → update automation → delete old).

### 5.2 Enrol a user device without SSO prompts
Not possible with setup keys if the device must be tied to a user; use `netzilo deploy-user`
or a PAT (`05-client-install-and-deploy.md` §8.3).

### 5.3 Bulk group changes
Peers → select → Assign Groups (add) or Overwrite Existing Groups (replace). API: edit
each group's `peers` list.

### 5.4 Force re-authentication of everyone
Settings → Authentication → lower **Peer login expiration**; SSO peers must re-login
when their current period ends. Immediate: delete the peers (devices re-enrol on next
`netzilo up`) or block the users.

### 5.5 Approve pending peers (Cloud)
Peers → **Pending Approvals** → **Approve** per peer (`PUT … {"approval_required":false}`).
If a pending device should *not* be on the network, do not leave it pending: delete the
peer (and block its user if it was SSO-enrolled). Pending is a review state, not a block.

### 5.6 Clean stale peers
Filter Offline, sort by Last seen, multi-select → Delete All. API recipe in
`09-api-and-automation.md` §4.4.

---

## 6. Diagnosis

| Symptom | Cause | Check / fix |
|---|---|---|
| New device does not appear | wrong management URL on the client; key not known here or invalid; the device never finished `netzilo up` | `grep ManagementURL` in the client config; read the client's `login failed:` / `login backoff cycle failed:` text and use the two rows below; Pending Approvals (Cloud) |
| `login backoff cycle failed: rpc error: code = FailedPrecondition desc = couldn't add peer: setup key is invalid` (after ~30 s of retries) | the key **exists on this server** but is expired, revoked, or over its usage limit | Activity → Events → `user.failedlogin`: `auth_method: setup_key`, `setup_key_name`, `peer_hostname`, and `error_type` = `expired`, `revoked` or `over_used` (with `usage_limit`/`used_times`); `reason` reads `Setup key expired: <key>`, `Setup key revoked: <key>` or `Setup key usage limit exceeded: <key>`. Create a new key, or raise the limit on a reusable one |
| `login failed: rpc error: code = NotFound desc = failed adding new peer: account not found` (immediate) | the key is **not known to this server at all**: typo, a key from another server or tenant, or the client points at the wrong management URL | check the management URL on the device first; then create a key on the right server. Where the server can attribute the attempt to an account, `user.failedlogin` carries `error_type: key_not_found` and `reason: Setup key not found: <key>` |
| Device that was working shows **Needs login**, log has `… unrecoverable error: rpc error: code = PermissionDenied desc = peer is not registered` | the peer was **deleted on the server while the device was running** (delete, bulk clean-up, user deleted, ephemeral expiry) | re-enrol: `netzilo up` with SSO or a new setup key. Later automatic attempts show `no peer auth method provided…` until then (`13` §4.8) |
| `peer has been already registered` | two registrations of the same key crossed (`netzilo up` twice at once) | `netzilo status`; usually already registered. Otherwise `netzilo down` then `netzilo up` once |
| Peer shows **Login required** and users complain | login expiration period elapsed | user runs `netzilo up`; extend the period; for servers use setup keys |
| Peer keeps disappearing | enrolled with an **ephemeral** key and goes offline > 10 min | use a non-ephemeral key for permanent devices |
| Two entries for the same device | device re-enrolled after `netzilo down` or a Linux one-liner upgrade (which logs out) | delete the stale entry; upgrade by binary replacement |
| Cannot toggle login expiration | setup-key peer | by design |
| Duplicate name shows `-1` suffix | DNS label collision | rename |
| Groups assigned but policy not working | group propagation or policy issue | `20-policies-access-control.md` §6 |
| Version column says "Update available" | client older than latest release | upgrade (`05` §7) |
| Security score low / F | posture flags red on detail page | fix device settings; the score is informational unless a posture check uses those items |
| Bulk delete fails | > 1000 selected | batch |
| `rpc error: code = PermissionDenied desc = maximum number of personal peers reached` on the device | Free plan (100 peers) | upgrade or remove peers (`31` §2). Treat the plan as the cause **only** when this exact text is returned; any other refusal is one of the rows above |

Events: `user.peer.add`, `setupkey.peer.add`, `user.peer.delete`, `peer.rename`,
`peer.group.add/delete`, `peer.ssh.enable/disable`, `peer.login.expiration.enable/disable`,
`peer.login.expire`, `peer.approve`, `setupkey.add/update/revoke/overuse/deleted`,
`setupkey.group.add/delete`.

## 7. Limits that reject a change

| Setting | Accepted range | Message when out of range |
|---|---|---|
| Peer login expiration | one hour to 180 days | `peer login expiration can't be larger than 180 days`, or a message naming the one-hour floor |
| Setup key lifetime | 1 to 365 days | `expiresIn should be between 1 day and 365 days` |

**Login expiration cannot be changed on a setup-key peer.** Attempting it returns
`this peer hasn't been added with the SSO login, therefore the login expiration can't be
updated`. This is by design: setup-key peers have no user to re-authenticate. The
dashboard says the same thing in a tooltip on the disabled control. If a customer needs
periodic re-authentication on such a device, it must be re-enrolled through single
sign-on instead.

**Deleting a network deletes every route inside it.** The delete action on a network row
removes all of that network's routing-peer routes at once, not just one. The confirmation
says so. Deleting a single route uses the action on the inner row instead. See
`22-network-routes-and-exit-nodes.md`.
