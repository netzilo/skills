---
id: '30'
title: Admin Skill — Activity Events, Reports, Dashboard Home and Integrations
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 15855
sections:
- id: '1'
  title: Activity → Events
  chars: 3828
- id: '2'
  title: Reports
  chars: 1550
- id: '3'
  title: Dashboard home
  chars: 498
- id: '4'
  title: Integrations
  chars: 6059
- id: '5'
  title: Procedures
  chars: 1105
- id: '6'
  title: Diagnosis
  chars: 1894
---
# Admin Skill — Activity Events, Reports, Dashboard Home and Integrations

**Dashboard:** Activity → **Events** (`/activity`), Activity → **Reports** (`/reports`),
**Dashboard** (`/dashboard`), **Integrations** (`/integrations`). **API:**
`/api/events/paginated`, `/api/reports`, `/api/stats`, `/api/integrations`,
`/api/event-streaming`, `/api/smartsearch`.

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
| Event types | multi-select grouped by category: Administration, Access Control, Data Exfiltration, Policy Violation, Suspicious, Investigation, AI Edge |
| User | single user (or "Netzilo System") |
| Rows per page | 10 / 25 / 50 / 100 (server-side pagination) |
| Download CSV | exports the **current page** only: Timestamp, User, Email, Event (code), Source, Target, More Information |
| Reset filters | clears everything |

Row anatomy: category icon with +/×/change badge, initiator (name, e-mail; "System" for
automatic actions; hover for location when known), timestamp, description, copy raw JSON
(hover). Special rows: `session.recorded` → play the recording; `aidr.graph` → **View
session snapshot**; events with a kill chain → **View kill chain**; `ai.insight` → AI
answer with citation cards.

Event categories and the most useful codes:

| Category | Codes |
|---|---|
| Administration | `user.peer.add`, `setupkey.peer.add`, `user.peer.delete`, `peer.rename`, `peer.group.add/delete`, `peer.ssh.enable/disable`, `peer.login.expiration.enable/disable`, `peer.login.expire`, `peer.approve`, `policy.add/update/delete`, `group.add/update/delete`, `route.add/update/delete`, `nameserver.group.*`, `dns.setting.*`, `setupkey.add/update/revoke/overuse/deleted`, `user.invite/join/block/unblock/delete`, `user.role.update`, `user.group.add/delete`, `service.user.create/delete`, `personal.access.token.create/delete`, `account.setting.*`, `transferred.owner.role`, `posture.check.created/updated/deleted`, `profile.created/updated/removed`, `tool.*`, `scanner.*`, `filter.*`, `integration.*`, `subscription.updated`, `tenant.updated`, `report.*`, `dashboard.login` |
| Access Control | `peer.access.granted`, `peer.access.blocked`, `peer.access.target`, `peer.access.target.blocked`, `browser.url.access`, `user.login`, `user.logout`, `workspace.app.started`, `session.recorded` |
| Data Exfiltration | `browser.data.redacted`, `browser.data.print.blocked`, `browser.data.clipboard.blocked`, `browser.download.content`, `browser.data.classified`, `browser.data.code.upload.blocked`, `browser.data.screenshot.blocked`, `workspace.print.blocked` |
| Policy Violation | `browser.download.file`, `browser.upload.file`, `browser.url.blocked`, `browser.isolation.*.required`, `browser.posture.check`, `workspace.posture.check`, `browser.data.code.redacted`, `browser.exception.request` |
| Suspicious | `workspace.selfdefense.activated`, `workspace.injection.detected`, `browser.data.prompt.injection.blocked`, `user.failedlogin` |
| Investigation | `ai.insight` |
| AI Edge | `tool.allowed`, `tool.blocked`, `tool.detected`, `semantic.event`, `aidr.graph` |

Reading AI Edge rows: "`<agent>` on `<peer>` prompted with model `<model>` on `<server>` —
blocked/detected" (LLM traffic), "`<agent>` tool call `<tool>` on `<server>` is blocked
because scanner detected `<rule>` … by filter `<filter>`", "… blocked because posture
check failed with reason …", "acquired skill …" (semantic).

API: `GET /api/events/paginated?limit=100&offset=0&date_from=<ISO>&date_to=<ISO>&user=<email>&code=<code>&code=<code>&q=<text>` →
`{events[], pagination{total,limit,offset,has_more,total_pages}}`. Omit `order` when
using `q` (relevance ranking).

---

## 2. Reports

**Create Report**: Report Type (**User Activity**, **Authentication Activity**, **AI
Agent Activity**), Date Range (default last 2 weeks), Groups (user groups; empty = all)
→ Save. Generation runs server-side; the table lists Type, Report Date, Range, Groups
with View / Download (PDF) / Delete.

| Report | Contents |
|---|---|
| User Activity | Total/active users, average session time, total events; User Distribution pie; events radar (Access Control, Data Exfiltration, Policy Violation, Suspicious Activity, Administration); per user: session time, last seen, daily activity chart, Top Targets, Top Applications, Top Web Sites, Top Blocked Sites, per-category event tables |
| Authentication Activity | Total logins, success/failed trend per day, failed-login reasons pie; per user: login/failed counts, session time, event list (from `user.login`/`user.failedlogin`) |
| AI Agent Activity | Users / AI Agents / Servers / Total Tool Calls / Policy Violations; top Agents, Models, Servers; per user (and per **Setup Key Peer** under "Serverless"): flow graph user → agent → server/LLM, Top Agents, Top Servers, Top Calls, Violations table (Date/Time, Category Security/Privacy/Compliance/Prompt Injection, Tool Call, Blocked By Scanner/Posture Check, Reason/Filter) |

Reports contain personal data; restrict who can open Activity (admins only by design).

API: `GET/POST /api/reports {report_type:"user_activity|authentication|ai_activity", from:"YYYY-MM-DD", to:"YYYY-MM-DD", groups:[…]}`, `GET/DELETE /api/reports/{id}`.

---

## 3. Dashboard home

Four 7-day tiles: **Security Score** (letter grade from device posture: A ≥ 80, B ≥ 60,
C ≥ 40, D ≥ 20, F), **Users**, **Agents** (distinct AI agent applications seen), **Devices**.
**AI Activity**: top Agents / Models by call share, **Policy Violations** donut
(Security, Privacy, Compliance, Prompt Injection). **Devices**: OS distribution and
Security Score distribution radar. Empty states offer **Add Peer** and **Get Started with
AI Edge**. API: `GET /api/stats`.

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

**Artificial Intelligence is not a card and not an integration.** It is its own
resource — see §4a.

API: `GET/POST /api/integrations {platform:"twilio|cloudflare|static", config:{…}, enabled:true}`,
`PUT/DELETE /api/integrations/{id}`; `GET/POST /api/event-streaming {platform:"s3"|"min.io", config:{bucket,access_key,secret_key,region,endpoint?}, enabled:true}`,
`DELETE /api/event-streaming/{id}`. Posting an AI platform to `/api/integrations`
is refused; use `/api/ai/providers`. The listing masks stored credentials, so a
secret can never be read back out of it.

### 4a. Artificial Intelligence — providers, models and approvals

Any endpoint that speaks a supported protocol can be added; there is no fixed
list of vendors. **Integrations → Artificial Intelligence** shows a table of
providers, not cards, with **Add provider**.

A provider has a name, a **protocol** (`anthropic-messages` or
`openai-completions` — the latter covers Azure OpenAI, vLLM, Ollama, Groq,
Together, OpenRouter, Mistral, DeepSeek and any other OpenAI-compatible
gateway), an optional **endpoint** (empty means the vendor's own API), an API
key, and a list of **models**.

**Approval is per feature.** There are three: **Assistant** (`assistant`) is
the admin chat panel; **Log Analysis** (`log-analysis`) covers risk analysis of
discovered tools and smart search; **Threat Analysis** (`threat-analysis`)
covers scanner rule generation and prompt scanning. Each is approved at
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

Cloud-only integrations (identity-provider sync, EDR) are documented in the public docs
and are not present on self-hosted servers.

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
- **Investigate an AI incident**: Events → AI Edge → open the `aidr.graph` snapshot for
  the peer; use **Run Scanners** to test candidate rules against it; view the kill chain
  on `tool.blocked` rows that have one; generate an AI Activity report for the period.
- **Self-hosted relay independence**: Networking → TURN/STUN Servers to use your own
  coturn instead of the built-in one (test with **Test Connection** first).
- **Ask in plain language**: enable an AI provider, then use ✦ in the Events search;
  answers are saved as `ai.insight` events.

---

## 6. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| No events for a device | client not connected; nothing matched a policy/filter/profile | `netzilo status`; check bindings |
| `user.login` events missing (self-hosted) | login-event import from the identity provider requires the built-in provider and the service account roles created at install | verify identity provider health (`04` §9) |
| CSV export incomplete | only the current page is exported | raise rows per page or use the API |
| AI Smart Search greyed / AI Insights Disabled | no model approved for Log Analysis | Integrations → Artificial Intelligence → approve a model |
| Assistant button missing from the header | no model approved for `assistant` | Integrations → Artificial Intelligence → approve a model |
| "The model … cannot serve Assistant" | approval withdrawn while a chat was open | re-approve it, or pick another model in the chat's picker |
| AI rule generation unavailable | no model approved for Threat Analysis | Integrations → Artificial Intelligence → approve a model |
| Report empty | date range / groups; users not in the selected groups | widen |
| AI Activity report shows "Serverless" users | peers enrolled with setup keys (no user) | expected; shown per peer |
| Event Streaming card shows Disabled after saving | credentials rejected or bucket policy | re-enter; check IAM `s3:PutObject`/`s3:PutObjectAcl` |
| Recording playback fails | S3 credentials changed or object expired | fix integration; recordings are read via signed URLs |
| TURN/STUN test fails | wrong `host:port`, credentials, firewall (3478/5349 + relay range) | fix and re-test before saving |
| Dashboard Security Score F | many devices with red posture indicators | Peers → sort by score; fix or enforce with posture checks |

Events about this area: `integration.create/update/delete/disabled`, `report.*`, `ai.insight`.
