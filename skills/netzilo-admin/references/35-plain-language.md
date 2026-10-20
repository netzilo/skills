---
id: '35'
title: Plain language — what to call things when you talk to an admin
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 9926
sections:
- id: '1'
  title: When an identifier belongs in the answer
  chars: 817
- id: '2'
  title: Areas of the product
  chars: 5965
- id: '3'
  title: 'Objects: names, not ids'
  chars: 599
- id: '4'
  title: 'Events: say the activity, not the code'
  chars: 783
- id: '5'
  title: Rewrites
  chars: 1045
---
# Plain language — what to call things when you talk to an admin

**Audience:** any agent or engineer reporting Netzilo findings to a customer. Read this
once; it changes how every answer reads.

An admin knows their product through its dashboard: pages with names, objects with names,
events with sentences. They do not know your transport. When an answer is written in API
paths, activity codes and object ids, the admin has to translate it back before they can
act — and most of them cannot. Worse, it reads as though the assistant is describing its
own plumbing rather than their network.

The rule is simple: **say what the admin would say, and keep the identifiers for the
places that need identifiers.**

---

## 1. When an identifier belongs in the answer

Name things in prose. Use the exact API path, activity code or object id only when:

- **you are proposing a change** — an approval must show the exact method, path and body,
  because that is what will run;
- **the admin asked how**, or asked for something they can paste into a script;
- **you are telling them what to search for themselves** — a filter value on the Activity
  page, a code for a detection rule;
- **the name is ambiguous and the id resolves it** — two peers called `laptop`, say, where
  you then give the id once and go back to the name.

Everywhere else, an identifier is noise. If you catch yourself writing a path to justify
that you looked something up, delete it: "I checked the profile" is the claim, and the
admin can ask how if they care.

## 2. Areas of the product

Where an admin finds each thing, and what to call it. Navigation names come from the
dashboard; if a customer's build shows a different label, theirs wins.

| Say this | Where they find it | Endpoint behind it |
|---|---|---|
| the dashboard home (tiles Users, Devices, Agents, Tokens; Agentic Activity) | Dashboard | `/api/stats`, `/api/summary` |
| a peer / a device | Endpoint → Peers | `/api/peers` |
| a setup key | Endpoint → Setup Keys | `/api/setup-keys` |
| a posture check | Endpoint → Posture Checks | `/api/posture-checks` |
| a profile (Workspace, Enterprise Browser, Disposable Browser, Extension) | Endpoint → Profiles | `/api/profiles` |
| an access control policy | Network → Policies | `/api/policies` |
| a group | used by policies, peers, users and keys throughout | `/api/groups` |
| a network route / an exit node | Network → Routes | `/api/routes` |
| a published application | Network → Applications | `/api/published-apps` |
| a nameserver / DNS settings | Network → DNS (Servers \| Settings tabs) | `/api/dns/nameservers`, `/api/dns/settings` |
| a user; a service account ("agent") | Team → Users; Team → Agents | `/api/users` |
| account settings, groups, permissions, the plan, the tenant | Settings (tabs Authentication, Groups, Permissions, Plans & Billing (Netzilo Cloud only), Tenant) | `/api/accounts`, `/api/groups`, `/api/tenant` |
| a provider (the gateway's model catalogue) | Edge → Providers | `/api/edge/providers` |
| an MCP server | Edge → MCP → MCP Servers tab | `/api/edge/mcp-servers` |
| an MCP bundle | Edge → MCP → MCP Bundles tab | `/api/edge/virtual-mcps` |
| a guardrail (detection rule) | Edge → Guardrails | `/api/edge/guardrails` |
| a limit (spend, token or request quota) | Edge → Limits | `/api/edge/limits` |
| a filter — an endpoint filter (devices) or a gateway filter (users) | Edge → Filters | `/api/edge/filters` |
| the user's gateways and MCP servers, their AI Gateway token | Workplace → Agentic Access | `/api/users/current/ai-access` |
| an event / the activity log | Activity → Events | `/api/events`, `/api/events/paginated` |
| an AI session (a recorded agent conversation, LLM or MCP) | Activity → AI Sessions; the home page's Agentic Activity, **View** | `/api/ai/sessions` |
| a report | Activity → Reports | `/api/reports` |
| an integration; the AI the dashboard itself uses | Integrations; Integrations → Artificial Intelligence | `/api/integrations`; `/api/ai/providers` |

### 2.1 AI Edge terms

Say these the way the dashboard does; the admin has never seen the old words (tools,
scanners, catalogue) in this release.

| Term | What it means |
|---|---|
| **guardrail** | a detection rule (YAML) bound by a filter; its verdict is allow, detect (report), redact, block or redirect. Formerly "scanner" — do not use that word for the object; "the AI scanner" inside a rule's `scan` action keeps its name |
| **endpoint filter** | a filter of type Endpoint: groups × operating systems (and optionally Agents) on devices; binds guardrails the Netzilo client enforces |
| **gateway filter** | a filter of type Gateway: groups of users; grants models, limits, MCP servers and bundles, lists the gateway addresses, binds guardrails the AI gateway enforces |
| **model grant** | an entry in a gateway filter's Models tab, `provider/model` or a whole provider; without one the user is refused at the gateway with "no model is granted to this user" |
| **limit** | a spend, token or request quota, applied per user per gateway; the lowest value wins when several filters apply |
| **MCP server / MCP bundle** | an admin-defined server the gateway serves at `<gateway>/mcp/<slug>`; a bundle is one endpoint that combines tools of several servers |
| **Agentic Access** | the Workplace section where a user sees their gateways and MCP servers, creates their AI Gateway token and signs in to per-user MCP servers |
| **AI Gateway** | the Netzilo AI Gateway (`netzilo-aigw`), a peer of the account that identifies callers as users and applies their gateway filters; not the clientless-access gateway on 8443, although the same binary serves both |
| **browser extension** (as an AI enforcement point) | the Netzilo extension in Chrome, Edge, Firefox or Safari running the same governance engine as the client and the gateway: it applies the endpoint filters whose Operating Systems include **Browser** to the signed-in user's AI use in the page. Say "the extension governs the browser"; it is not a device, not a peer, and not the Enterprise Browser (which bundles it) |
| **browser source** | the user's browser as an uploader of behaviour: one per user and browser under `GET /api/aidr/sources` with `kind: browser`. Say "Erin's browser" or "the browser on Erin's MacBook", not the source id |
| **tab session** | the behaviour-graph session of one browser tab on one site (its parent is the browser session); the `session_id` on browser `ai.*` events. Say "the ChatGPT tab" or "that conversation's session" |
| **Session snapshot** | the Activity entry (`aidr.graph`) that announces the first behaviour of a browser tab session ("… for <program> in the browser"); it opens the session's behaviour graph. Device entries ("… for peer <peer>") are no longer created; old ones stay. Say "the session snapshot for that tab", never the code |
| **Session trajectory available** | an Activity entry (`aidr.trajectory`) older servers created for a new AI session ("Session trajectory is available for <agent> on <peer>"); **View session** opens it. Current servers no longer create it: sessions are in Activity → AI Sessions. Say "the session entry", never the code |
| **AI session** | one conversation of one user (or setup-key peer) with one agent, recorded on the device, the gateway or both; "Seen at" names where a call was recorded |
| **MCP client** | the program that called an MCP server, by the name it gave when it connected; "Unknown client" when it gave none |

## 3. Objects: names, not ids

Peers, groups, policies, users and profiles all have names the admin chose. Use them, in
the capitalisation the admin uses. An id (`daob0dkkr4h37occqos0`) belongs in an approval
body or a follow-up call, not in a sentence — with one exception: after you create
something, giving the new id once is useful, because it is the only way they can find it
before the page refreshes.

Say "the **servers** group", not "group `daob0…`". Say "**Erin's MacBook**", not "peer
`acme-4`" — unless the hostname *is* what the admin calls it, which for enrolled devices
it often is.

## 4. Events: say the activity, not the code

Every event carries three fields: `activity` (a display name — "Code injection
detected"), `activity_code` (the stable identifier — `workspace.injection.detected`) and
`activity_category` ("Suspicious"). The display name is already in the response you are
reading. Quote it.

The full list is `references/34-event-catalogue.md`: 162 activities with their display
names, codes and categories. Use it when you are choosing a `code=` filter, and use it in
reverse when a code turns up in a log or a rule and you need to say what it means.

Categories are worth a mention when they carry the weight: *Policy Violation*,
*Data Exfiltration* and *Suspicious* tell an admin how alarmed to be, and are exactly the
words on their Activity page.

## 5. Rewrites

Before, and what to say instead:

> I can pull the actual profile (`GET /api/profiles`) that defines this container, or
> check for any `workspace.posture.check` / `workspace.injection.detected` failures.

> I can open the profile that defines this container and show its restrictions, or check
> whether it logged any posture-check failures or code-injection detections.

---

> Peer `daob0dkkr4h37occqos0` has `connected: false` and `last_seen`
> 2026-09-19T08:14:02Z.

> **Erin's MacBook** has been offline since Friday morning.

---

> I called `GET /api/policies` and found 3 objects with `enabled: true`.

> You have three active access control policies.

---

> The `setupkey.peer.add` events indicate enrollment.

> Those are devices being added with a setup key.

---

Keep the discipline in writing that survives the chat, too: a report you save, a summary
you send to support, a message an admin forwards to their security team. The identifiers
go in the appendix or the request body; the story goes in the sentences.
