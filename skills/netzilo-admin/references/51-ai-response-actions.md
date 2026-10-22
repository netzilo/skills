---
id: '51'
title: AI Response Actions — Autonomous Response and the AI Kill Switch
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 25178
sections:
- id: '1'
  title: What a response action does
  chars: 2049
- id: '2'
  title: Autonomous response — Netzilo contains a session on its own
  chars: 2590
- id: '3'
  title: Scopes — what an action applies to
  chars: 1614
- id: '4'
  title: Applying, editing, lifting and deleting in the dashboard
  chars: 3627
- id: '5'
  title: The REST API
  chars: 3913
- id: '6'
  title: Delivery and enforcement on each host
  chars: 1418
- id: '7'
  title: What a stopped person or agent sees
  chars: 1294
- id: '8'
  title: Session badges — the badge means it is enforced
  chars: 892
- id: '9'
  title: Activity events
  chars: 897
- id: '10'
  title: Incident playbook — contain first, investigate, lift
  chars: 1950
- id: '11'
  title: Troubleshooting
  chars: 2386
- id: '12'
  title: Limits to state before a customer discovers them
  chars: 962
---
# AI Response Actions — Autonomous Response and the AI Kill Switch

**Dashboard:** Edge → Governance → **Actions** (`/ai-edge/governance?tab=actions`; the
older `/ai-controls` address redirects there), and the **Response Action** menu of an AI
session (Edge → **Sessions**). **API:** `/api/ai/controls`. Owners and admins only.

Netzilo responds to AI threats on its own. When an agent session goes wrong — injected
instructions, drift from what the user asked, a harmful tool call blocked and then tried
again — Netzilo puts the session **Under Inspection** and, at the second strike,
**isolates** it: every AI call of that session is refused on every device, browser and
gateway that carries it, within seconds, with no one watching. An administrator does the
same by hand with the **AI Kill Switch**: one response action — isolate the Finance
group, one user, one agent everywhere, or all AI activity — stops that AI at once, with a
clear reason shown to every person and agent it stops, until it is lifted.

This file is the operator's runbook: what the two actions do, who they cover, how to
apply and lift them in the dashboard and through the API, how fast hosts enforce them,
what a stopped person or agent sees, and the incident playbook. Rule authors who want a
guardrail to apply an action load `32-detection-rule-authoring.md` (Response Actions).

Versions: Netzilo Server, the Netzilo client and the AI Gateway **v5.3.590** or later,
the browser extension **5.2.578** or later, the Agent SDK **5.2.2** or later. An older
host does not enforce response actions (§11).

---

## 1. What a response action does

| Action | Badge | Verb | What it does |
|---|---|---|---|
| **Isolation** — the AI Kill Switch | **Under Isolation** | Isolate | Every AI call it covers is refused: model calls, tool and MCP calls, chats in the browser. A stream in progress is cut. The refusal tells the person or agent why (§7) |
| **Inspection** | **Under Inspection** | Inspect | Stricter checks. Guardrails see that the session is under inspection and act on it (Cruise Control Gate and Containment, §2). Inspection on its own blocks nothing |

- **Isolation wins over inspection.** When both cover a call, the call is refused.
- **Management keeps the desired state; each host enforces it.** Netzilo Server
  replicates every action to every host that carries AI traffic: the Netzilo client on
  devices (desktop AI apps through inspection, coding-agent hooks, agents with the
  embedded SDK), the AI Gateway, and the browser extension. Each host decides locally on
  every call, keeps the actions on disk — an isolation holds across restarts and while
  management is unreachable — and reports which version it applied (§6).
- **An action covers AI activity Netzilo governs.** It refuses what passes through a
  Netzilo host: an AI app the device inspects (an endpoint filter's Agents), a hooked
  coding agent, an SDK agent, the browser extension's AI sites, every call through the
  AI Gateway. It does not disconnect the device, block the user's sign-in or touch
  network access; for that, block the user (`15-incident-response-and-recovery.md` §2).
- **Every action carries a reason** (required, up to 1000 characters): it is recorded in
  the activity log and shown in every refusal. Write it for the person who will read it
  in their tool: "Investigating a suspected data leak — contact the security team".
- **Expiry is optional.** Never, In 1 hour, In 24 hours, In 7 days, or At a specific
  time; the action is lifted automatically then. Actions Netzilo applies on its own
  expire after 7 days unless lifted earlier (§2).

---

## 2. Autonomous response — Netzilo contains a session on its own

Netzilo's Cruise Control rules apply response actions themselves, in seconds. The rows
they create show **Applied by: Guardrail `<rule name>`** (source **Guardrail** in the
filters) and the event **Response action applied by a guardrail** (§9).

| Rule | Id | What it does |
|---|---|---|
| **Cruise Control Inspection** | `netzilo-intent-probation-001` | When **Cruise Control Patrol** flags a session — injected instructions, drift from the user's request, likely harm — it puts that session **Under Inspection**. It never blocks on its own |
| **Cruise Control Containment** | `netzilo-intent-containment-001` | When a session is **Under Inspection** (by Cruise Control Inspection or by an administrator) and **Cruise Control Gate** blocks another of its tool calls — the second strike — it **isolates** the session |

How the response behaves:

- **One session, nothing wider.** A guardrail isolates or inspects the session it judged;
  isolating a user, a group or an agent is an administrator's decision.
- **An administrator's lift wins.** An action an administrator lifted is not raised
  again by the same guardrail for that session, on any host.
- **Rule-raised actions expire after 7 days** unless lifted earlier.
- **Inspection changes the other rules' behaviour.** A session an administrator puts
  Under Inspection is checked by Cruise Control Gate and Patrol as if Patrol had flagged
  it; lifting the inspection ends those stricter checks.

Turning it on: add the four Cruise Control rules (Gate, Patrol, Inspection, Containment)
from the public rule library (`github.com/netzilo/aidr-sigma`, `ai_agent/`) under
Edge → Governance → **Guardrails** and bind all four in the same filters — endpoint
filters for devices and browsers, gateway filters for the AI Gateway
(`28-edge-guardrails.md`, `29-edge-filters.md`). Inspection reads what Patrol keeps and
Containment reads what Gate decided, so a filter that binds one without the other does
nothing useful. Gate and Patrol have their own prerequisites (`10-ai-security-aidr.md`
§8). Inspection and Containment declare the `controls` capability: hosts older than this
release skip them (they load nothing and raise nothing), and Gate and Patrol keep working
on their own there.

They have no report mode of their own: Inspection only labels a session, and Containment
isolates only after Gate has already blocked twice. Roll them out on a pilot group like any guardrail (`28` §4), read the
**Response action applied by a guardrail** events, then widen.

---

## 3. Scopes — what an action applies to

| Applies to | What it covers |
|---|---|
| **All AI activity** | everything in the account. Isolating it asks for a second confirmation: "All AI activity in your account will be blocked." → **Isolate All AI Activity** |
| **Users** | each user's AI on all their devices, in their browser and at the AI Gateway (up to 1000 users) |
| **Groups** | the users and devices in the groups (up to 200 groups). Membership follows automatically: someone who joins a group under isolation is covered at the next sync, someone who leaves is freed |
| **Devices** | everything the Netzilo client on those devices governs, and calls the AI Gateway receives from those devices over the network (up to 1000 devices). A browser is not a device: the extension is covered through its user, not through a device action |
| **Agents** | an agent ID or a glob pattern, case-insensitive, matched against the agent of each call: `claude-code`, `codex`, a browser AI site such as `chatgpt.com`, or `*-sdk-*`, `anthropic-sdk-*` (`*` any run of characters, `?` one character). Up to 50 per action. The agent ID is the **agent** of a session in Edge → Sessions |
| **Sessions** | the selected AI sessions only (up to 200), on whichever host carries them |

Through the API one action may combine dimensions: users, groups and devices are
alternatives (a call by any of them matches), while agents and sessions narrow — users
`[alice]` + agents `[claude-code]` isolates only Alice's Claude Code. The dialog offers one
dimension per action; **All AI activity** cannot be combined with anything.

---

## 4. Applying, editing, lifting and deleting in the dashboard

### 4.1 The Actions tab

Edge → Governance → **Actions** — "Isolate or inspect AI activity for sessions, users,
groups, devices or agents." The tab reads "{n} Actions" while more than one is active.

- Filters: state **Active** (default) / **Lifted** / **Expired** / **All**; **All
  actions** (Isolation, Inspection); **All sources** (Administrator, Guardrail); search
  "Search response actions...".
- Columns: **Action**, **Applies to**, **Applied by** (the administrator's e-mail, or
  "Guardrail `<rule name>`"), **Created**, **Expires** ("Never"). A lifted row says
  "Lifted by `<user>` on `<time>`"; an expired one "Expired on `<time>`".
- Row menu: **Lift**, **Delete**; clicking a row opens **Edit Response Action**. Select
  rows to **Lift** or **Delete** several at once.

### 4.2 Add an action (the AI Kill Switch)

**Add Action** → **Add Response Action** ("Isolation blocks AI activity; inspection
applies stricter checks."):

1. **Action**: Isolation or Inspection.
2. **Applies to**: All AI activity, Users, Groups, Devices, Agents or Sessions, then pick
   the targets (agents are typed: "Agent ID or pattern, e.g. claude-code or *-sdk-*").
3. **Reason** (required): "Recorded in the activity log and shown in blocked responses."
4. **Expires**: Never, In 1 hour, In 24 hours, In 7 days, At a specific time.
5. **Add Action** → "Response action added".

Then verify enforcement, not intent: the covered sessions show **Under Isolation** in
Edge → Sessions once their hosts applied it (§8), and new calls appear as **AI blocked**
events with the response-action reason (§9).

### 4.3 From a session

In Edge → **Sessions** (and the session's own view), the **Response Action** menu offers
**Isolate session**, **Inspect session**, **Isolate user**, **Isolate agent** and, when an
action holds the session, **Lift action**. Each asks for a reason ("Isolate all AI
sessions of `<user>`?", "Isolate all sessions of `<agent>`?").

- **Lift action lifts the whole action holding the session**, whatever its scope. The
  dialog says "Applies to `<scope>`." — read it: lifting a group's isolation from one
  session frees the whole group.
- A session row's **⋯** menu also has **Isolate**, **Inspect**, **Lift** and **Delete**;
  selecting several rows offers the same in bulk. A bulk **Lift** ("Lift response actions
  for N sessions?") frees the selected sessions from actions that name only sessions — an
  action left with none is lifted, one that names others too is narrowed — and lists the
  wider actions (users, groups, devices, agents, all) that still hold some: "Lift them in
  Governance → Actions."
- **Delete** a session ("The session and all its data are permanently deleted.") removes
  its recorded calls, conversation, trajectory and behaviour graph. It is an
  administrator's action and is recorded as **AI session deleted**; it does not lift an
  action. Export what an investigation needs first.

### 4.4 Edit, lift, delete

- **Edit** changes the action, scope, reason or expiry ("Edit Response Action" → **Save
  Changes**). A lifted action is history and cannot be edited.
- **Lift** — "Lift response action?" shows "Applies to `<scope>`." and an optional
  "Reason for lifting" → **Lift** → "Response action lifted". The row stays under
  **Lifted** with who lifted it and why. Lifting is the normal way to end an action: it
  keeps the record and tells the guardrails the administrator decided (§2).
- **Delete** — "The action stops applying immediately." The row is gone; only the
  activity log keeps it. Prefer Lift.

---

## 5. The REST API

Admin token (`SKILL.md`, "First things first"); a non-admin gets `403 Only
administrators can manage response actions`. Read the request back after every write
(`SKILL.md`, "Making a change through the API").

| Call | Does |
|---|---|
| `GET /api/ai/controls[?past=1]` | the account's actions, active first; `past=1` adds lifted and expired ones (at most 500 rows) |
| `POST /api/ai/controls` | apply an action (body below) |
| `PUT /api/ai/controls/{controlId}` | replace its effect, scope, reason and expiry (same body); a lifted action → `412` |
| `POST /api/ai/controls/{controlId}/lift` | lift it; optional body `{"reason": "…"}` |
| `DELETE /api/ai/controls/{controlId}` | delete it |
| `POST /api/ai/controls/bulk-lift` | `{"ids": […], "reason": "…"}` → `{"lifted": n}` (1–500 ids) |
| `POST /api/ai/controls/bulk-delete` | `{"ids": […]}` → `{"deleted": n}` |
| `POST /api/ai/controls/release-sessions` | `{"session_ids": […], "reason": "…"}` → `{"lifted", "narrowed", "skipped": [wider actions still holding some]}` |
| `GET /api/ai/sessions?control=kill\|probation\|any` | sessions an action holds for real (as their hosts applied it); every session carries `control` (applied) and `action` (in force now) as `{id, effect, reason, origin}` |
| `DELETE /api/ai/sessions/session?id=<session>`, `POST /api/ai/sessions/bulk-delete {"session_ids": […]}` | delete AI sessions and everything they recorded |

Body of `POST` / `PUT`:

| Field | Value |
|---|---|
| `effect` | `"kill"` (isolation) or `"probation"` (inspection) — required |
| `all` | `true` for all AI activity; then no other scope field |
| `users`, `groups`, `peers` | user ids, group ids, peer (device) ids |
| `agents` | agent IDs or glob patterns |
| `sessions` | AI session ids as `GET /api/ai/sessions` returns them |
| `reason` | required, at most 1000 characters |
| `expires_at` | RFC 3339 time in the future, or omit/`null` for never |

Isolate a group — the AI Kill Switch for Finance:

```bash
nz /groups | jq -r '.[] | select(.name=="Finance") | .id'     # read the id first
nz /ai/controls -X POST -d '{
  "effect": "kill",
  "groups": ["<finance-group-id>"],
  "reason": "Suspected prompt injection in a vendor email — contact security@example.com",
  "expires_at": "2026-10-23T18:00:00Z"
}'
```

Inspect one agent everywhere, isolate one session, lift:

```bash
nz /ai/controls -X POST -d '{"effect":"probation","agents":["*-sdk-*"],"reason":"Reviewing SDK agents after an incident"}'
nz /ai/controls -X POST -d '{"effect":"kill","sessions":["<session id>"],"reason":"Session sent customer data to an unknown host"}'
nz /ai/controls/<controlId>/lift -X POST -d '{"reason":"Investigation closed, no data left the company"}'
```

The answer of a create or edit is the action: `id` (`c-…` for an administrator's, `r-…`
for one a guardrail raised), `effect`, `all`, `sessions`, `users`, `groups`, `peers`,
`agents`, `reason`, `origin` (`admin:<user id>` or `rule:<rule id>`), `created_at`,
`expires_at`, `active`, `version`. The list adds `state` (`active`, `expired`, `lifted`),
`lifted_at`, `lifted_by`, `lift_reason`, and for an active action **`hosts`** (hosts seen in
the last day that it reaches) and **`applied`** (how many of them applied its latest
change) — the quickest check that it is enforced.

Refusals: `422` with the reason in plain words (no effect, no reason, an unknown user,
group or device, an invalid agent pattern, `all` combined with a scope, an expiry in the
past); `412` "This account already has 500 response actions in force, the maximum. Lift
an action before adding another" (administrators' actions; those Netzilo raises do not
count); `404` for an unknown id.

`GET /api/ai/controls/view`, `POST /api/ai/controls/report` and
`/api/users/current/ai-controls[/report]` are how the AI Gateway and the browser extension
fetch actions and report them. They are not for scripts.

---

## 6. Delivery and enforcement on each host

| Host | How it receives actions | How fast | Needs |
|---|---|---|---|
| Netzilo client on a device (inspection, hooks, SDK) | pushed by management with the device's network map | usually well under a second for a connected device | client v5.3.590+; Agent SDK 5.2.2+ for SDK agents |
| AI Gateway | polls management | every 2 s | gateway v5.3.590+ |
| Browser extension | refreshes from management | every 30 s, and at sign-in | extension 5.2.578+, signed in |

- **Offline is safe for isolation.** Every host keeps the actions it applied on disk and
  enforces them after a restart and while management is unreachable. A device that was
  offline when an action was added receives it when it reconnects; until then it cannot
  enforce what it has not received.
- **The browser extension enforces an isolation even with no browser filter** for the
  user: a signed-in extension fetches the user's actions on its own.
- **Lifting follows the same path** and the same timing: the gateway frees the session
  within 2 s, a browser within 30 s, a connected device at once.
- Hosts log what they applied: on a device `[intake] AI controls: version N, M
  control(s)` (and `[intake] AI controls restored (version N)` at start); on the gateway
  `gateway ai: controls version N, M control(s)` and, per refused call, `gateway ai:
  killed a call of <user> (control <id>)`.

---

## 7. What a stopped person or agent sees

Every refused call carries one line:

> Response action: AI access is isolated by an administrator. Reason: `<reason>`. Reference: `<id>`.

— or "…isolated by a guardrail. Reason: …" when Netzilo applied it on its own (§2). The
Reference is the action's id.

| Where | What appears |
|---|---|
| A coding agent or SDK agent through the AI Gateway | the model or MCP call fails with HTTP 400, error type `netzilo_policy`, and the line above — Claude Code shows it as an API error |
| An AI app or agent on a device | the call is refused with the same line, the way a guardrail block is refused (`10-ai-security-aidr.md` §3); a stream in progress is cut |
| A web AI app in the browser (ChatGPT, Claude, Gemini, …) | the chat is refused like a guardrail block (`49-browser-extension-aidr.md` §5), with the response-action line |
| Inspection | nothing, unless a guardrail then blocks a call |

What to tell the person: their AI access was stopped on purpose by the security team (or
automatically by Netzilo), the reason is in the message, and the Reference is what the
administrator needs. Nothing on their device fixes it; retrying is refused the same way.
`17-end-user-guide.md` and `39-end-user-self-service.md` carry the user-facing wording.

---

## 8. Session badges — the badge means it is enforced

Edge → **Sessions** shows a status badge **Under Isolation** or **Under Inspection** and
has a status filter (**Any Status**, **Under Isolation**, **Under Inspection**); sessions
also show **Active**, **Idle** or **Finished**.

- **A badge appears only once the host carrying the session applied the action** —
  device, gateway or browser. It is real enforcement, not intent. A session whose host
  has not applied it yet shows no badge, although the **Response Action** menu in its
  view already shows the action in force (and offers Lift).
- Lifting clears the badge once the host applies the lift.
- An action that names only **devices** puts no badge on sessions: it is enforced on
  those devices, and its reach is in the action's `hosts` / `applied` (§5).
- A session under both shows **Under Isolation** (isolation wins).

---

## 9. Activity events

Activity → Events, category **AI Edge** (`34-event-catalogue.md`):

| Event | When |
|---|---|
| **Response action applied** (`ai.control.created`) | an administrator added an action; meta `effect`, `reason`, `scope`, `origin`, `expires_at` |
| **Response action applied by a guardrail** (`ai.control.raised`) | Netzilo isolated or inspected a session on its own; initiator Netzilo System, `origin` names the rule |
| **Response action updated** (`ai.control.updated`) | an administrator edited one |
| **Response action lifted** (`ai.control.lifted`) | lifted; meta `lift_reason` |
| **Response action deleted** (`ai.control.deleted`) | deleted |
| **AI session deleted** (`ai.session.deleted`) | an administrator deleted a session and its records |
| **AI blocked** (`ai.blocked`) | each refused call; engine `control`, the reason is the response-action line (§7) |

---

## 10. Incident playbook — contain first, investigate, lift

1. **Contain fast with an isolation.** Isolate the narrowest scope that surely covers the
   threat: the session if one session is hijacked; the **user** if their account or
   device may be compromised; the **agent** (or a pattern) if a tool or SDK agent is
   misbehaving across users; the **group** if a team is targeted (a poisoned vendor email
   reaching Finance); **All AI activity** only for an account-wide emergency. Give a
   reason people can act on and, if the window is known, an expiry. From a session:
   **Response Action** → Isolate session / Isolate user / Isolate agent.
2. **Confirm it holds.** The sessions show **Under Isolation** (§8); `GET
   /api/ai/controls` shows `applied` equal to `hosts`; new attempts appear as **AI
   blocked** with engine `control`. A covered device that is offline gets it on
   reconnect; check Endpoint → Peers.
3. **Investigate the session.** Open it in Edge → Sessions: the trajectory (prompts,
   tool calls, results, verdicts), MCP calls, files, the behaviour graph and kill chains
   (`30-activity-reports-and-integrations.md` §1a, §3); the guardrail events of the same
   session (Activity → Events, category AI Edge); for a session Netzilo contained on its
   own, the **Response action applied by a guardrail** events and the Gate block that was
   the second strike. Preserve evidence before deleting any session.
4. **Widen or narrow.** Edit the action rather than stacking new ones; add a user's other
   devices' sessions by isolating the user; if the cause is broader than AI (a stolen
   device or credential), also follow `15-incident-response-and-recovery.md`.
5. **Lift** when the cause is removed (Actions → Lift, with a reason). Lifting a session
   Netzilo contained tells its guardrails not to contain that session again. Then tighten
   the guardrail or filter that should have caught it earlier (`28` §6).

---

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No **Under Isolation** badge after adding an action | the host carrying the session has not applied it: device offline, gateway not reaching management, browser not yet refreshed (up to 30 s) | wait for the host's interval (§6); check the device is connected (Endpoint → Peers), the gateway's log (`controls version N`), the extension signed in; read `hosts` / `applied` of the action |
| Badge missing only for browser sessions | extension older than **5.2.578**, or not signed in | update the extension; sign in from its popup (`49` §10) |
| Badge missing for a device's sessions, calls still pass | client older than v5.3.590 (or an SDK agent older than 5.2.2); the app is not inspected on that device (not in an endpoint filter's Agents) | update; an app Netzilo does not inspect is not stopped by any action (§1) |
| An **agent pattern** isolates nothing on some hosts | an older host treats a pattern as a literal agent name | update the host, or name the exact agent ID meanwhile |
| A device action shows no badges | by design: device-only actions name no session (§8) | read the action's `applied`; look for **AI blocked** events with engine `control` |
| Calls still pass right after **Add Action** | the gateway takes up to 2 s, a browser up to 30 s | wait, then retry once; a device must be connected |
| Still blocked after **Lift** | the host has not applied the lift yet, or another action covers the call (a group, an agent, all) | wait for the interval; `GET /api/ai/sessions?control=kill` and the session's `action` name what still holds it |
| A guardrail keeps isolating sessions | Cruise Control Containment working as designed; its reason names the tool and the likely goal | lift with a reason; review Gate's blocks for that tool; narrow the filters binding the rules (`28`) |
| Cruise Control Inspection / Containment never act | not bound in the same filters as Gate and Patrol; hosts too old (`controls` capability missing, the rules are skipped) | bind all four together; update hosts (§2) |
| `412` when adding | 500 administrator actions in force | lift or delete old ones; prefer broader scopes |
| A user isolated by group membership is still blocked after leaving the group | the device or browser has not synced since | `netzilo refresh` on the device, or wait for the next sync |

---

## 12. Limits to state before a customer discovers them

- **An action stops AI that passes through Netzilo**, not AI on an unmanaged device or an
  app the device does not inspect (§1). Combine with endpoint filters that cover the AI
  apps in use, and with the AI Gateway for agents.
- **Hosts must be current** (client and gateway v5.3.590, browser extension 5.2.578, Agent
  SDK 5.2.2); older hosts ignore response actions.
- **Enforcement is as fast as each host's delivery**: a device at once, the gateway 2 s, a
  browser up to 30 s; an offline device on reconnect.
- **Inspection alone does nothing visible**: it matters only through guardrails that read
  it (§2).
- **At most 500 administrator actions in force** per account.
- **Session verdicts are not response actions.** A guardrail's own session verdict (`10`
  §8) is invisible here and cannot be lifted from the dashboard; a response action is
  visible, audited and lifted by an administrator.
