---
id: '20'
title: Admin Skill — Policies (Access Control)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 10192
sections:
- id: '1'
  title: Model
  chars: 1281
- id: '2'
  title: Field reference (Add / Update Access Control Policy)
  chars: 3003
- id: '3'
  title: API
  chars: 1025
- id: '4'
  title: Procedures
  chars: 1894
- id: '5'
  title: Semantics you must get right
  chars: 951
- id: '6'
  title: Diagnosis — "why can't A reach B / why can A reach B?"
  chars: 1651
---
# Admin Skill — Policies (Access Control)

**Dashboard:** Network → **Policies** (`/access-control`). **API:** `/api/policies`.
**Who:** owners and admins (users see "You don't have access to Policies").

Policies are the only thing that lets two peers talk. This skill covers the model, every
field, safe change procedures, and how to prove why a connection is or is not allowed.

---

## 1. Model

- A **policy** is a named, enable-able container with one or more **rules** and optional
  **posture checks** that gate the *source* peer.
- A **rule** allows traffic from **Source** groups to **Destination** groups for a
  **Protocol**, optionally limited to **Ports** and (for routed traffic) **Routes**.
- Rules are **allow-only**. There is no deny rule and no ordering; the union of all
  enabled rules is what is permitted. Anything not matched is dropped by the client's
  firewall on the initiating side.
- A new account has one policy, **Default**: `All → All`, protocol ALL, bidirectional,
  no posture checks. While it is enabled every peer can reach every peer on every port,
  so **new restrictive policies have no visible effect until Default is disabled or
  deleted**.
- The group **All** contains every peer and cannot be edited.
- Enforcement point: the peer that initiates the connection checks its outbound rules;
  the receiving peer accepts inbound traffic over the tunnel. Consequence: after a change
  the *source* peers must have received the new network map (within ~30 s, or
  `netzilo refresh`).
- Rules also generate **audit events**: `peer.access.granted` (which policy) and
  `peer.access.blocked` (which posture check and reason).

---

## 2. Field reference (Add / Update Access Control Policy)

Header text: "Use this policy to restrict access to groups of resources."

**Policy tab** — one accordion entry per rule, header shows `ALLOW <PROTOCOL>`, source
summary, direction arrow, destination summary, `Ports: …` / `Routes: …`.

| Field | Help text in UI | Values / rules |
|---|---|---|
| Protocol | "Allow only specified network protocols. To change traffic direction and ports, select TCP or UDP." | `ALL`, `TCP`, `UDP`, `ICMP`. ALL and ICMP force bidirectional and clear ports. |
| Source / Destination | group selectors | one or more groups each; typing a new name + Enter creates the group on save; `All` allowed |
| Direction (arrows between Source and Destination) | — | both directions (green), or one-way (blue). One-way requires TCP/UDP **and at least one port**. |
| Ports | "Allow network traffic and access only to specified ports. Select ports between 1 and 65535." | single ports or ranges `start-end`; empty = all ports (bidirectional only) |
| Routes | "Allow network traffic and access only to specified targets. Enter IP addresses e.g. 192.168.1.1/16 or 192.168.2.34" | CIDRs; restricts which **routed** destinations this rule may reach through a routing peer; empty = any |
| Rule menu ⋮ | — | Duplicate, Move Up, Move Down, Delete |
| Add Rule | — | adds another rule to the same policy |
| Enable Policy | "Use this switch to enable or disable the policy." | disables the policy and all its rules |

The view toggle (top right) switches to **Policy Rules (JSON Format)**: an array of
`{protocol, sources, direction, destinations, ports, routes}` with `direction` ∈
`IN|OUT|BOTH`. Validation messages: "JSON must be an array of rule objects", "Rule n:
Missing required fields (protocol, sources, direction, destinations)", "Rule n: Invalid
protocol …", "Rule n: Invalid direction …", "Rules must have both sources and
destinations", "TCP/UDP unidirectional rules must specify ports". Use the JSON view for
bulk edits; verify direction with a real test afterwards, because the JSON `IN`/`OUT`
labels are the reverse of the arrows shown in the visual editor.

**Posture Checks tab** — Browse Checks / New Posture Check; when ≥1 check is attached,
**Posture Check Evaluation**: "Choose whether all posture checks must pass or if any one
set can pass" → **All** (default) or **Any**.

**Name & Description tab** — name (required; UI label "Name of the Rule"), description.

Create flow buttons: Policy → Continue → Posture Checks → Continue → Name → **Add
Policy**. Edit: **Save Changes** on any tab. Continue is disabled until every rule has
≥1 source, ≥1 destination and (one-way TCP/UDP) ≥1 port.

**Table** (`/access-control`): Name (green dot = enabled), Active toggle (disables policy
and all rules), Sources, Destinations, Rules (count), Posture Checks (badge or "Add
Posture Check"), Delete. Filters All/Active/Inactive, source/destination group filters,
search "policies, rules, groups, ports, routes".

---

## 3. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET  /api/policies
POST /api/policies
GET/PUT/DELETE /api/policies/{id}
```
Body:
```json
{"name":"dev-to-servers","description":"","enabled":true,
 "any_check_must_pass":false,"source_posture_checks":["<check-id>"],
 "rules":[{"name":"ssh-https","description":"","enabled":true,"action":"accept",
           "protocol":"tcp","bidirectional":false,
           "sources":["<group-id>"],"destinations":["<group-id>"],
           "ports":["22","443"],"port_ranges":[{"start":8000,"end":8100}],
           "allowed_routes":["10.20.0.0/16"]}]}
```
`PUT` replaces the whole policy: `GET` → modify → `PUT`. Groups are referenced by ID
(`GET /api/groups`). `protocol` ∈ `all|tcp|udp|icmp`; `action` is always `accept`.

---

## 4. Procedures

### 4.1 Move from open mesh to least privilege (safe order)
1. Inventory who needs what (Activity → Events, `peer.access.granted` shows real flows;
   Reports → User Activity → Top Targets).
2. Create groups per role/resource (Peers → Assigned Groups, or setup-key auto-groups,
   or user auto-groups with group propagation).
3. Create the specific policies. They are inert while Default is enabled.
4. Pick a pilot group, create a **temporary** broad policy for everyone else
   (`All → All` minus the pilot is not expressible; instead keep Default enabled and test
   the pilot rules for correctness with the API resolution in §6).
5. Disable **Default** (Active toggle) during a low-traffic window. Watch
   `peer.access.blocked` events and helpdesk for 24 h. Re-enable Default to roll back.
6. Delete Default once stable.

### 4.2 Allow one service
Rule: protocol TCP, Source = consumer group, Destination = server group, one-way arrow
from source to destination, Ports = the service port(s). Attach posture checks if the
consumers are laptops.

### 4.3 Server-to-server within a group
Rule with the same group as Source and Destination, protocol ALL or the needed ports.

### 4.4 Allow ping for troubleshooting
Rule protocol ICMP (bidirectional by definition) between the groups; remove later if
not desired.

### 4.5 Restrict what a routed network exposes
Use the rule's **Routes** field (CIDRs inside the route's network) and the route's
**Policy Groups**; see `22-network-routes-and-exit-nodes.md` §4.

### 4.6 Emergency isolation of a device
Remove it from every group except All and make sure no enabled rule uses All as a
destination that matters; or block its user (Team → Users → Block) which disconnects all
of that user's peers; or delete the peer.

### 4.7 Time-boxed access
Attach a **Date & Time** posture check (`21-posture-checks.md`) to the policy.

---

## 5. Semantics you must get right

- **Bidirectional** with ports: either side may initiate on those ports.
- **One-way**: only the source may initiate; return traffic is allowed automatically.
- **ALL/ICMP** cannot be one-way or port-limited.
- **Ports apply to the destination port** of the connection.
- **Routes** in a rule only matter for traffic that leaves through a routing peer; they
  do not restrict peer-to-peer traffic.
- **Posture checks** apply to the **source** peer of every rule in the policy; with
  **All** every check must pass, with **Any** one is enough. A failing check blocks *all*
  rules of that policy for that peer and logs `peer.access.blocked`.
- Disabling a policy disables all rules; disabling a single rule is possible via API
  (`enabled:false` on the rule) and in the JSON view.
- Group deletion is refused while a policy references the group.
- Free-plan tenants can create policies but not posture checks.

---

## 6. Diagnosis — "why can't A reach B / why can A reach B?"

1. **Are both peers in the groups you think?** Peers → peer → Assigned Groups (or
   `GET /api/peers`, `GET /api/groups`).
2. **Resolve the rules programmatically** — the exact query is in
   `11-connectivity-diagnosis.md` §3; it prints every enabled rule whose sources cover A's
   groups and destinations cover B's groups (or the reverse for bidirectional rules).
3. **No rule** → create/adjust. **Rule but wrong protocol/ports** → the symptom is
   "ping works but the port does not" (or vice versa). **Rule with posture checks** →
   `GET /api/events/paginated?code=peer.access.blocked&q=<A>` shows the failing check and
   reason.
4. **Default still enabled?** Then everything is allowed and a "policy not working" report
   is really "Default masks it".
5. **Change not applied yet** → `netzilo status -d` on A must list B; `netzilo refresh`.
   Peers receive updates within ~30 s.
6. **Routed destination** → additionally validate the route and the routing peer
   (`22-network-routes-and-exit-nodes.md` §6); a rule's Routes field can exclude the target.
7. **Unexpected access** → search `peer.access.granted` events for the pair; the event
   names the policy that granted it. Check for broad rules using `All`, duplicate policies,
   and bidirectional rules that were meant to be one-way.

Common mistakes: one-way rule with the arrow pointing the wrong way (recreate with the
arrow from consumer to server and test); ports typed in the Routes field; expecting a
deny (does not exist — remove the allow instead); testing from a peer whose login
expired (`Login required` badge).
