---
id: '36'
title: 'Netzilo — Device Tools: diagnose and repair a peer from the support agent'
requires:
- api
- device-tools
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 12849
sections:
- id: '0'
  title: When to reach for a device, and when not to
  chars: 986
- id: '1'
  title: Whose device it is decides what you may do
  chars: 1666
- id: '2'
  title: Find the device
  chars: 1092
- id: '3'
  title: Check the device before you use it
  chars: 1373
- id: '4'
  title: Reading a result
  chars: 1130
- id: '5'
  title: Diagnose methodically
  chars: 540
- id: '6'
  title: Changing a device well
  chars: 1120
- id: '7'
  title: 'Shell: the last tool, not the first'
  chars: 714
- id: '8'
  title: What device tools cannot do
  chars: 678
- id: '9'
  title: When management, not the device, answers
  chars: 1147
- id: '10'
  title: Reporting
  chars: 446
---
# Netzilo — Device Tools: diagnose and repair a peer from the support agent

Until now an agent in the dashboard could read the whole account through the API and
still had to hand the person a command to run on their laptop. Device tools close that
gap. Through management, the agent can ask a device what it can do, read its logs and
connection state, test name resolution and reachability *from that machine*, and, with
the right consent, change its state or run a command on it.

This file is the procedure: when to reach for a device, whose device it is and what that
permits, how to find and check it, how to read a result, how to change a device well, and
what these tools still cannot do. The exact contract of every tool, argument by argument
and platform by platform, is `references/37-device-tool-reference.md`; the diagnostic
method and the symptom trees are `references/38-device-diagnosis-method.md`. Read the
tool card before the first call to a tool; do not learn a tool by calling it.

Two tools carry all of it: `device_tools(peer_id)` lists a device and what it offers;
`device_run(peer_id, name, arguments, reason)` runs one of those tools.

In the Netzilo harness nothing about the customer's server is configured in advance, so
`device_tools` there also takes `server_url` (the management base URL, no `/api`) and
`token`. Get both from the person the way `SKILL.md` establishes the API token, pass them
on the first `device_tools` call for a device, and `device_run` reuses them for that
device. A change (`mod.*`, `shell.run`) on someone else's device shows the person an
approval prompt and runs as soon as they approve; it runs straight away when the session
has no approval prompt, and it does not run only when the person rejects it. Pass
`reason` so the prompt says what will change. The token is recorded in the session like any tool argument: ask for a
short-lived one, and tell the person to revoke it when the task is done.

## 0. When to reach for a device, and when not to

Reach for the device when the question is about **that machine's view of the world**:
it says connected but cannot reach a host; a name resolves in the browser but not through
Netzilo; access is denied and you need to know which posture signal failed; the person
says "it was working yesterday" and only the client log can say what changed.

Do not reach for the device when the account already answers the question. Whether a
policy allows A to reach B, whether a route exists, whether a peer is approved or expired,
what group a user is in — those are API reads (`references/08-network-administration.md`
and the per-page files). Read the account first, and go to the device to confirm or to see
what the account cannot: what the device actually received and did with it.

Every device call is a request to someone's computer. Say what you are about to do, do the
minimum that answers the question, and report exactly what you ran.

## 1. Whose device it is decides what you may do

Management tells you, per device, whether the person in the chat **owns** it. The line
`device_tools` returns says either `(yours)` or `(belongs to someone else)`. That one fact
sets the rules for the whole conversation:

| The device is | Diagnostics (`diag.*`) | Changes (`mod.*`) and commands (`shell.run`) |
|---|---|---|
| the caller's own | run immediately | run immediately |
| somebody else's, caller is an admin | run immediately | **proposed**; the admin approves before anything runs |
| somebody else's, caller is not an admin | refused by management (403) | refused by management (403) |

The proposal path is enforced by the platform, not by your judgement: calling
`device_run` for a `mod.*` or `shell.*` tool on a device the caller does not own ends your
turn with the exact tool and arguments shown to the admin under the heading "Approve
device change". If they choose **Approve**, that call — and only that call — is executed
before your next turn and its result is the first thing you see. A proposal without a
`reason` is refused before it becomes a prompt: say in plain words what will change on
that person's machine and why it helps. "Refresh the device so it picks up the policy you
changed two minutes ago" is a reason. "Fix it" is not.

Before you propose anything that ends a session — `mod.disconnect` — or runs a command —
`shell.run` — say what the person at that laptop will experience. Never route around the
rule: do not use `shell.run` on your own device to reach another, do not describe a
change as a diagnostic, and do not run a diagnostic whose only purpose is a side effect.

## 2. Find the device

The chat is never bound to a machine. You find the device the conversation is about, and
you name it on every call by its **peer id**.

```
GET /api/peers
```

Match on what the person gave you, in this order of reliability: the exact peer **name**
or hostname; the **user** the peer belongs to (`user_id`); the Netzilo **IP**
(`100.64.x.y`); the **DNS label**. For a person asking about their own laptop, filter to
peers whose `user_id` is the caller and pick the connected one, or ask if there are
several. For an admin asking about someone else's device, confirm the name with the admin
before touching it. Two devices on one host share a name; the id is what you pass.

Take these fields with you: `id`, `connected`, `last_seen`, `os`, `version`, `user_id`,
`login_expired`, `approval_required`. A device that is login-expired or awaiting approval
may be connected to management and still unable to work; that is an account fix.

If two peers match, ask. Running a diagnostic on the wrong laptop wastes a turn; running
a change on the wrong laptop is an incident.

## 3. Check the device before you use it

```
device_tools(peer_id="<id>")
```

This never touches the device's network state. It returns one line describing the machine
— name, operating system, whose it is — then the **catalog**: every tool that device
offers right now, with a summary and the JSON Schema of its arguments. The platform in
that line decides your branch for everything that follows ("Darwin" is macOS). The
catalog decides which tools exist; `references/37-device-tool-reference.md` decides what
they mean.

Three answers mean stop, and each has its own next step:

- **"runs a client too old for support tools"** — nothing can run on it. Tell the person
  their Netzilo client needs updating (`references/05-client-install-and-deploy.md`),
  and fall back to the hand-run commands in `references/07-client-troubleshooting.md`.
- **"is offline"** — nothing can run. Check `last_seen`; if recent, the device may be
  mid-reconnect. If old, the problem is the device's connection to management, which
  `references/07-client-troubleshooting.md` §4 diagnoses by hand.
- **"the command did not run: you do not have access to this device"** — the caller may
  not use this device. Do not look for another way in.

Call `device_tools` once per device per conversation. `device_run` refuses a device it has
not seen a catalog for, so the order is not optional.

## 4. Reading a result

Every `device_run` returns one envelope. Read `status` first, then the payload. The full
contract is `references/37-device-tool-reference.md` §0; the short version:

| `status` | Meaning | Do |
|---|---|---|
| `ok` | the tool ran | read `output`; **for `shell.run`, a non-zero `exit_code` is a finding, not an error** |
| `error` | the tool ran and failed | report `error`; do not retry blindly |
| `invalid` | your arguments did not match the schema | fix them from the catalog |
| `unknown` | no such tool on this device | re-read the catalog |
| `disabled` | the account switched that family off for this device | say so; no workaround |
| `unsupported` | this platform or this daemon's privilege cannot do it | `error` names the cause |
| `timeout` | the deadline passed | for `diag.*` repeat once; for a change or a command, ask what the person observed before repeating |

`truncated: true` means the payload was clipped; never present it as complete. Quote a
`verdict` where a tool gives one. A line beginning `the command did not run:` is not a
result at all: management never dispatched it (§9).

## 5. Diagnose methodically

Do not improvise a sequence of tool calls. `references/38-device-diagnosis-method.md`
gives the facts you must not rediscover, the loop (symptom, account first, platform,
one hypothesis per tool, evidence ledger, stop condition), the per-platform matrix, and a
decision tree for each symptom an operator actually reports: not connected, connected
but cannot reach X, names do not resolve, slow, access denied, worked yesterday, after an
upgrade. Load the section for the symptom in front of you and follow it.

## 6. Changing a device well

Changes are rarely the first step and never the only one. Read, say, apply, read back,
report — the same six steps as an API write.

1. **Read** the state you are about to change (`diag.status`, `diag.routes`, `diag.loglevel`).
2. **Say** what you will do and what the person at the device will experience. For a
   device that is not the caller's, this is the `reason` the admin reads.
3. **Apply** exactly one change.
4. **Read back** with the matching diagnostic and quote the new value.
5. **Report** the difference, and how to undo it.

Three tools change a device. `mod.refresh` forces a sync and is the answer to stale
policy; read `diag.routes` or `diag.status` back afterwards. `mod.loglevel` is only useful
if you then reproduce and read the log, so plan both in one breath and **lower it
afterwards**. `mod.disconnect` **signs the person out** and ends your work on that device
for this conversation: its result comes back first, marked scheduled, and the client goes
down the moment the result has left. There is no reconnect and no separate logout; the
person signs in again.

## 7. Shell: the last tool, not the first

`shell.run` exists for what no structured tool answers: a system utility's view of the
network, a service state, a file the client did not write. Before running a command,
state the exact command and what it reads or changes; on a device the caller does not own
that statement is your `reason`. Arguments are verbatim — pipelines need `sh -c` or
`powershell -Command` — and every command is platform-specific, so pick it from the OS
table in `references/37-device-tool-reference.md` §13, never from memory of another OS.
Output is capped; search large files with `diag.grep`, count on the device, never pipe a
log into the result. The never list in §13 is not advisory.

## 8. What device tools cannot do

- **The debug bundle stays on the device.** `diag.bundle` returns a path; nothing uploads
  it. The person sends it for an escalation (`references/12-escalation-package.md` §11).
- **No file transfer, no interactive session, no state between calls.** One request, one
  answer; each `shell.run` starts fresh.
- **Legacy clients offer nothing**, and management refuses them before dispatching.
- **A family may be off by account policy.** `disabled` is a decision, not a fault.
- **One device at a time.** Diagnose one fully, then ask before touching a second.
- **Delivery is at most once.** A `timeout` does not say whether the command ran.

## 9. When management, not the device, answers

Any line beginning `the command did not run:` is management refusing or failing to
dispatch. The device did not see the request.

| Message says | Meaning | Do |
|---|---|---|
| you do not have access to this device | the caller may not use it | stop; explain §1 |
| Management does not know this device | wrong peer id, or another account's peer | re-check `GET /api/peers` |
| the device is offline | not connected right now | check `last_seen`; the fix is the device's own connection |
| too old for support tools | client predates the feature | update the client; hand-run steps |
| connected to another management node | online, but its connection is on a different server node | retry once; if it persists, a server-side routing problem for the admin |
| this deployment cannot reach devices | no device transport configured | nothing device-side can run here |
| did not answer in time | dispatched, no reply, or the device is not reading its updates | for `diag.*` repeat once; otherwise ask first |
| could not reach Management | the agent lost the server | report; it is not the device |

## 10. Reporting

Say what you ran, on which device and platform, and what it showed, in the product's
words: "your laptop is connected but every peer is relayed, which is why it is slow", not
a field name. Close with **Outcome**, **Changes made** (and how to undo), **Open items**,
**Next step**. If you ran anything on a device the caller does not own, list it even when
it was read-only; the admin approving is entitled to a complete account.
