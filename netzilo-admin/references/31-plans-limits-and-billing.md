# Plans, Limits and Billing — Why Something Is Blocked

**Use this when an action is refused and the reason might be the plan, a quota, or
billing.** These produce more tickets than any genuine fault, and almost all of them are
self-service once the admin knows which limit they hit.

**Dashboard:** Settings → **Plans & Billing** (owner only; not shown on self-hosted or
managed instances). **API:** tenant subscription endpoints, owner only.

Never quote a price from memory. Prices and trial terms are shown in the dashboard and
are the only figures to rely on.

---

## 1. The three plans

Every account carries one plan: **Free**, **Professional** or **Enterprise**. The plan is
a property of the tenant, and every gate below reads it.

| Plan | Users | Devices | Notable gates |
|---|---|---|---|
| Free | 5 | 100 | No posture checks, no profiles, no premium scanner rules, no event streaming |
| Professional | unlimited | unlimited | No profiles, no premium scanner rules |
| Enterprise | unlimited | unlimited | Everything |

Trials run for fourteen days on both paid plans. An Enterprise checkout bills a minimum
of ten seats even if the account has fewer users. Both facts are shown at checkout.

---

## 2. Every hard limit, and the exact message

| Limit | Applies to | What the admin sees | Fix |
|---|---|---|---|
| 5 users | Free | `maximum number of users reached`, HTTP 409, when inviting the sixth | Delete a user or upgrade |
| 100 devices | Free | `maximum number of personal peers reached`, HTTP 403, when enrolling the 101st | Remove peers or upgrade |
| Posture checks | Free | `free customers can't update posture checks`, HTTP 403. The dashboard shows **Upgrade Plan** instead of Save | Upgrade |
| Profiles | Free, Professional | `only Enterprise customers can update profiles`, HTTP 403 | Upgrade to Enterprise |
| Premium scanner rules | Free, Professional | `Enterprise subscription required to use premium scanner rule <id>`, HTTP 403, when saving a filter that binds one. In the scanner catalogue the rule shows a **Locked** badge | Upgrade to Enterprise, or bind a custom scanner instead |
| Event streaming | Free | Refused with a message that Free customers cannot enable it | Upgrade |
| Personal access token lifetime | all | `expiration has to be between 1 and 365` | Choose 1 to 365 days |
| Setup key lifetime | all | `expiresIn should be between 1 day and 365 days` | Choose 1 to 365 days |
| Peer login expiration | all | `peer login expiration can't be larger than 180 days` or smaller than one hour | Choose between one hour and 180 days |
| Tenant logo | all | `file too large. Maximum size is 500KB`, HTTP 400 | Use a smaller PNG, JPG or SVG |
| Scanner rule replay payload | all | Request rejected above 512 KB of rule YAML | Replay a smaller rule set |
| Event batch from a device | all | `too many events: maximum allowed is 1024` | Not admin-actionable; devices batch automatically |

**Two traps worth stating before the customer hits them.**

Service users, shown as **Agents**, count toward the Free plan's five-user limit. Creating
an automation agent on a Free account can consume a seat a person needed. They are not
counted in marketplace billing, which is why the two numbers can differ.

Edge **Filters** themselves carry no plan restriction. Any plan can create and use them.
Only premium catalogue scanner rules bound inside a filter require Enterprise. Do not
tell a Professional customer to upgrade in order to use filters.

---

## 3. What has no limit

There is no cap on groups, policies, network routes, DNS nameserver groups, setup keys,
API tokens, custom scanners, or integrations. There is no API rate limit. There is no
automatic retention limit on activity events, so plan database growth on a busy
self-hosted server.

---

## 4. Changing plan

Upgrades and downgrades are self-service in Settings → Plans & Billing, and only the
**Owner** can make them. An admin who is not the owner gets `Only owners can update
subscriptions`. Transfer ownership or have the owner do it.

**A downgrade is blocked while the account is over the target plan's limits.** The
dashboard says `Please reduce number of peers to 100 in order to be able to downgrade.`
or the equivalent for users. Remove the excess first, then downgrade.

A downgrade takes effect immediately and is charged pro rata for the current cycle. The
dashboard states this before confirming.

**Plan and device counts reconcile once a day, in the early hours UTC.** An upgrade can
therefore take up to twenty-four hours to be reflected everywhere. If a customer upgraded
and a gate still refuses them, this is almost always why. Wait, do not re-purchase.

---

## 5. What happens when payment lapses

This is the question customers ask most and the one most often answered wrongly.

When a subscription ends through the payment provider, the account is **set back to
Free**. Nothing is deleted and nothing is disconnected. Existing users, devices,
policies, routes and rules keep working, even if they exceed the Free limits.

What stops is **new** work. No new users beyond five, no new devices beyond one hundred,
no posture check or profile edits, no premium scanner rules.

Restoring the plan restores those actions immediately, subject to the daily reconcile in
§4. Tell the customer plainly: nothing was lost, additions are paused.

---

## 6. Self-hosted and managed instances

Self-hosted servers have no billing page and no payment provider. The plan is set on the
server:

- **Marketplace images** promote the tenant to Enterprise automatically after the first
  login, through a one-shot service that then disables itself.
- **On-premises and managed-provider installs** use a provider key set in the server
  environment. When it is present, new tenants default to Enterprise.

If a self-hosted customer reports that an Enterprise feature is gated, check the tenant's
plan on the server before anything else. This is a server configuration question, not a
billing one. The procedure is in `02-server-operations.md`.

---

## 7. Diagnosis

| Symptom | Cause | Action |
|---|---|---|
| Invite fails with a conflict | Free five-user limit, possibly consumed by Agents | Count users including Agents; delete one or upgrade |
| New device refused | Free hundred-device limit | Remove stale peers, see `24-peers-and-setup-keys.md`, or upgrade |
| Save button reads **Upgrade Plan** | Feature gated on this plan | Check §2 for which plan is needed |
| A scanner shows **Locked** | Premium catalogue rule on a non-Enterprise plan | Upgrade, or write an equivalent custom rule |
| Upgraded but still blocked | Daily reconcile has not run | Wait up to twenty-four hours before investigating further |
| Downgrade button does nothing | Over the target plan's limits | Read the message; reduce users or devices first |
| Features stopped being addable, nothing was deleted | Subscription lapsed to Free | Restore the plan, see §5 |
| Enterprise feature gated on self-hosted | Tenant plan not set on the server | See §6 |
| Owner cannot be reached to change plan | Only owners can change plans | Transfer ownership, see `25-users-groups-and-account-settings.md` |

Deleting the tenant is irreversible and removes every peer, user, group, policy and
route. If the account carries a paid subscription, cancel the subscription first so
billing does not continue, then delete.
