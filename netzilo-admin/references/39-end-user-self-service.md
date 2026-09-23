---
id: '39'
title: 'Netzilo — Self-Service for a Regular User: their own devices, their own access'
requires:
- api
- device-tools
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 9226
sections:
- id: '1'
  title: What a regular user can see through the API
  chars: 2051
- id: '2'
  title: What you may do on their device
  chars: 1401
- id: '3'
  title: The questions a regular user brings, and where each one ends
  chars: 2439
- id: '4'
  title: Ending on the administrator's side of the boundary
  chars: 1418
- id: '5'
  title: What not to do
  chars: 801
---
# Netzilo — Self-Service for a Regular User: their own devices, their own access

**Use this when the person you are helping is not an administrator.** The AI assistant
on the Workplace page is opened by an employee whose laptop runs the Netzilo client. They
reached you because the account's administrator switched the assistant on for their group
(Settings → Permissions → *Allow regular users to use the AI Assistant*, plus an allowed
group). Every other file in this skill set assumes an administrator's permissions. This
one tells you what changes when they are not: what the person can see, what you may do on
their behalf, where the administrator's boundary runs, and how to hand a problem across
that boundary well.

Read this file first in a regular user's session, then the card for each device tool you
are about to use in `37-device-tool-reference.md` and the playbook for the symptom in
`38-device-diagnosis-method.md`. `36-device-tools.md` is written for an administrator
working on somebody else's machine; its §1 consent rule collapses here to one case, the
person's own device (see §2 below).

---

## 1. What a regular user can see through the API

Management enforces the caller's own permissions on every call you make with
`netzilo_api`. A regular user's view is small and exact:

| Call | What comes back |
|---|---|
| `GET /api/users?self=true` | A list with one entry, the person: id, name, e-mail, role `user`, their groups (`auto_groups`), and `permissions` — `dashboard_view` (`limited`, or `blocked` when the administrator disabled the portal) and `ai_assistant: true` (or you would not be here). `GET /api/users/current` is refused for a regular user; `GET /api/users` without the filter returns the same single entry |
| `GET /api/peers` | **Their own devices only**: id, name, IP, `connected`, OS, version, `user_id` equal to theirs, `last_seen`, groups. Other people's devices are not in the list; a peer id you are given that is not here belongs to someone else |
| `GET /api/peers/{id}` | One of their devices, same shape; 403 or 404 for anyone else's |
| `GET /api/support/devices/{id}` | The device summary for the tools: `online`, `tools_supported`, `owned_by_caller: true` |
| `GET /api/support/devices/{id}/tools` | The device's tool catalog |
| `GET /api/edge/filters` | The Edge filters that apply to them (read-only, expanded) |

Everything else answers **403**: groups, policies, routes, DNS settings, posture checks,
events, reports, stats, setup keys, other users, account settings, integrations. A 403 is
the boundary, not a fault. Say in one sentence that the administrator controls that
object, and carry on with what you can see. Never retry a 403 with a different path in
the hope of finding a way around, and never ask the person for another token, an
administrator's login or any credential.

Writes through the API are refused for a regular user with two exceptions that do not
matter for support (their own personal access tokens, and the Edge event and AI scan
endpoints the client itself calls). Do not propose an API write to a regular user. What
they can change is on their device, through the device tools.

## 2. What you may do on their device

The device tools (`device_tools`, `device_run`) work for a regular user exactly as for an
administrator on **their own** device, and refuse anyone else's with 403. Ownership is the
peer's `user_id`; the summary line from `device_tools` says "(yours)". Because the device
is theirs, the consent rule of `36-device-tools.md` §1 has one case only:

- **Diagnostics (`diag.*`) run immediately.** Status, configuration, routes, route match,
  DNS as the tunnel resolves it, probe, posture, log tail, log search, debug bundle.
- **Changes (`mod.*`) and `shell.run` also run immediately** — the platform does not
  interpose an approval on a person's own machine. That makes *your* discipline the only
  gate: read before you change (`36-device-tools.md` §6), say what you are about to do and
  why in the same message, one change at a time, and verify after. Never run `shell.run`
  for something a `diag.*` tool answers (`36-device-tools.md` §7).
- **`mod.disconnect` ends the conversation's reach.** The client goes down and the device
  answers nothing until the person brings it back up themselves. Say so before you use
  it, and prefer `mod.refresh`.

Load the tool's card in `37-device-tool-reference.md` before the first call; §0 there is
the result envelope every tool shares, including what `status: unsupported`, `timeout`
and a non-zero `exit_code` mean.

## 3. The questions a regular user brings, and where each one ends

The person describes a symptom in their own words; `17-end-user-guide.md` §3 translates
the common phrasings. The table says which side of the boundary the cause usually sits
on, so you know early whether the ending is a fix on the device or a message to the
administrator.

| They say | Check first | Where it usually ends |
|---|---|---|
| "I can't log in" / "it keeps asking me to sign in" | `diag.status` — `needs_login` and login-expiry state; `GET /api/users?self=true` works at all (a blocked user gets nothing) | Their side if it is a browser or the wrong identity provider account; **administrator** if the login expired under a policy they cannot change, or the user is blocked |
| "Netzilo is not connected" / "red icon" | `diag.status` (management, signal, relay reachability), then `diag.logs` tail | Device: network, captive portal, VPN conflict, service not running (`38-device-diagnosis-method.md` §4, *not connected*) |
| "I can't reach X" | `diag.route_match` for X, `diag.dns` for its name, `diag.probe` | Device if the name does not resolve or the route is missing locally; **administrator** if the route matches but the probe is refused (a policy, a group the person is not in, a posture check) |
| "Some site is slow" / "everything is slow since Netzilo" | `diag.status` — relayed or direct; `diag.route_match` — is that traffic even going through Netzilo | Device for a relayed connection or a broad route; note it for the administrator if all peers relay |
| "A posture warning" / "my device is non-compliant" | `diag.posture` — the exact signal and its value on this OS (`38-device-diagnosis-method.md` §3 for what each signal means per platform) | Device: update the OS, turn on the disk encryption or screen lock the warning names; **administrator** if the check cannot be true on this platform |
| "What is Netzilo doing on my laptop?" / "what does it collect?" | Nothing to run | Answer from `17-end-user-guide.md` §4 and `14-data-handling-and-privacy.md`; no tool needed |
| "It worked yesterday" | `diag.grep` around the time it stopped; `diag.status` for a version change | Either; the log says which (`38-device-diagnosis-method.md` §4, *worked yesterday*) |

Work the symptom with the loop in `38-device-diagnosis-method.md` §2 and stop at the
tree's stop condition. The trees end at a cause; §4 below says how to end the conversation.

## 4. Ending on the administrator's side of the boundary

When the evidence points at something only an administrator can change, do not stop at
"ask your admin". Write the message they can send, so the administrator opens it and knows
what to do. Four lines:

```
Device: <device name> (<peer id>), <OS>, Netzilo <version>, owner <e-mail>
Symptom: <what fails, since when, how often>
What the device shows: <concrete lines: the route that matched, the probe result,
                        the posture signal and value, the log line with its time>
Please: <the one change asked for, in the administrator's words — "add me to the
         group that can reach <resource>", "review the posture check <name> for
         macOS", "reset my login expiry">
```

Concrete data is the whole value of this message: the administrator will otherwise
re-run the same checks with their own tools. Use plain page names from
`35-plain-language.md`; the administrator sees "Network → Policies", not a table name.
Do not include tokens, keys or anything from the person's credentials.

There is no escalation to Netzilo Level 3 from this seat. A regular user reports to
their administrator; the administrator decides whether to escalate. If you believe the
cause is product behaviour rather than configuration, say so in the message to the
administrator with the evidence, and name `12-escalation-package.md` as what they would
use.

## 5. What not to do

- Do not explain account-wide state you cannot see. "Your administrator's policy blocks
  this" is a guess unless a probe or a 403 on a resource shows it; say what you observed.
- Do not enumerate other people or devices. Nothing you can call returns them, and a peer
  id the person pastes that is not theirs is answered with 403; say that it is not one of
  their devices and stop.
- Do not treat the absence of an approval prompt as licence. On the person's own device
  a `mod.*` or `shell.run` call runs at once; announce and justify it in the same message.
- Do not send the person to the dashboard pages a regular user cannot open. Their view is
  the Workplace page; instructions like "go to Network → Policies" belong in the message
  to the administrator, not to them.
