---
id: '15'
title: Incident Response and Recovery — Containment, Revocation, Getting Back In
requires:
- api
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 8946
sections:
- id: '1'
  title: Before you touch anything
  chars: 707
- id: '2'
  title: What each action actually does
  chars: 1266
- id: '3'
  title: Suspected compromised device
  chars: 1150
- id: '4'
  title: Suspected compromised or leaked credential
  chars: 1062
- id: '5'
  title: Departing employee
  chars: 949
- id: '6'
  title: Locked out — getting back in
  chars: 2060
- id: '7'
  title: Suspicious AI activity
  chars: 787
- id: '8'
  title: After the incident
  chars: 488
---
# Incident Response and Recovery — Containment, Revocation, Getting Back In

**Use this when something is wrong right now**: a device or account is suspected
compromised, credentials leaked, an employee left abruptly, or an admin change locked
people out. These are low-volume and high-severity. Speed matters, and so does not making
it worse.

Work top-down through the relevant section. Every step says what it does immediately,
what it does not do, and how to verify.

---

## 1. Before you touch anything

1. **Get the token and, for self-hosted, shell access** (`SKILL.md`). Containment through
   the API is faster and leaves an audit trail.
2. **Write down the time in UTC** when you started. You will need it to read logs later.
3. **Do not delete anything yet.** Blocking is reversible and preserves evidence.
   Deleting is not. Contain first, investigate second, clean up last.
4. **Capture evidence before you change state** if this may become an investigation:
   export the relevant Activity events and, for a device, collect a debug bundle
   (`12-escalation-package.md`). Blocking a user does not erase their history, but
   deleting them removes their devices.

---

## 2. What each action actually does

Knowing this prevents the most common mistake, which is revoking the wrong thing and
believing the problem is contained.

| Action | Effect | Does **not** do |
|---|---|---|
| **Block user** | Immediate. Their devices are disconnected and dashboard access is refused. Reversible. | Does not delete devices or history |
| **Delete user** | Removes the user, their devices and their dashboard access. Irreversible. | Cannot be done to yourself or to the Owner |
| **Delete peer** | Removes that device from the network immediately | Does not stop the person re-enrolling if they still have a valid login or setup key |
| **Delete or expire a setup key** | Stops the key being used for **new** enrolments | **Does not disconnect devices already enrolled with it.** This is the single most common containment mistake |
| **Delete an access token** | That token stops working immediately | Does not affect the user's own login |
| **Remove from all groups** | Policies stop matching, so access stops | Device stays connected and enrolled |
| **Disable a route** | The published network stops being reachable through it | Does not remove the routing peer |
| **Disable a tool or scanner** | Applies everywhere immediately | — |

---

## 3. Suspected compromised device

Contain in this order.

1. **Block the owning user** if a person owns the device. This disconnects all their
   devices at once and is the fastest single action.
2. **Delete the peer** if you want that specific device out while leaving the person
   working on others.
3. **Check how it enrolled.** If it was enrolled with a setup key, deleting the peer is
   not enough: the same key can enrol it again. Delete or expire the key, then confirm
   no other device used it.
4. **Verify it is gone.** The peer should disappear from the peer list and stop appearing
   as connected. Confirm from the server side rather than from the device.
5. **Collect evidence** from the device if you still have access, then rebuild it.
6. **Review what it reached** in Activity, filtered to that peer, for the period in
   question. For AI activity use the AI Activity report.

**If the device is lost or stolen and you cannot reach it:** block the user, delete the
peer, and rotate any setup key it held. Its stored configuration contains a private key
that is now useless because the server no longer recognises the peer.

---

## 4. Suspected compromised or leaked credential

| What leaked | Do this |
|---|---|
| A user's password or SSO session | Block the user, force a password reset and re-enrol MFA in the identity provider (`04-identity-and-sso.md`), then unblock |
| An API access token | Delete that token. Tokens carry the full permissions of their owner's role, so also review Activity for what it did |
| A setup key | Delete or expire it, then audit every peer that enrolled with it and remove any you do not recognise |
| The AI inspection certificate authority key on a device | Treat the device as compromised, rebuild it. The key is per-device |
| A server secret, such as the database password or the identity provider master key | This is a server rebuild. Follow `02-server-operations.md` for backup and restore, and change the secret as part of the restore rather than in place |

After any credential incident, check whether the same credential is embedded in
automation. A deleted token breaks every script using it, which is correct but should be
announced.

---

## 5. Departing employee

Order matters. Blocking first stops access while you do the rest.

1. **Block the user.** Access stops immediately, devices disconnect, nothing is lost.
2. **Export their activity** if the organisation retains records of access.
3. **Reassign or delete their devices.** A shared machine should be re-enrolled under
   its new owner rather than left on the old account.
4. **Check for tokens and agents they created.** Tokens belonging to a deleted user go
   with them and will break any automation depending on them. Move automation to a
   service user first, see `25-users-groups-and-account-settings.md`.
5. **Check group memberships driven by the identity provider.** If groups come from the
   provider, removing them there is what actually revokes access.
6. **Delete the user** once the above is done.
7. **Verify:** they no longer appear in the user list, their peers are gone, and a login
   attempt fails.

---

## 6. Locked out — getting back in

These are the cases where a correct-looking change removes everyone's access, including
the admin who made it.

### 6.1 Everyone locked out after enabling a group restriction on login

Enabling a restriction that only allows members of one identity-provider group will lock
out everyone who is not in that group, including the admin who set it.

**Recovery:** use an API token that already exists to clear the restriction on the
account settings. This is why the intake checklist asks for a service-user token early:
it keeps working when interactive login does not. If no token exists and no one can log
in, this becomes a server-side fix on self-hosted, and a support case on Cloud.

**Prevention:** the dashboard warns to make sure you are in the group before saving.
Confirm your own membership first, and keep one break-glass admin outside the
restriction.

### 6.2 Policy change removed everyone's access

Removing the permissive default policy before replacements exist, or attaching a posture
check that every device fails, silently blocks traffic. Nothing errors.

**Recovery:** re-enable the previous policy or detach the posture check. Policies take
effect on the next sync, which is immediate for connected peers.

**How to tell this is what happened:** clients report zero connectable peers while the
control plane is healthy. `11-connectivity-diagnosis.md` covers the full check.

**Prevention:** make posture checks report-only first where possible, and never attach a
virtual-device or workspace check to a policy whose source group contains servers.

### 6.3 The Owner is unavailable

Only the Owner can change the plan or transfer ownership, and the Owner cannot be
deleted or blocked. If the Owner has left, ownership must be transferred from their
account before it is closed. Plan this during offboarding rather than after.

### 6.4 Admin cannot change their own role

Admins cannot change their own role or block themselves, by design. Another admin or the
Owner must do it. This is not a fault.

---

## 7. Suspicious AI activity

1. **Identify the scope**: which user, which device, which agent, which tool. The AI
   Activity report groups by user and by device, and the per-peer session snapshots show
   what an agent actually did.
2. **Contain** by disabling the tool, or by removing the device's group from the filter
   that permits it. Disabling a tool applies everywhere immediately.
3. **Confirm enforcement changed** by checking that new events show the action you
   expect rather than the previous one.
4. **Preserve the evidence.** Events carry the content that triggered a detection, which
   is what an investigator needs. Export before pruning anything.
5. **Tighten the rule** only after containment, so you are not changing detection logic
   during an incident.

---

## 8. After the incident

- Write down what was revoked and when, in UTC. Activity is the authoritative record.
- Restore anything you blocked that turned out to be legitimate.
- Remove temporary access you granted yourself, including any token the customer created
  for you.
- If the cause is unclear and the answer needs the product's internals, build the package
  in `12-escalation-package.md`. Include the containment timeline so the analyst is not
  confused by state you changed.
