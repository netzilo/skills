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
chars: 23027
sections:
- id: '1'
  title: What a regular user can see through the API
  chars: 6358
- id: '2'
  title: What you may do on their device
  chars: 2164
- id: '3'
  title: The questions a regular user brings, and where each one ends
  chars: 10738
- id: '4'
  title: Ending on the administrator's side of the boundary
  chars: 1736
- id: '5'
  title: What not to do
  chars: 866
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
working on somebody else's machine; its §1 approval table collapses here to one case, the
person's own device, while your own consent obligation stays whole (see §2 below).

---

## 1. What a regular user can see through the API

Management enforces the caller's own permissions on every call you make with
`netzilo_api`. The rule is one sentence: **a regular user's REST view is the union, over the
peers they own, of what each of those peers receives from Management.** What you read
here is what the person's devices themselves hold, no more.

| Call | What comes back |
|---|---|
| `GET /api/users?self=true` | A list with one entry, the person: id, name, e-mail, role `user`, their groups (`auto_groups`), and `permissions` — `dashboard_view` (`limited`, or `blocked` when the administrator disabled the portal) and `ai_assistant: true` (or you would not be here). `GET /api/users/current` is refused for a regular user; `GET /api/users` without the filter returns the same single entry |
| `GET /api/peers` | **Their own devices only**: id, name, IP, `connected`, OS, version, `user_id` equal to theirs, `last_seen`, groups. Other people's devices are not in the list |
| `GET /api/peers/{id}` | One of their devices, same shape; 403 for anyone else's |
| `GET /api/policies`, `/api/policies/{id}` | The policies whose source or destination groups contain one of their peers. A policy outside that set answers 404 |
| `GET /api/groups`, `/api/groups/{id}` | The groups those policies and routes refer to, plus the groups their peers are in, each holding only the peers the person may know about (their own, the ones they may reach, the routing peers). The names you need to make the other lists readable |
| `GET /api/routes`, `/api/routes/{id}` | The routes their peers receive |
| `GET /api/dns/nameservers`, `/api/dns/settings` | The nameserver groups distributed to their peers; the DNS settings with only their own groups among the disabled ones |
| `GET /api/posture-checks`, `/api/posture-checks/{id}` | The checks the policies on their peers apply |
| `GET /api/profiles` | The profiles their peers receive |
| `GET /api/support/devices/{id}`, `/tools` | The device summary for the tools (`online`, `tools_supported`, `owned_by_caller: true`) and the tool catalog |
| `GET /api/edge/filters` | Their enabled **endpoint** filters only (what the extension reads). Gateway grants are not in it: they come from `GET /api/users/current/ai-access` |
| `GET /api/users/current/ai-access` | The Workplace's **Agentic Access** view: their gateways with models, their MCP servers with connection state, bundles, and the guardrails that apply. Both lists empty = no gateway filter grants them anything, and the tab is hidden |
| `GET /api/users/current/mcp-connections`, and the connect / complete / headers / disconnect calls under it | Their own sign-ins and header values for per-user MCP servers (`not_connected`, `needs_reauth`, connected); the writes a user makes from the MCP server dialog (`47-agentic-access-workplace.md` §3, `46-ai-gateway-mcp-servers-and-bundles.md` §4) |
| `GET/POST/DELETE /api/users/{their id}/tokens` | Their own personal access tokens; the Workplace creates one named **AI Gateway** with scope `mcp` (90 days) for gateway use — that scope identifies them to gateways and reads nothing else. An application they approved on the consent page (Claude Desktop's **Sign in with your organization**) holds one named **<app> (MCP)**, for example **Claude (MCP)**, same scope, renewed by the application itself; deleting it signs that application out |
| `GET /api/users/current/published-apps` | The published applications the person may open (the Workplace's Applications tiles): name, address, `url`. Empty when publishing is off for the tenant or none of their groups is admitted (`44-published-applications.md` §12) |
| `GET /api/users/{their id}/gateway-sessions` | Their browser sessions through a Netzilo gateway (`vp-<n>-PROXY`) with `connected`, browser and OS: the Workplace page's **Private access** status (`43-clientless-access-gateway.md` §3.5, §10.3). Another user's id answers 403. (Not the AI gateway: for that, `ai-access` above) |
| `GET /api/ai/sessions`, `/api/ai/sessions/session`, `/trajectory`, `/message` | Their own AI sessions only (recorded on their devices and through the AI Gateway), with the captured conversation; `user=` is always themselves, and another person's session answers 404. The **AI Sessions** page is for admins only; regular users read their sessions through the API |
| `GET /api/aidr/sessions`, `GET /api/aidr/sources` | Their own AI sessions and sources only: the sessions recorded on their devices and in their browser (a source of `kind: browser`, with the `device` it runs on and the `capabilities` the browser offers). Without `scope` the list is narrowed to theirs; `scope=session:<id>` for someone else's session answers 403 (`session is not one of yours`); `scope=source:<id>` must be one of their peers or their browser |

When the administrator has **disabled the portal for regular users** (Settings → Permissions),
every list above is empty: the person's client still works,
but this seat can see nothing. Say so and hand the case to the administrator (§4).

Everything else answers **403**: events, reports, stats, setup keys, other users, account
settings, integrations, and the Edge objects — providers, guardrails, limits, MCP servers
and filters as objects (what a user is granted is readable only through `ai-access`
above). A 403 or a 404 on an object is the boundary,
not a fault. Say in one sentence that the administrator controls that object, and carry on
with what you can see. Never retry with a different path in the hope of finding a way around.
Nothing a regular user asks for needs a credential beyond the session they are already in:
do not ask them for another token, and never for an administrator's login or token to get
past a 403 (`SKILL.md` rule 6). If they paste a credential anyway, do not repeat it, do not
use it to widen their access, and tell them to revoke it.

Writes through the API are refused for a regular user with three exceptions (their own
personal access tokens, their own MCP sign-ins and header values through
`mcp-connections`, and the Edge event and AI scan endpoints the client itself calls).
The first two are what the Workplace's Agentic Access page does on their behalf; do not
propose any other API write to a regular user. What else they can change is on their
device, through the device tools.

## 2. What you may do on their device

The device tools (`device_tools`, `device_run`) work for a regular user exactly as for an
administrator on **their own** device, and refuse anyone else's with 403. Ownership is the
peer's `user_id`; the summary line from `device_tools` says "(yours)". Because the device
is theirs, the platform's approval behaviour in `36-device-tools.md` §1 has one case only,
and your own obligation (`SKILL.md` rule 3) is unchanged:

- **Diagnostics (`diag.*`) run immediately.** Status, configuration, routes, route match,
  DNS as the tunnel resolves it, probe, posture, log tail, log search, debug bundle.
- **Changes (`mod.*`) and `shell.run` also run immediately** — the platform does not
  interpose an approval on a person's own machine. That makes *your* discipline the only
  gate: read before you change (`36-device-tools.md` §6), say what you are about to do and
  why before you do it, one change at a time, and verify after. Never run `shell.run`
  for something a `diag.*` tool answers (`36-device-tools.md` §7).
- **Destructive changes need the person's explicit "yes" first**, even though nothing
  would stop you: anything that logs the device out, disconnects it, deletes, wipes or
  reinstalls. Ask in the chat, wait for the answer, then run it.
- **`mod.disconnect` ends the conversation's reach.** The client goes down, the person is
  signed out, and the device answers nothing until they sign in again themselves. Say so,
  get the "yes", and prefer `mod.refresh`. Never stop or restart the Netzilo service to
  "reset" the connection: that also logs the device out (`36-device-tools.md` §6).
- **A device that has lost its management connection cannot be reached at all** —
  offline, stopped, or its login expired. Work from `GET /api/peers` (`connected`,
  `last_seen`, `login_expired`) and ask the person for `netzilo status` output or a
  screenshot of the Netzilo window (`36-device-tools.md` §3).

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
| "I can't log in" / "it keeps asking me to sign in" | `GET /api/peers` — `login_expired` and `connected` on their device; `GET /api/users?self=true` works at all (a blocked user gets nothing). A device that needs a login usually has no management connection, so device tools cannot reach it: ask for `netzilo status` output (it shows `Daemon status: NeedsLogin` or `LoginFailed`) or a screenshot of the Netzilo window. If the device is reachable, `diag.status` reports the same in its `status` string (for example `"NeedsLogin"`) | Their side if it is a browser or the wrong identity provider account; **administrator** if the login expired under a policy they cannot change, or the user is blocked |
| "Netzilo is not connected" / "red icon" | if `device_tools` reaches the device: `diag.status` (management, signal, relay state), then `diag.logs` tail. If it says offline, the management connection is down: `last_seen` from `GET /api/peers`, and ask for `netzilo status -d` output or a screenshot | Device: network, captive portal, VPN conflict, service not running (`38-device-diagnosis-method.md` §4, *not connected*) |
| "I can't reach X" | `diag.route_match` for X, `diag.dns` for its name, `diag.probe`; `GET /api/policies` and `/api/routes` show whether anything reaching X applies to their device at all | Device if the name does not resolve or the route is missing locally; **administrator** if the route matches but the probe is refused (a policy, a group the person is not in, a posture check) |
| "Some site is slow" / "everything is slow since Netzilo" | `diag.status` — relayed or direct; `diag.route_match` — is that traffic even going through Netzilo | Device for a relayed connection or a broad route; note it for the administrator if all peers relay |
| "A posture warning" / "my device is non-compliant" | `diag.posture` — the exact signal and its value on this OS (`38-device-diagnosis-method.md` §3 for what each signal means per platform) | Device: update the OS, turn on the disk encryption or screen lock the warning names; **administrator** if the check cannot be true on this platform |
| "What is Netzilo doing on my laptop?" / "what does it collect?" | Nothing to run | Answer from `17-end-user-guide.md` §4 and `14-data-handling-and-privacy.md`; no tool needed |
| "It worked yesterday" | `diag.grep` around the time it stopped; `diag.status` for a version change | Either; the log says which (`38-device-diagnosis-method.md` §4, *worked yesterday*) |
| "My workspace won't open" / "the secure browser is missing or blocked" / anything about Enterprise Workspace, Enterprise Browser or Disposable Browser | `GET /api/profiles` — which profiles their device receives; then the workspace troubleshooting steps | `26-profiles-secure-workplace.md` §9 "Troubleshooting the Workspace"; **administrator** if no profile reaches their device |
| "I can't open <a published application>" / "the tile is missing" / "Access Denied" / "Access Failed" / "There is no application at this address" (an address of its own, any browser, nothing installed) | `GET /api/users/current/published-apps` — is the address in their list; their `vp-<n>-RPROXY` peer in `GET /api/peers` (connected). No device tools for a browser | Their side only for cookies blocked on the address or an old link; **administrator** for the groups, the tenant switch, the policy to the target, or the address (`44-published-applications.md` §12) |
| "I can't copy / print / download / upload" / "a watermark" / "Access restricted" inside a published application | the Netzilo notice text they saw; which application | by design: the application's restrictions (`44-published-applications.md` §4.2). The person cannot change them and should not try to work around them; if a task needs it, the message to the administrator names the application, the action and why |
| "Access Denied — because posture check … failed" / "Additional Protection Required" at a published application | the reason text the dialog shows; is the Netzilo client on their device running and current (a Workspace's client too); are they in the Enterprise Browser or another browser; the extension popup | Their side: start or update the client, use the browser the check asks for, add or connect the extension, fix the named setting, then Workplace logout and open again. **Administrator** when the check cannot be met by that audience (`44-published-applications.md` §4.1, §12) |
| "Our internal site opens by IP but not by name" / "it works in Chrome but not in Firefox" / "the browser says Secure Connection Failed for an http site" | their gateway session or peer in `GET /api/peers` (connected); ask whether the address bar shows `https://` after typing `http://`, and whether the IP or another browser works. No device tools for a browser | Their side, with the one-site browser reset of `43-clientless-access-gateway.md` §11.3a once all four conditions hold (ask before: it clears that site's cookies in that browser); **administrator** for what served the name over HTTPS outside the tunnel |
| "Private access says unavailable" / "I can't open our internal sites in the browser" (browser extension, no Netzilo app) | Ask what hovering over **unavailable** shows; their `vp-<n>-PROXY` session in `GET /api/peers` (connected, public IP). There are no device tools for a browser | Their side for Firefox private-window access or a proxy owned by another extension; **administrator** for an operating-system proxy the profile does not name, the account switch, the profile, the gateway port, or a policy (`43-clientless-access-gateway.md` §11.2) |
| "I have no Agentic Access tab" / "where is the AI gateway?" | `GET /api/users/current/ai-access` — `gateways` and `mcp` both empty? | **Administrator**: no gateway filter targets a group they are in, or it grants no gateway address and no MCP server (`47-agentic-access-workplace.md` §5) |
| "My coding agent cannot reach the model" / 400 (older gateways 403) `no model is granted to this user` or `model X is not granted` | `ai-access` — the models listed under their gateway; is the one the tool asks for among them | **Administrator**: the gateway filter grants the models; the user can switch to a granted model meanwhile (`47` §5) |
| 429 or 402 from the gateway / "limit reached" | the error body names the limit; `ai-access` lists the guardrails but not the limits as objects | **Administrator** raises the limit, or the user waits for the window to reset (`47` §5, `45-ai-gateway-providers-and-limits.md` §2.2) |
| An MCP server shows **Needs Attention** / "it asks me to sign in" / a tool answers `Connect <server> in your Workplace…` | `GET /api/users/current/mcp-connections` → `not_connected` or `needs_reauth` for that server | Their side: open the server's card, **Connect** or **Reconnect** (`47` §3). **Administrator** when the server uses the admin's shared sign-in ("An admin has not connected this server yet") |
| A gateway card shows **Offline** | `ai-access` has the address; ask whether `curl <gateway>/v1/models -H "Authorization: Bearer <token>"` works from their machine (never ask for the token itself) | **Administrator**: the gateway is down, started without the Workplace's address, or not reachable from the user's network (`47` §5, `27-ai-gateway.md` §5) |
| 401 `a Netzilo credential is required` from the gateway | the token: expired (90 days), deleted under Access Tokens, mistyped, or passed as an API key instead of a bearer/auth token | Their side: create a new token in the gateway dialog, and for Anthropic clients pass it as the auth token (`47` §5) |
| "My browser extension says Inactive" / "nothing is redacted in ChatGPT" | the popup: are they signed in (**Login**), what the **Protection** line says; `GET /api/edge/filters?os=browser` — is any endpoint filter with **Browser** among its operating systems in the list; `GET /api/aidr/sources` — does their browser appear with `kind: browser`. No device tools for a browser | Their side: sign in from the popup, update the extension; in Safari enable the **Netzilo Browser** extension and allow it on all websites. **Administrator** when no endpoint filter listing **Browser** targets their groups, or that filter binds no guardrail (`49-browser-extension-aidr.md`) |
| "The extension says the desktop client governs this browser" | `GET /api/peers` — their device on that computer is connected. Nothing else to check | Expected: the Netzilo client on that device inspects the AI sites itself and the extension stands down; the same rules apply through the client. On Linux the client does not take over the browser, so the extension stays in charge there (`49-browser-extension-aidr.md`) |
| "Claude Desktop sign-in fails" — "gateway SSO discovery failed: 401", "Gateway returned HTTP 405 … /v1/messages", "gateway SSO metadata invalid: token_endpoint: must be same-origin …", "server does not advertise device_authorization_endpoint", "gateway SSO device init failed: HTTP 400" | the endpoint they typed against the **Anthropic API** address in `ai-access`: it must end in `/anthropic` (401 and 405 mean it does not) | Their side for the address; **administrator** for the other three: the gateway or the server predates the device sign-in and needs an upgrade (`47-agentic-access-workplace.md` §5, `46-ai-gateway-mcp-servers-and-bundles.md` §6) |
| "I approved but Claude still waits" | did the page reach **Access allowed**; how long ago — the sign-in expires 10 minutes after Claude started it and the approval is collected within 5 minutes; a server restart in between drops it | Their side: start again from Claude (**Sign in with your organization**) and approve once more; **administrator** if every attempt ends the same way (`47` §5, `46` §6) |
| "A token named Claude (MCP) appeared under my Access Tokens — what is it" | `GET /api/users/{their id}/tokens` — a token named **<app> (MCP)**, scope `mcp`, created the moment they pressed **Allow** for that application | Their side, expected: it is the application's sign-in and it renews itself; deleting it signs the application out and nothing else changes (`47` §5, `46` §6) |

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
         macOS", "reset my login expiry", "grant my group the model <name> on the
         AI gateway <name>" or "raise the limit <name> that refuses my requests">
```

For a gateway grant, add what `GET /api/users/current/ai-access` showed (the gateways
and models listed, or that both lists were empty) in place of a device line; there is no
device to describe.

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
  a `mod.*` or `shell.run` call runs at once; announce and justify it before you run it,
  and for anything destructive wait for their explicit "yes" (§2).
- Do not send the person to the dashboard pages a regular user cannot open. Their view is
  the Workplace page; instructions like "go to Network → Policies" belong in the message
  to the administrator, not to them.
