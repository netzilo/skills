---
id: '30'
title: Admin Skill — Activity Events, Reports, Dashboard Home and Integrations
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 34840
sections:
- id: '1'
  title: Activity → Events
  chars: 7012
- id: 1a-activity-ai-sessions
  title: 1a. Activity → AI Sessions
  chars: 2360
- id: '2'
  title: Reports
  chars: 3523
- id: '3'
  title: Dashboard home
  chars: 6455
- id: '4'
  title: Integrations
  chars: 7913
- id: '5'
  title: Procedures
  chars: 1914
- id: '6'
  title: Diagnosis
  chars: 4677
---
# Admin Skill — Activity Events, Reports, Dashboard Home and Integrations

**Dashboard:** Activity → **Events** (`/activity`), Activity → **AI Sessions**
(`/ai-sessions`), Activity → **Reports** (`/reports`), **Dashboard** (`/dashboard`),
**Integrations** (`/integrations`). **API:** `/api/events/paginated`, `/api/ai/sessions`,
`/api/reports`, `/api/stats`, `/api/integrations`, `/api/event-streaming`,
`/api/smartsearch`.

This is the evidence layer: every administrative change, access decision, DLP action and
AI verdict lands here. Use it to prove what happened, to tune policies, and to feed a
SIEM.

Pull evidence through the API rather than reading the screen: the dashboard's CSV export
covers only the page on display, while `GET /api/events/paginated` returns up to 1000
rows per call with filters. Ask the customer for a token as described in
`00-operator-playbook.md` §4.1 — a read-only agent token is enough for everything in
this file except changing integrations.

---

## 1. Activity → Events

Header shows the total count. Two status cards link to Integrations: **Event Streaming**
(Enabled when an S3/Min.io target exists) and **AI Insights** (Enabled when an AI
provider is configured).

Controls:

| Control | Behaviour |
|---|---|
| Search box | keyword search ranked by relevance ("Ranked by relevance"); with AI Insights enabled, the ✦ button runs **AI Smart Search** in natural language ("Who uploaded a file to Dropbox last week?") and stores the answer as an `ai.insight` event with cited events/recordings |
| Date range | default last 14 days |
| Event types | multi-select grouped by category: Administration, Access Control, Data Exfiltration, Policy Violation, Suspicious, Investigation, AI Edge; its search matches the event name and the code. It also lists codes that are no longer recorded (`rule.*`), so old rows stay filterable |
| User | single user (or "Netzilo System") |
| Rows per page | 10 / 25 / 50 / 100 (server-side pagination) |
| Download CSV | exports the **current page** only: Timestamp, User, Email, Event (code), Source, Target, More Information |
| Reset filters | clears everything |

Row anatomy: category icon with +/×/change badge, initiator (name, e-mail; "System" for
automatic actions; hover for location when known), timestamp, description, copy raw JSON
(hover). Special rows: `session.recorded` → play the recording; `aidr.trajectory`
("Session trajectory is available for `<agent>` on `<peer>`") → **View session** (opens it
in the Agentic Activity window, §3); `aidr.graph` ("Session snapshot") → **View behavior
graph** (now created for browser tab sessions only; device rows from earlier stay);
events with a kill chain → **View kill chain**; `ai.insight` → AI answer with citation
cards.

Event categories and the most useful codes:

| Category | Codes |
|---|---|
| Administration | `user.peer.add`, `setupkey.peer.add`, `user.peer.delete`, `peer.rename`, `peer.group.add/delete`, `peer.ssh.enable/disable`, `peer.login.expiration.enable/disable`, `peer.login.expire`, `peer.approve`, `policy.add/update/delete`, `group.add/update/delete`, `route.add/update/delete`, `nameserver.group.*`, `dns.setting.*`, `setupkey.add/update/revoke/overuse/deleted`, `user.invite/join/block/unblock/delete`, `user.role.update`, `user.group.add/delete`, `service.user.create/delete`, `personal.access.token.create/delete`, `account.setting.*`, `transferred.owner.role`, `posture.check.created/updated/deleted`, `profile.created/updated/removed`, `guardrail.*`, `filter.*`, `gateway_provider.*`, `gateway_limit.*`, `gateway_mcp_server.*`, `gateway_virtual_mcp.*`, `published_app.created/updated/removed`, `ai.provider.*`, `integration.*`, `subscription.updated`, `tenant.updated`, `report.*`, `dashboard.login` |
| Access Control | `peer.access.granted`, `peer.access.blocked`, `peer.access.target`, `peer.access.target.blocked`, `browser.url.access`, `user.login`, `user.logout`, `workspace.app.started`, `session.recorded`, `gateway.credential_refused`, `mcp.connected`, `mcp.disconnected`, `mcp.reauth_required`, `published_app.access_allowed`, `published_app.access_not_admitted` |
| Data Exfiltration | `browser.data.redacted`, `browser.data.print.blocked`, `browser.data.clipboard.blocked`, `browser.download.content`, `browser.data.classified`, `browser.data.code.upload.blocked`, `browser.data.screenshot.blocked`, `workspace.print.blocked` |
| Policy Violation | `browser.download.file`, `browser.upload.file`, `browser.url.blocked`, `browser.isolation.*.required`, `browser.posture.check`, `workspace.posture.check`, `browser.data.code.redacted`, `browser.exception.request`, `published_app.access_denied` |
| Suspicious | `workspace.selfdefense.activated`, `workspace.injection.detected`, `browser.data.prompt.injection.blocked`, `user.failedlogin` |
| Investigation | `ai.insight` |
| AI Edge | `ai.blocked`, `ai.redacted`, `ai.redirected`, `ai.detected` (a report-only match), `aidr.graph` ("Session snapshot"), `aidr.trajectory` ("Session trajectory available": one per new AI session, when its first recorded calls reach the server — seconds after the first call, not at the end; initiator = the user, none for a setup-key peer's session; target = the device or the account; meta `session_id`, `agent_name`, `peer`, `point`) |

Reading AI Edge rows. Every `ai.*` row has the same shape: "`<agent>` on `<peer>` for
`<user>`: prompt to `<model>` (`<provider>`) | response from … | tool call `<tool>` on
`<server>` | tool result … | request to `<host>` | connection to `<host>` | process
`<tool>` | periodic rule — blocked by rule `<rule>` by filter `<filter>` —
`<reason>` (matched: `<excerpt>`) | redacted | redirected to `<target>` | matched". The
raw JSON carries `surface` (`llm_request`, `llm_response`, `tool_call`, `tool_result`,
`prompt`, `sampling`, `http_request`, `connect`, `process_exec`, `periodic`), `engine`
(`rules`, `semantic`, `script`, `periodic`, `policy`, `limit`), `source` (`mitm`, `hook`,
`extension`, `gateway`, `probe`), the rule, filter, provider, model, server, tool, host,
session and actor fields, and `content` (at most 8 KB, after redaction, with
`content_truncated`). A limit refused at the AI Gateway is `ai.blocked` with engine
`limit`, source `gateway`, surface `llm_request`; a model or provider the user is not
granted is engine `policy`. Rows written by clients before this release with the retired
`tool.*` codes render as "UNKNOWN_ACTIVITY"; they are history, not a fault.

AI Edge events are verdicts only — blocked, redacted, redirected, detected — from every
source; a clean call is in its AI session (§1a), never an event. The server no longer
records `ai.allowed` or `semantic.event`, also when an older client, gateway or extension
still sends them; older rows stay until they age out. Rows saying "allowed" are history.

**Browser rows.** Events from the browser extension (`49-browser-extension-aidr.md`)
have `source` `extension`, the **site** as the agent (`chatgpt.com`, `claude.ai`,
`gemini.google.com`, …), `program` = the site's origin and `session_id` = the tab's
session; the row reads "`<site>` **in the browser** for `<user>`: …" where a device row
reads "`<agent>` on `<peer>` for `<user>`". A redacted conversation reload is an
`ai.redacted` row with the same tab session and program as the original answer. The
**Session snapshot** row (`aidr.graph`) exists for browsers too: "Session snapshot is
available for `<program>` in the browser" — one per tab session the first time it shows
behaviour, with the session id, program, device and source `extension` in the JSON;
"Session snapshot is available for peer `<peer>`" is the device form (no longer created;
a device's AI session is announced by `aidr.trajectory`).

API: `GET /api/events/paginated?limit=100&offset=0&date_from=<ISO>&date_to=<ISO>&user=<email>&code=<code>&code=<code>&q=<text>` →
`{events[], pagination{total,limit,offset,has_more,total_pages}}`. Omit `order` when
using `q` (relevance ranking).

---

## 1a. Activity → AI Sessions

`/ai-sessions`; navigation Activity → Events, **AI Sessions**, Reports; admins and owners
only (other users see the restricted-access page and read their own sessions through the
API). Title "AI Sessions (n)", "Here you can see all recorded AI sessions." A session is
one conversation of one user (or setup-key peer) with one agent, recorded on the device,
the AI Gateway or both (`point` `endpoint`, `gateway`, `endpoint,gateway`).

Tabs **LLM** (sessions with model calls) and **MCP** (sessions with MCP calls;
`?tab=mcp`); a session with both is on both. Each tab keeps its own search, filters, page
and sort.

| Control | Behaviour |
|---|---|
| Search box | Enter searches; Ctrl/⌘+K focuses it; "Ranked by relevance" while searching with no column sort |
| Date range | default last 14 days, remembered per tab in the browser; lists sessions active in the range (last activity on or after its start, started on or before its end) |
| User | All Users, or one user |
| Rows per page, refresh, **Reset filters** | Reset filters appears when something is filtered |

Columns are the Agentic Activity window's session lists (§3). Sortable on the server:
Started, Last activity, Turns / Calls, Usage, Violations (blocked + redacted + detected
of the whole session); the other columns are not. Default: Last activity, newest first.
Paged on the server; a page past the end moves to the last page. Usage of a session
recorded on a device shows cost $0.00: cost is not computed on devices. Clicking a row
opens the session in the Agentic Activity window (LLM tab → Trajectory, MCP tab → MCP
Calls); the kill-chain badge opens it on the graph.

**Search** matches the user (e-mail, name), agent, client app, MCP client, gateway, models,
MCP server names and tools. Text is split into words at anything that is not a letter or
digit (`alice@corp.example` → alice, corp, example; `search_docs` → search, docs; `gpt-4o`
→ gpt, 4o); every query word must match the **start** of one of the session's words, in
any order, case-insensitive. The middle of a word does not match (`orvex` does not find
`qorvex`); provider names are not searched; a query of punctuation alone finds nothing.

API: `GET /api/ai/sessions` with the same filters, sort and paging (`09-api-and-automation.md`
§2); a regular user gets only their own sessions.

---

## 2. Reports

**Create Report**: Report Type (**User Activity**, **Authentication Activity**, **AI
Agent Activity**, **AI Usage**), Date Range (default last 2 weeks), Groups (user groups;
empty = all) → Save. Generation runs server-side; the table lists Type, Report Date,
Range, Groups with View / Download (PDF) / Delete.

| Report | Contents |
|---|---|
| User Activity | Total/active users, average session time, total events; User Distribution pie; events radar (Access Control, Data Exfiltration, Policy Violation, Suspicious Activity, Administration); per user: session time, last seen, daily activity chart, Top Targets, Top Applications, Top Web Sites, Top Blocked Sites, per-category event tables |
| Authentication Activity | Total logins, success/failed trend per day, failed-login reasons pie; per user: login/failed counts, session time, event list (from `user.login`/`user.failedlogin`) |
| AI Agent Activity | Two tabs, **Users (n)** and **Agents (n)** — "Agents" are setup-key peers, which have no user. Calls come from the usage recorded in AI sessions: per user on **Users**, per setup-key peer (sessions the peer owns) on **Agents**. Stats Total Users / AI Agents / Servers / Total Tool Calls / Policy Violations; charts Agents, Models, Servers; per user or agent: Top Agents, Top Servers, Top Calls, Violations table (Date/Time, Category, Tool Call, Blocked By, Reason / Filter). **Blocked By** is **Guardrail** when a rule refused the call, **Limit** when a limit did (event engine `limit`), **Model or MCP grant** when the user's filters grant no such model or MCP server (engine `policy`); Reason / Filter names the guardrail and filter, or the refusal reason. Reports generated before this distinction show "—" in Blocked By for refusals that were not a rule — generate the report again. Violations are the `ai.blocked` events; detected, redacted and redirected calls count as calls, not violations |
| AI Usage | The usage recorded in AI sessions, by AI Gateways and by current Netzilo clients. **LLM Usage**: cards Requests, Tokens, Cost, Avg Latency, Users, Cache Hit; "Over time" chart switchable Requests \| Tokens \| Cost; Breakdown by Model / User / Provider / Gateway (for a device's records, the device's name); Top Models, Top Users. **MCP Usage**: Tool Calls, Servers, Avg Latency, Users; Breakdown by Server / Tool / User / Gateway; Top Servers, Top Tools. Breakdowns show at most 20 rows, Top lists at most 6 as shares; series are hourly up to 72 h, daily beyond. Empty: "No AI gateway usage in this period." The PDF is titled "NETZILO AI USAGE REPORT" |

AI Usage counts the usage recorded in AI sessions (`27-ai-gateway.md` §8): by AI
Gateways and by current Netzilo clients through TLS inspection (endpoint cost is 0). It
holds facts (user, model, tokens, cost, latency, status, MCP server and tool), never
text. Hook-only traffic, the browser extension and clients or servers older than session
recording are not in it; the empty text still reads "No AI gateway usage in this
period." AI Agent Activity counts violations from the `ai.blocked` events of every
source and calls from the usage records only.

Reports contain personal data; restrict who can open Activity (admins only by design).

API: `GET/POST /api/reports {report_type:"user_activity|authentication|ai_activity|ai_usage", from:"YYYY-MM-DD", to:"YYYY-MM-DD", groups:[…]}`, `GET/DELETE /api/reports/{id}`.
`to` is inclusive. `groups` is optional; for `ai_usage` it restricts the report to the
groups' members.

---

## 3. Dashboard home

Four tiles with a 7-day history: **Users**, **Devices**, **Agents** (distinct AI agents
active in the last 7 days) and **Tokens** (tokens recorded by gateways and devices per day). There
is no Security Score tile any more; the per-peer score is on each peer's page (the
Peers list no longer has the column; `24-peers-and-setup-keys.md` §2).

**Agentic Activity**: a period selector (**Last 24 Hours** | **Last 7 Days** | **Last 30
Days**), three tabs, and two buttons at the top right — **Refresh** (circular arrows) and
**View** (opens the Agentic Activity window, below):

| Tab | Cards | Chart | Top lists |
|---|---|---|---|
| Overview | Tokens, Cost, MCP Calls | Tokens over time | Top Teams, Top Guardrails |
| Agents | LLM Requests | LLM requests over time | Top Agents, Top Models |
| MCP | MCP Calls | MCP calls over time | Top Servers, Top Tools |

Top lists hold at most 6 rows as percentage shares. Top Teams is by tokens and names the
users' groups (never `All`). Top Agents and Top Guardrails count `ai.*` events from
every source; Top Models, Top Servers and Top Tools combine recorded usage with the
events from other sources; the cards and the time series are recorded usage (gateways
and devices). Before any recorded usage exists the section shows "Getting Started with AI
Edge" with the button **Get Started with AI Edge** (→ Edge → Providers).

Everything above is a **snapshot computed hourly** by the stat job, not a live query: a
request made a minute ago is not on the home page yet, while the AI Usage report (§2)
reads the live data. **Refresh** builds the snapshot and the window's views now: the
server builds an account once at a time and keeps a build younger than 30 seconds, so
admins refreshing together get one build. On a busy account it takes tens of seconds.

**The Agentic Activity window** (admins only; built from the AI sessions recorded on
devices and gateways, every 15 minutes or on **Refresh**) goes from the company down to
one agent session. The title names the level; the back arrow or **Escape** goes up one;
**Escape** on the first page closes it. Levels:

1. **First page** — the same tabs as the panel, then **Teams**: a tile per group whose
   members had recorded AI sessions in the period (**All** = everyone; a user in no
   group is under All only). A tile shows the name, active agents, people and service users, and token
   bars over the period; a left bar shades from gray to blue by the team's tokens against
   the busiest team (legend **Tokens Low → High**). Busiest first; **Search teams** filters
   by name; hovering shows sessions, tokens, cost and violations (blocked + redacted +
   detected). A group's membership is what the user had when each request was made.
2. **A team** — a traffic switch **LLM | MCP**. LLM: a flow **Users → Agents → Models ·
   by provider**, band width = tokens; **Users**, **Agents**, **Models** and the period
   narrow it. MCP: **Users → MCP Clients → MCP Servers → Tools**, band width = calls (no
   verdicts on the flow); menus Users, Clients, Servers, Tools (tools grouped by server).
3. **Sessions** — LLM list: Started, Agent / User, Models, Turns (model calls · tool
   calls), Usage (tokens and cost), Violations, kill-chain badge. MCP list: Started, Last
   activity, User · Agent, MCP servers (chips), Calls (n tools), Latency (average),
   Violations, and a **Trajectory** badge — **Model + MCP** when the session also made
   model calls, **MCP only** when it made none. Violations are blocked + redacted +
   detected of the whole session. Newest first; the kill-chain badge opens the session on
   its graph; **Search** by name, agent or model. Activity → AI Sessions (§1a) lists the
   same sessions with server-side search and sort.
4. **A session** — tabs **Trajectory**, **Behavior Graph** and, when the session has MCP
   calls, **MCP Calls**. **Trajectory**: a timeline (lanes Input, Model, Tools, Host, and
   Kill chain when there is one; scale Duration / Turns / Calls) and every message by
   turn — system prompt, prompts, context, thinking, answers, tool calls and results — with guardrail
   verdicts and kill-chain steps marked; long texts show a preview, the whole on click.
   A tool call refused before the agent got it has a row of its own (the tool, **Blocked**)
   whose **Verdict** names the rule and the reason it gave — for a judge rule, the judge's
   explanation.
   An MCP call the model asked for sits on the model's tool step; a direct call (no model
   loop) is a step of its own; a call from an MCP client with no model whose User-Agent
   names no known agent is shown under the client's name (**Unknown client** if it never
   named itself). A tool row's **Source** tab: Server, Tool, Ran by, MCP client, MCP
   session, **Seen at** (the host that recorded it). The Trajectory also shows the agent's
   **host activity** from the device — processes started, files read or written,
   connections — on the tool run that caused it, else as a step after the one it followed
   (**Host activity of the agent**); the summary counts distinct paths.
   **MCP Calls**: the trajectory limited to MCP tool rows — tool, arguments → result
   preview, chips **Redacted**, **Blocked**, **Execution** (a kill-chain stage), time.
   **Behavior Graph**: the user, agent, models, tools and device with the steps between
   them, file nodes folded per program; **Kill chains** marks a chain, **Filters** hides
   node and edge types.

The messages are the captured conversations of the device (Netzilo client) and the
gateway (`27-ai-gateway.md` §8.1), after the guardrails. A session seen at both is one
session (`point` `endpoint,gateway`); a call the device sent to the account's gateway is
recorded once, by the gateway. A session recorded on a device shows cost $0.00. A call
whose content did not reach the server shows **Content not captured for this call**.

Below it, the **Devices** panel: OS Distribution and the Security Score Distribution
radar.

API: `GET /api/stats` returns the saved snapshot — `null` before the job has run once —
with the fields `total_users`, `total_devices`, `total_agents`, `total_tokens`, `date`,
plus the 7 daily rows behind the tiles. The window reads `GET /api/ai/activity` and the
`/api/ai/sessions…` endpoints (`GET /api/ai/sessions` is also the AI Sessions list,
§1a), and **Refresh** is `POST /api/ai/activity/refresh` (`09-api-and-automation.md` §2).

---

## 4. Integrations

Cards toggle on/off; turning off asks "Disable this integration? … All settings of this
integration will be lost." Free-plan tenants see **Upgrade Plan**.

| Tab | Card | Purpose | Fields | Notes |
|---|---|---|---|---|
| Event Streaming | **Amazon S3** | stream every event as JSON objects; storage for workspace recordings | region, bucket, access key, secret key (IAM: `s3:PutObject`, `s3:PutObjectAcl` on the bucket) | one streaming target at a time |
| Event Streaming | **Min.io** | same, S3-compatible on-prem | endpoint URL, bucket, access key, secret key | |
| Networking | **Twilio** | managed TURN relays | Account SID, Auth Token (validated against Twilio before saving) | exclusive with Cloudflare / TURN-STUN |
| Networking | **Cloudflare** | managed TURN relays | Token ID, API Token | exclusive |
| Networking | **TURN/STUN Servers** | your own relays | STUN `host:port` UDP/TCP; TURN `host:port` UDP/TCP/DTLS/HTTPS + username/password; **Test Connection** runs a browser-side ICE test ("Connection test successful! Found: … candidates" / "TURN authentication failed - no relay candidates found…") | exclusive; overrides the built-in relay for all peers |

The **Artificial Intelligence** tab is not stored as an integration: it shows one card per
AI provider plus an **Add Provider** card, backed by its own resource — see §4a.

API: `GET/POST /api/integrations {platform:"twilio|cloudflare|static", config:{…}, enabled:true}`,
`PUT/DELETE /api/integrations/{id}`; `GET/POST /api/event-streaming {platform:"s3"|"min.io", config:{bucket,access_key,secret_key,region,endpoint?}, enabled:true}`,
`DELETE /api/event-streaming/{id}`. Posting an AI platform to `/api/integrations`
is refused; use `/api/ai/providers`. The listing masks stored credentials, so a
secret can never be read back out of it.

### 4a. Artificial Intelligence — providers, models and approvals

Any endpoint that speaks a supported protocol can be added; there is no fixed
list of vendors. **Integrations → Artificial Intelligence** shows one card per
provider (its protocol, the features it is used for, its verification status, an
on/off switch and **Configure**) and an **Add Provider** card.

A provider has a name, a **protocol** (`anthropic-messages`; `openai-completions`,
which covers Azure OpenAI, vLLM, Ollama, Groq, Together, OpenRouter, Mistral,
DeepSeek and any other OpenAI-compatible gateway; or `typesafe-systemone`, see
below), an optional **endpoint** (empty means the vendor's own API), optional
**Request headers** (every admin can read them; keep credentials in the API key), an
API key, a **Priority** (lower wins when several providers can serve the same
feature), and a list of **models**.

A **System One (TypeSafe)** provider (`typesafe-systemone`) answers typed questions
and never generates text. Only AIDR detection rules call it, through the `system_one()`
builtin (`32-detection-rule-authoring.md`); it is approved for no feature, so its models
step has nothing to tick and its card reads "Called by AIDR rules". A rule may name one
of its models (`model="jev-preview"`); otherwise the highest-priority System One
provider's first model answers. The key stays in management: hosts reach it through
management (`POST /api/ai/systemone`), and every call is a paid round trip.

**Approval is per feature.** There are three: **Assistant** (`assistant`) is
the admin assistant in the chat panel and the guardrail editor (the dialog's AI
panel, `28-edge-guardrails.md` §2.1); **Log Analysis** (`log-analysis`) covers AI
Smart Search and log analysis; **Threat Analysis** (`threat-analysis`) covers only
the AI judge of guardrail rules — `scan` rules with a `prompt`, the `llm_call()`
builtin and prompt scanning (`32-detection-rule-authoring.md`). The dashboard
describes them as "The admin assistant in the chat panel and the guardrail editor"
and "Judging content for guardrails — AI scans and judge rules". A rule's
`llm_call(..., model=...)` may name any model an enabled text provider lists, approved
for Threat Analysis or not; a model the account cannot use is an error, never a
fallback to another model. Each is approved at
provider level, and any model may override that for itself. In the dashboard
a fetched catalogue starts with **nothing approved** — the admin ticks models
in, singly or with the column checkbox — so "I added the provider but the
assistant says no model is approved" usually means no box was ticked yet.

**Editing keeps what you do not touch.** `PUT /api/ai/providers/{id}` treats an
omitted field as "keep the stored value" and a sent field — even empty — as a
replacement; an empty or omitted `api_key` always keeps the stored key. The
card's switch disables and re-enables; **Remove** in the settings dialog is
the only thing that deletes. A model with no override
inherits the provider; a model with an explicit empty list is approved for
nothing, which is how an expensive model is kept out of the assistant while
its siblings stay available. One model per feature per account can be starred
as the **default**.

A provider that lists **no** models serves the "automatic" model: whichever
model its endpoint currently reports as newest. That is what an account
upgraded from the old OpenAI/Anthropic integration rows gets, so nothing stops
working at upgrade.

**Verify** lists the endpoint's models and makes a one-token request to prove
the credential works. It stores nothing when run on a draft. A typed reason
comes back — `invalid-credential`, `unreachable`, `no-models`,
`model-refused`, `invalid-url`, `unsupported-protocol` — so the fix is
obvious. "Not verified" is not a failure: it means nobody has tested it yet.

A self-hosted endpoint must be reachable **from the management server**, not
from the admin's browser.

**These providers are management's own AI**, used by the server itself for the
assistant (also in the guardrail editor), smart search and the AI judge. They are not
the models employees reach through the AI Gateway: those are configured under
Edge → **Providers** (`45-ai-gateway-providers-and-limits.md` §1, API
`/api/edge/providers`) and the two lists are independent. Adding a vendor key
here grants nobody a model, and a gateway provider does not make the assistant
work.

| Call | Purpose |
|---|---|
| `GET /api/ai/protocols` | protocols, features and form prefills |
| `GET /api/ai/providers` | list; the API key is never returned, only `credential_set` |
| `POST /api/ai/providers` | add (owner only) |
| `PUT /api/ai/providers/{id}` | change (owner only); an empty `api_key` keeps the stored one |
| `DELETE /api/ai/providers/{id}` | remove (owner only) |
| `POST /api/ai/providers/verify` | test a draft; nothing is stored |
| `POST /api/ai/providers/{id}/verify` | test a stored provider and record the result |
| `GET /api/ai/models?use=assistant` | the models approved for a feature (`assistant`, `log-analysis`, `threat-analysis`) |
| `GET /api/ai/capabilities` | which features this account can serve |

Reads need admin; writes need owner. Adding, changing, removing and verifying
a provider are all audited (`ai.provider.create`, `.update`, `.delete`,
`.verify`).

**Choosing the model in the assistant.** The chat panel has a model picker
listing exactly the models approved for `assistant`, defaulting to the starred
one. The choice sticks to that chat and each answer records which model
produced it. The server re-checks the choice on every message: a model the
admin names on that message and that has lost its approval is refused with an
error naming it, not quietly swapped. A model the chat merely *remembers*
and that no longer exists (a provider that had no catalogue served "@auto",
then gained one) falls back to the default and the chat continues — so "the
picker shows Opus but I am refused for another model" should no longer occur;
if it does, the dashboard is out of date.

---

## 5. Procedures

- **SIEM feed**: Event Streaming → S3 (or Min.io) → point the SIEM at the bucket (objects
  named `ID_<id>_<Y>_<M>_<D>_<h>_<m>_<s>.json`). Also required before enabling
  workspace **Record Desktop Activity**.
- **Weekly access review**: Events → type `peer.access.blocked` + `user.failedlogin` +
  Policy Violation category, last 7 days, export CSV per page or pull
  `/api/events/paginated` with `limit=1000`.
- **Prove who reached what**: `peer.access.granted` (names the policy) and
  `peer.access.target` events per user.
- **Investigate an AI incident**: Events → category AI Edge → read the `ai.*` rows for
  the user or peer (the raw JSON names the surface, engine, source, rule and filter);
  find the session in Activity → AI Sessions (search the user, agent, tool or server;
  the MCP tab for tool calls) or from its **Session trajectory available** row → **View
  session**; read Trajectory, MCP Calls and a tool row's Source (Seen at); list the
  behaviour sessions with `GET /api/aidr/sessions?scope=source:<peer-id>` — for a browser, the source id of the
  user's browser from `GET /api/aidr/sources` (`kind: browser`), so
  `scope=source:<browser-source-id>`; a regular user sees only their own browser
  sessions there, an admin all (`49` §7); test candidate rules in report mode on
  the same device or user (`28-edge-guardrails.md` §4); view the kill
  chain on `ai.blocked` rows that have one; then generate an **AI Agent Activity** report
  for the period (device and gateway events) and an **AI Usage** report (the usage
  gateways and devices recorded; cost from the gateway).
- **Self-hosted relay independence**: Networking → TURN/STUN Servers to use your own
  coturn instead of the built-in one (test with **Test Connection** first).
- **Ask in plain language**: enable an AI provider, then use ✦ in the Events search;
  answers are saved as `ai.insight` events.

---

## 6. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| No events for a device | client not connected; nothing matched a policy/filter/profile; AI events are verdicts only, so clean AI traffic is in Activity → AI Sessions, not in events | `netzilo status`; check bindings; look in AI Sessions |
| `user.login` events missing (self-hosted) | login-event import from the identity provider requires the built-in provider and the service account roles created at install | verify identity provider health (`04` §9) |
| CSV export incomplete | only the current page is exported | raise rows per page or use the API |
| AI Smart Search greyed / AI Insights Disabled | no model approved for Log Analysis | Integrations → Artificial Intelligence → approve a model |
| Assistant button missing from the header | no model approved for `assistant` | Integrations → Artificial Intelligence → approve a model |
| "The model … cannot serve Assistant" | approval withdrawn while a chat was open | re-approve it, or pick another model in the chat's picker |
| No AI panel in the guardrail dialog (Edge → Guardrails) | no model approved for Assistant (the header's Assistant button is missing too), or the user is not an admin | Integrations → Artificial Intelligence → approve a model for Assistant (`28-edge-guardrails.md` §2.1) |
| Report empty | date range / groups; users not in the selected groups | widen |
| AI Agent Activity report lists peers under **Agents** | setup-key peers (no user) | expected; shown per peer |
| AI Agent Activity violation shows "—" under **Blocked By** | the report was generated before reports recorded what refused a call (limit or model/MCP grant), or the event came from a client or gateway that does not report its engine | generate the report again for the same period |
| AI Usage report empty although devices produce `ai.*` events | the device's client or the server predates session recording; the app is not intercepted (hooks only, the browser extension); or the traffic is Cursor, Gemini CLI or Connect-streaming (not recorded yet) | upgrade client and server; use the AI Agent Activity report for that traffic |
| AI Agent Activity report shows a setup-key peer's verdicts but none of its clean calls | the **Agents** tab counts events, and a current client sends no event for a clean call | read the peer's sessions in Activity → AI Sessions (user = the peer's name) |
| Agentic Activity on the home page empty although the gateway works | the snapshot is computed hourly; the AI Usage report reads live data | wait for the next run, or generate the report |
| Tokens tile zero | no recorded usage (gateway or device) that day | — |
| My device's sessions do not show up in AI Sessions | client or server older than session recording (the client records only once management announces it); the app is not intercepted (not in an endpoint filter's Agents; on Linux not pointed at the proxy); Cursor, Gemini CLI, Connect-streaming or stdio MCP (not recorded yet); the call went to the account's AI Gateway (recorded once, as point `gateway`) | upgrade both; fix Agents (`10-ai-security-aidr.md` §2); look for the gateway session |
| "No allowed events any more" | expected: AI events are verdicts only, and the server drops allowed events from older hosts | read the sessions in AI Sessions |
| Session usage shows tokens but cost $0.00 | recorded on a device: cost is not computed on devices | cost comes from the gateway only |
| A session's user is a peer name | a setup-key peer (no user) owns its sessions (`peer:<dns label>`); its groups are the peer's | expected |
| MCP sessions under "Unknown client" | an MCP client with no model that never sent its name (`clientInfo` in `initialize`) | expected |
| AI Sessions search finds nothing for part of a word | search matches word starts (`orvex` ≠ `qorvex`); provider names are not searched | search the word's start; filter by model or user instead |
| Event Streaming card shows Disabled after saving | credentials rejected or bucket policy | re-enter; check IAM `s3:PutObject`/`s3:PutObjectAcl` |
| Recording playback fails | S3 credentials changed or object expired | fix integration; recordings are read via signed URLs |
| TURN/STUN test fails | wrong `host:port`, credentials, firewall (3478/5349 + relay range) | fix and re-test before saving |
| "Where is the Security Score?" | the home page no longer has a score tile; the per-peer score remains, and the Devices panel shows its distribution | Peers → sort by Security Score; fix the red indicators or enforce with posture checks |

Events about this area: `integration.create/update/delete/disabled`, `report.*`, `ai.insight`.
