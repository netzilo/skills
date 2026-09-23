---
id: '25'
title: Admin Skill — Users, Agents (Service Users), Groups and Account Settings
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 12285
sections:
- id: '1'
  title: Roles and visibility
  chars: 802
- id: '2'
  title: Users page — reference
  chars: 1343
- id: '3'
  title: Groups
  chars: 840
- id: '4'
  title: Account settings — reference
  chars: 2800
- id: '5'
  title: API
  chars: 1273
- id: '6'
  title: Procedures
  chars: 930
- id: '7'
  title: Diagnosis
  chars: 1706
- id: '8'
  title: Rules that refuse a change, and why
  chars: 2036
---
# Admin Skill — Users, Agents (Service Users), Groups and Account Settings

**Dashboard:** Team → **Users** (`/team/users`), Team → **Agents** (`/team/service-users`),
user detail (`/team/user?id=`), **Settings** (`/settings`: Authentication, Groups,
Permissions, Plans & Billing, Tenant). **API:** `/api/users`, `/api/users/{id}/tokens`,
`/api/groups`, `/api/accounts/{id}`, `/api/tenant`.

Identity-provider tasks (passwords policies, MFA enforcement, SSO federation, SMTP) are
in `04-identity-and-sso.md`; this skill is the Netzilo-account side.

---

## 1. Roles and visibility

| Role | Can | Cannot |
|---|---|---|
| **Owner** (one per account) | everything, incl. Plans & Billing, Tenant (logo, delete tenant), transfer ownership | — |
| **Admin** | all administration | owner-only items above |
| **User** | `/workplace` portal (apps, devices, tools), own profile & access tokens; sees only own peers and what policies allow | any admin page ("You don't have access to …") |
| **Agent** (service user) | API access with the role given (`user` = read, `admin` = write) | interactive login |

**Disable portal access for regular users** (Settings → Permissions) sends users to
`/install` instead of `/workplace`.

Transferring ownership: Team → Users → user → User Role → Owner → confirm "Transfer
Ownership?" — the current owner becomes Admin.

---

## 2. Users page — reference

Text: "Manage users and their permissions. Same-domain email users are added
automatically on first sign-in."

Columns: Name (avatar; "You"; clock icon = invited, ban icon = blocked; e-mail), Role
(Owner/Admin/User), Status (Pending = invited, Blocked, Active), Groups (auto-groups),
**Block User** toggle (not for self/owner), Last Login, Delete (not for self/owner;
"Deleting this user will remove their devices and remove dashboard access.").

**Add User** modal: name (first and last name required), e-mail, role (Owner hidden),
**Auto-assigned groups** ("Groups will be assigned to peers added by this user."),
**Email invitation** (default; needs SMTP on the identity provider) or **Create
password** (rule: ≥8 chars, upper, lower, digit, one of `@$!%*?&`; credentials shown
once; user must change at first login).

User detail: Name (editable), E-Mail, Status, Block User, Last login, **MFA** (Active →
**Reset MFA**, or Not Enrolled), **Auto-assigned groups**, **User Role**, **Password →
Change Password**, **Save Changes** (asks "Would you like to apply group change to
user's peers?"), **Access Tokens** (own profile or Agents only): name, expires in 1–365
days; token shown once.

Agents page: "Use agents to create API tokens and avoid losing automated access." →
**Create Agent**: name, role.

---

## 3. Groups

- Created implicitly wherever a group selector accepts a typed name + Enter, or via
  `POST /api/groups`.
- Membership sources: manual (Peers), setup-key auto-groups (new peers), user
  auto-groups → user's peers (**Enable user group propagation**), JWT claims (**Enable JWT
  group sync**, name-matched to existing groups; never created), integrations.
- **Settings → Groups** table: usage counts across Setup Keys, Peers, DNS, Access
  Controls, Network Routes, Users, Profiles, Filters; **Delete** only when unused
  ("Remove dependencies to this group to delete it."). `All` is immutable.

Naming guidance: role groups (`developers`, `finance`), resource groups (`dc-routers`,
`prod-db`), platform groups (`windows-laptops`), AI groups (`ai-users`, `agents`). Keep
names stable — JWT sync and scripts match by name.

---

## 4. Account settings — reference

| Tab | Setting | UI help | Field |
|---|---|---|---|
| Authentication | **Peer login expiration** | "Request periodic re-authentication of peers registered with SSO." | `peer_login_expiration_enabled` |
| Authentication | Expires in (1–180, Days/Hours) | "Time after which every peer added with SSO login will require re-authentication" | `peer_login_expiration` (seconds; default 24 h) |
| Authentication | **Peer inactivity expiration** + Expires in | "Expire inactive peers automatically" / "Time after which peer is expired" | `peer_inactivity_expiration_enabled`, `peer_inactivity_expiration` |
| Groups | **Enable user group propagation** | "Allow group propagation from user's auto-groups to peers, sharing membership information." | `groups_propagation_enabled` |
| Groups | **Enable JWT group sync** | "Sync groups from JWT claims to the user's auto-groups, granting and revoking membership as the claim changes. Only groups that already exist in Netzilo are matched — groups are never created from a token." | `jwt_groups_enabled` |
| Groups | JWT claim | "Specify the JWT claim that carries the user's group names, e.g., roles or groups…" | `jwt_groups_claim_name` |
| Groups | JWT allow group | "Limit access to Netzilo for the specified group name… To use the group, you need to configure it first in your IdP." Warning: "To prevent losing access, ensure you are part of this group." | `jwt_allow_groups` |
| Permissions | **Disable portal access for regular users** | "Access to the application portal(i.e. /workplace) will be disabled for non-admin users." | `regular_users_view_blocked` |
| Permissions | **Allow regular users to use the AI Assistant** + **Allowed groups** | "Admins always have the AI Assistant. When enabled, regular users in the groups below also get it on the Workplace page, for their own devices." | `user_ai_assistant_enabled` (boolean) and `user_ai_assistant_groups` (group ids). Both are needed: the switch on and the user in one of the groups; an empty list admits nobody. The server reports the outcome per user as `permissions.ai_assistant` on the user record (`GET /api/users?self=true` for the user themselves). A regular user admitted this way works with their own permissions — see `39-end-user-self-service.md` |
| Plans & Billing (owner; hidden on self-hosted/MSP) | current plan, usage, Upgrade/Downgrade, payment portal | Free 5 users/100 peers; Professional; Enterprise (Profiles, premium scanners) | `POST /api/tenant/subscription` |
| Tenant (owner) | **Company Logo** (PNG/JPG/SVG ≤ 500 KB), Tenant Name, **Tenant ID** (for support), **Delete Tenant** (irreversible) | | `/api/tenant/logo`, `DELETE /api/accounts/{id}` |

Cloud only: peer approval (`extra.peer_approval_enabled`), acted on per peer.

---

## 5. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET /api/users[?service_user=true|false] ; POST /api/users ; GET/PUT/DELETE /api/users/{id}
PUT /api/users/{id}/password ; PUT /api/users/{id}/name ; POST /api/users/{id}/invite
GET/DELETE /api/users/{id}/auth-factors
GET/POST /api/users/{id}/tokens ; GET/DELETE /api/users/{id}/tokens/{tid} ; POST /api/tokens/revoke
GET/POST /api/groups ; GET/PUT/DELETE /api/groups/{id}
GET /api/accounts ; PUT /api/accounts/{id} {"settings":{…}} ; DELETE /api/accounts/{id}
GET/PUT /api/tenant
```
Create user: `{"email":"j.doe@example.com","name":"Jane Doe","role":"user","auto_groups":["<gid>"],"is_service_user":false,"password":"…","password_change_required":true}` (omit password to invite by e-mail).
Update user: `{"role":"admin","auto_groups":[…],"is_blocked":false,"update_peer_groups":true}`.
Agent: `{"name":"automation","role":"admin","auto_groups":[],"is_service_user":true}`, then `POST /api/users/{id}/tokens {"name":"ci","expires_in":90}` → `plain_token`.

---

## 6. Procedures

- **Onboard a team**: create groups → create users (invite or password) with auto-groups
  → enable group propagation → policies per group. With SSO, rely on same-domain
  auto-join and JWT group sync.
- **Offboard**: Block User first (immediate, reversible: peers disconnected), then Delete
  (removes peers; on self-hosted also the identity-provider user). Rotate any Agent
  tokens the person knew.
- **Least-privilege admins**: keep one Owner, few Admins; use Agents with `user` role for
  read-only automation.
- **Restrict who can log in at all**: JWT allow group (put admins in it first) or the
  identity provider's own assignment.
- **Session hygiene**: Peer login expiration 8–24 h for laptops; inactivity expiration for
  contractors; setup keys for servers.
- **Rebrand**: Settings → Tenant → Company Logo (also shown on the login page on
  self-hosted when the identity provider has no logo).

---

## 7. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Invited user never gets the e-mail | identity provider has no SMTP (self-hosted default) | configure SMTP (`04` §6) or use Create password |
| "If a user already has a Netzilo account, you can't invite them" | e-mail already exists | they log in; same-domain auto-join |
| User logs in but sees only Workplace | role `user` | change role |
| User sees `/install` only | Permissions → portal disabled, or `dashboard_view` blocked | toggle |
| User's peers lack the groups | propagation off, or Save Changes answered "No" to applying to peers | enable propagation; save with Yes |
| JWT groups not syncing | claim name wrong; group names differ from token values; groups don't exist | create groups with the exact names; check claim |
| Everyone locked out after enabling JWT allow group | admins not in the group | fix IdP group; or `PUT /api/accounts/{id}` via an Agent token to clear `jwt_allow_groups` |
| Cannot delete a group | still referenced | Settings → Groups usage counts |
| Cannot delete/demote Owner | by design | transfer ownership first |
| `maximum number of users reached` | Free plan (5 users) | upgrade |
| Token creation fails for another human user | tokens can only be created on your own profile or on Agents | use an Agent |
| Access token stopped working | expired (1–365 days) or deleted; user blocked | new token |

Events: `user.invite`, `user.join`, `user.role.update`, `user.block/unblock`,
`user.delete`, `user.group.add/delete`, `service.user.create/delete`,
`personal.access.token.create/delete`, `group.add/update/delete`,
`account.setting.*`, `transferred.owner.role`, `tenant.updated`, `subscription.updated`.

## 8. Rules that refuse a change, and why

These are deliberate protections, not faults. An admin who does not know them files a
ticket; an admin who does moves on.

| Attempt | Result | Why |
|---|---|---|
| Delete your own account | `self deletion is not allowed` | Prevents locking the account out |
| Delete the Owner | `unable to delete a user with owner role` | Transfer ownership first |
| Block the Owner | Refused | The Owner is always reachable |
| Block or unblock yourself | `admins can't block or unblock themselves` | Same reason |
| Change your own role | `admins can't change their role` | Prevents self-escalation; another admin must do it |
| Grant or remove the Owner role | Only the Owner may | Ownership transfers are owner-initiated |
| Invite someone directly as Owner | Refused | Create then transfer |
| Create a token for another person | Refused | Tokens exist only on your own profile or on an Agent |

The role selector on a user's page is simply disabled in these cases, with no explanation
on screen. When an admin reports that they "cannot change a role", check this table
before looking for a fault.

**Service users count toward the Free plan's user limit.** Creating an Agent on a Free
account consumes one of the five seats, even though Agents are excluded from marketplace
billing counts. See `31-plans-limits-and-billing.md`.

**A group cannot be deleted while anything references it.** Policies, routes, DNS
nameserver groups, setup keys, users, profiles and filters all count, and so do two that
are easy to miss: groups used by disabled DNS management, and groups bound to an
identity-provider validator. Through the API this surfaces as an unhelpful 500, so check
references rather than assuming a server fault (`09-api-and-automation.md` §7). The
dashboard disables the delete control instead and explains it in a tooltip. The `All`
group cannot be deleted at all.

**Plan and device counts reconcile once a day.** A plan change can take up to
twenty-four hours to be reflected in every gate.
