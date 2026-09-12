# Day 0 to Production — Onboarding and Rollout

**Use this for a new customer, or an existing one expanding to a new team.** Most
first-week tickets come from doing things in the wrong order: devices enrolled before
groups exist, the permissive default policy removed too early, or AI security switched to
blocking on day one. This file is the order that avoids them.

Each phase has an exit test. Do not start the next phase until the current one passes.

---

## 0. What the admin sees first

**The onboarding form.** The first owner to sign in is asked for company name, website,
employee count and how they heard about Netzilo. It can be skipped with the close
control, and skipping does not break anything. It appears only once.

**The progress widget.** A floating button sits in the corner of the dashboard. Before
setup is complete it shows onboarding progress and prompts to finish remaining steps.
Afterwards it becomes a system status indicator, reporting signal, relay and DNS problems
at three levels: minor issues, severe degradation, and critical connection issues. Tell
the admin what it is on day one, because a red button later is otherwise alarming and
generates a ticket on its own. It can be hidden from the account menu.

---

## Phase 1 — The server is ready

**Cloud:** nothing to do. Go to phase 2.

**Self-hosted:** the installer leaves several things undone that will become incidents
later. Close them now, on day one, not after the first outage.

1. **Back up.** Nothing is automatic. Set up the backup in `02-server-operations.md` §6
   and prove a restore works before real data exists.
2. **Configure mail.** Without it, invitations and password resets never arrive.
   Until it is done, create users with passwords instead. See `04-identity-and-sso.md`.
3. **Cap container logs.** There is no log rotation by default and a busy server will
   fill its disk.
4. **Close the cache port** if the install published it on the host without a password.
5. **Record where the keys live.** The identity provider master key and the encryption
   key cannot be regenerated. If they are lost, the deployment cannot be restored.

**Exit test:** the dashboard loads over a valid certificate, a test user receives a real
invitation e-mail, and a backup has been restored successfully at least once.

---

## Phase 2 — Design the groups before anyone connects

Groups are the unit of policy. Getting them wrong means re-doing every policy later.

1. **Decide the group model first.** Typically by role and by system type: one group per
   user population, one per class of server or network.
2. **Create the groups** before creating users, so users can be auto-assigned on
   creation and devices inherit them on enrolment.
3. **If the identity provider will drive groups**, configure that now and confirm names
   match exactly. Groups are matched by name and are never created from a token.

**Exit test:** every group that policy will reference exists, and is either populated or
will be populated automatically at enrolment.

---

## Phase 3 — Pilot with a handful of devices

Enrol between three and ten devices covering every operating system in use, owned by
people who will tolerate a problem.

1. **Leave the permissive default policy in place.** Removing it now hides connectivity
   problems behind policy problems.
2. **Enrol one device per platform.** Follow `05-client-install-and-deploy.md`. On macOS
   expect three separate approvals, not one.
3. **Verify each device reaches the network**, not just that it shows as connected.
4. **Test one real workload** end to end: a file share, an internal site, an SSH session.

**Exit test:** every pilot device can reach the intended resource, and
`netzilo status -d` shows direct connections where the network allows them.

---

## Phase 4 — Replace the default policy

Now, and not before.

1. **Write the replacement policies** from the group model, least privilege first.
2. **Confirm each pilot device still works** with both the new policies and the default
   in place.
3. **Remove the permissive default policy.**
4. **Re-test immediately.** If something breaks, this is why.

**Exit test:** pilot devices reach what they should and cannot reach what they should
not. Verify the negative case explicitly; people forget to test what should fail.

---

## Phase 5 — Routes, DNS and exit nodes, if needed

Only if the customer has networks that will not run the client.

1. **Stand up the routing peer** on Linux, and give it high availability with a second
   peer before anyone depends on it.
2. **Publish the route**, then the DNS that makes it usable by name.
3. **Test from a device that is not the routing peer.**

**Exit test:** a pilot device resolves and reaches a resource on the routed network by
name.

---

## Phase 6 — Posture checks, in report mode first

Posture checks silently exclude devices from policies they fail, so a mistake here looks
like a network fault.

1. **Create the check but do not attach it** to a policy yet.
2. **Look at the peer list** and confirm the indicators show what you expect across the
   fleet. A check that every Mac fails, because it names a Windows-only condition, is the
   classic error.
3. **Attach it to one policy** affecting pilot devices only.
4. **Never attach device-integrity or workspace checks to policies whose source group
   contains servers or routing peers.**

**Exit test:** the intended devices pass, the intended devices fail, and nothing else
changed.

---

## Phase 7 — AI security, in report mode first

1. **Create the filter** binding groups, operating systems, tools and scanners.
2. **Run every rule in report mode.** Collect a week of real traffic.
3. **Review what fired.** Tune the rules that produce noise before anyone is blocked.
4. **Switch to blocking** one rule at a time, highest confidence first.
5. **Tell users in advance** that AI traffic is inspected, before the first block.

**Exit test:** a week of events with an acceptable false-positive rate, and a named owner
for tuning.

---

## Phase 8 — Roll out to everyone

1. **Send the user communication** before the install, not with it. Use
   `17-end-user-guide.md` as the basis.
2. **Deploy in waves**, by team, not all at once. Each wave should be small enough that
   one person can handle the questions.
3. **Watch the peer list** after each wave for devices that enrolled but never connected.
4. **Keep the previous access path working** until the last wave is done. Removing the
   old VPN on day one removes your fallback.

**Exit test:** device count matches expected headcount, and the support queue is quiet
for a week before the old path is switched off.

---

## The first-week mistakes, in order of frequency

| Mistake | What it looks like | Avoid by |
|---|---|---|
| Removing the default policy too early | Everything connects, nothing works | Phase 4, after replacements are proven |
| Attaching an impossible posture check | One platform silently loses all access | Phase 6, check the fleet first |
| Blocking AI traffic on day one | Users blocked mid-task, trust lost | Phase 7, report mode first |
| Enrolling before groups exist | Devices land ungrouped, policies miss them | Phase 2 |
| Only approving one macOS prompt | AI features silently do nothing | Three approvals, see `05` |
| No backup on self-hosted | Recoverable incident becomes a rebuild | Phase 1 |
| Removing the old VPN immediately | No fallback during the transition | Phase 8 |
| Not telling users anything | Ticket volume, not technical failure | Phase 8 |

---

## Handover

Before you finish, make sure the customer has:

- A named owner for policy and for AI rule tuning.
- The backup procedure, tested, on self-hosted.
- The plan limits they are subject to (`31-plans-limits-and-billing.md`).
- The end-user guide (`17-end-user-guide.md`) in their own help system.
- The answers to their security review (`14-data-handling-and-privacy.md`).
- Any token created for this engagement deleted.
