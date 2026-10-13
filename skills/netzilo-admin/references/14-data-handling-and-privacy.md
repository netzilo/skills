---
id: '14'
title: What Netzilo Collects — Data Handling, Privacy and Security Review
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 23268
sections:
- id: '1'
  title: The short answer
  chars: 1750
- id: '2'
  title: What every device reports to the management server
  chars: 1924
- id: '3'
  title: What the AI security layer collects
  chars: 3246
- id: '4'
  title: Session recordings and behaviour snapshots
  chars: 394
- id: '5'
  title: Server usage statistics
  chars: 858
- id: '6'
  title: Answers to the questions reviewers actually ask
  chars: 3617
- id: '7'
  title: Preparing for a security review
  chars: 1174
- id: '8'
  title: Data flows by feature
  chars: 9776
---
# What Netzilo Collects — Data Handling, Privacy and Security Review

**Use this when the customer asks what leaves their devices.** Security reviews, data
protection officers, works councils and procurement all ask this before a rollout, and a
vague answer stalls the deployment. Every field below is what the product actually sends,
stated plainly so you can hand the answer to a reviewer.

Answer only from this file. Do not reassure a customer that something is "not collected"
unless it appears here as not collected.

---

## 1. The short answer

| Question | Answer |
|---|---|
| Does Netzilo see the contents of my network traffic? | No. Traffic between devices is end-to-end encrypted WireGuard. The control plane distributes keys and policy; it does not hold the tunnel keys and cannot decrypt peer traffic. Relayed traffic passes through the relay still encrypted. |
| Does Netzilo see my AI prompts? | Prompt and response text leaves the device only when an AI-security rule matches; then the event includes the content that triggered it. Every AI call also produces an event with metadata and sizes, and MCP tool calls carry their arguments. See §3. Through the **AI Gateway**, prompts and answers traverse the customer's own gateway host on their way to the configured provider; management receives usage facts per request (who, which model, tokens, cost, latency, status), detections as events, and the **captured conversation** — the messages as the caller sent and received them after the guardrails — which administrators read in the session's trajectory (§3, §8). The dashboard's AI assistant is separate: what is typed into it goes to the configured AI provider (§8). |
| What does every device report about itself? | Hardware and OS identity, network addresses including MAC, and device posture. Full list in §2. |
| Where does it go? | To the management server. On self-hosted that is the customer's own server. On Cloud it is Netzilo. |
| Can any of it be turned off? | Server usage statistics can be disabled. Device metadata and the posture block cannot be disabled; the posture block is reported whether or not any posture check uses it. Only file checks (and Windows registry checks) are limited to what a posture check names. See §2.1 and §6. |

---

## 2. What every device reports to the management server

Sent when the client logs in and on each sync. This is the peer record an admin sees in
the dashboard.

**Identity and platform**

- Hostname
- Operating system, version, platform, kernel and kernel version
- Client version and desktop UI version
- System serial number, product name and manufacturer
- Cloud provider and platform, when the device runs in one

**Network**

- Every local network address, each with its **MAC address**
- Public IP address as seen by the server, and the region derived from it

**Device posture** (see §2.1 for when this is collected)

- Device identifier and Active Directory domain name
- Names of installed firewall products and antivirus products
- Whether the firewall is enabled, antivirus is active, antivirus is up to date
- Whether disk encryption is enabled, the screen is locked, the OS is up to date
- Whether the device is virtual, is running in a Netzilo container, is using Enterprise Browser
- Whether a debugger is attached to the client
- Process integrity level
- **Approximate geographic location as latitude and longitude**
- For file checks: the path checked, whether it exists, and whether it is running

Two of these routinely surprise reviewers, so raise them yourself rather than letting the
reviewer find them: MAC addresses of every local interface, and latitude and longitude.

### 2.1 What the posture checks in use change, and what they do not

The posture block above is reported on every login and sync, **whether or not the account
uses any posture check**; if it uses none, the block is still reported and nothing
consumes it. There is no per-field switch. What the checks do limit: file checks report
only the paths a posture check names, and on Windows registry checks report only the keys
a check names. Location is reported so that geolocation checks and the peer region
display can work.

---

## 3. What the AI security layer collects

This is the part that decides whether a deployment is approved, so be exact.

AI traffic is inspected in one of two places, and neither is the management server:

**On the device, not sent:** the TLS-inspecting proxy decrypts AI traffic locally, parses
it, and evaluates rules locally. Prompts and responses that match nothing are not
transmitted and are not stored.

**On the customer's AI Gateway:** where agents call models and MCP servers through the AI
Gateway (`27-ai-gateway.md`), the prompt, the answer, the tool call arguments and the tool
results traverse the gateway host — a host the customer runs — on their way to the provider
or the MCP server, and the guardrails run there. The gateway reports to management:
- **usage facts**, one record per model request (user, gateway, provider, model asked for
  and served, tokens by kind, cost, latency, status) and per MCP tool call (server, tool,
  status, latency, argument and result sizes), with no text;
- the **captured conversation** of each model call: system prompt, prompts, the agent's
  context, thinking, answers, tool calls and their results, **as the caller sent and
  received them after the guardrails** — what a guardrail redacted arrives redacted, a tool
  call the guardrails held back or refused is not sent, and a message is cut past 32 KB
  (`27` §8.1). Capture is always on for traffic through the gateway; administrators read it
  in the session's trajectory (`30` §3). Traffic that does not go through the gateway is
  not captured;
- a matching rule's event, as on a device, with the triggering content.

**Sent when something happens:**

| Event | What it carries |
|---|---|
| An AI request or response passes through | Operation, tool name, server name and URL, request, session and user identifiers, duration, **size in bytes** of input and output, status, the calling process identifier, and tool call arguments |
| A guardrail rule matches | Everything above, plus the action taken, the rule name, description and severity, the detection count, and a detection record |
| The detection record | The **content that triggered the match** — the prompt text for prompt rules, the URL for web-request rules — plus the rule pattern that matched, where in the request it matched, and the field path |

State this plainly to a reviewer: **when a rule fires, the text that caused it to fire
leaves the device** as part of the event. That is what makes the dashboard able to show
why something was blocked. For calls that match nothing, prompt and response text stays
on the device, but the event still carries the metadata and sizes in the table, and for
MCP tool calls the tool call arguments. Do not tell a reviewer that no content leaves on
an ordinary call.

Events are batched and pushed roughly every thirty seconds, which is why the dashboard
lags the device slightly.

**Reducing what is captured.** Narrow the rule so it matches less, or run the rule in
report mode rather than block mode, which still records the detection. There is no
setting that records a detection without its triggering content. If a customer cannot
accept that, the rule has to be removed from the filter that targets those devices.

---

## 4. Session recordings and behaviour snapshots

Where Enterprise Workspace or Enterprise Browser session recording is enabled, recordings
are produced and are viewable from Activity. AI behaviour snapshots capture the sequence
of actions an agent took on a device and are viewable per peer. Both are visible to
admins. Treat both as containing user content, and say so during a review.

---

## 5. Server usage statistics

A self-hosted management server periodically sends anonymous usage counts to Netzilo.

**What is sent:** counts only. Server uptime and version, number of accounts, users,
service users and tokens, number of peers and how many were active in the last day, how
many have SSH or login expiration enabled, counts of groups, policies, routes,
nameservers, posture checks and setup keys, the lowest and highest client versions in
use, which identity provider and which database engine are configured.

**What is not sent:** no names, no e-mail addresses, no IP addresses, no keys, no policy
contents, no device metadata, no AI events.

**Disabling it:** start the management service with the flag that disables anonymous
metrics. The server logs when it sends and when the next send is due, so you can confirm
it has stopped.

---

## 6. Answers to the questions reviewers actually ask

| Question | Answer |
|---|---|
| Can Netzilo staff read our traffic? | Not peer network traffic: it is end-to-end encrypted and the control plane holds no tunnel keys. On Cloud, Netzilo hosts the account's data — device metadata, activity and AI events including triggering content, assistant sessions (§8). |
| Can our own admins read employee traffic? | Not network traffic. Admins can see AI security events including triggering content, the conversations of AI agents that went through the AI Gateway (after the guardrails), session recordings where enabled, all activity events, and every AI assistant session in the account as a read-only audit log (§8). |
| Is anything sent to a third party? | Self-hosted sends Netzilo the usage counts in §5 (nothing if disabled), and an escalation only when an admin approves it (§8). Every AI feature of management itself — the assistant, smart search, guardrail generation, the AI judge inside a scanning rule — calls the AI provider the account configured under Integrations → Artificial Intelligence, with the account's own credentials; what it sends that provider is described in §8. The **AI Gateway** is the other third-party path: users' prompts and MCP tool calls go from the customer's gateway host to the upstream providers and MCP servers the admin configured under Edge → Providers and Edge → MCP, with the keys and sign-ins stored for them; management receives usage facts and the captured conversations (§3, §8). |
| Where is data stored? | Self-hosted: on the customer's server, in their database and volumes. Cloud: in Netzilo's hosted environment. |
| How long is it kept? | Activity events are retained until deleted; there is no automatic retention limit and no configurable retention period. Account statistics are pruned after ninety days. AI data (AI Gateway usage, sessions and captured conversations, behaviour observations) is deleted by the AI data retention job: 90 days for records and conversations, 400 days for hourly totals, 7 days for device and browser observations by default (`02-server-operations.md` §20). Plan database growth accordingly. Per-feature retention is in §8. |
| Can we export or delete a person's data? | Deleting a user removes the user, their devices (peers) and their access tokens, and records a deletion event. It does **not** delete their activity history: events they initiated or that name them stay in the audit trail. Do not promise otherwise. Activity can be exported from the dashboard a page at a time or through the API. |
| Are stored credentials encrypted? | Not at the field level. AI Gateway provider keys, the shared header values and sign-in of an MCP server, and users' own MCP sign-ins and header values are kept as plain JSON in the management database, masked in the API and dashboard, and delivered in clear to the account's gateways (§8). The AI provider keys under Integrations, integration secrets and setup keys are stored in plain form too, as are activity events; personal access tokens are stored only as hashes. The `DataStoreEncryptionKey` a self-hosted installer writes is not used to encrypt any of this. Protect database access, backups and the gateways' service tokens accordingly; on a self-hosted server, encrypt the database volume and backups. |
| Is there an audit trail of admin actions? | Yes. Administrative changes are recorded as activity events attributed to the user or service account that made them. |
| What if a device is offline? | Nothing is reported until it reconnects. Events queue on the device. |

---

## 7. Preparing for a security review

Do this before the customer's reviewer asks, not after.

1. Confirm the deployment model, because the answer to "where does data go" differs
   entirely between self-hosted and Cloud.
2. List which posture checks are enabled, since that determines which device attributes
   are actually used.
3. List which guardrails are bound to which groups through filters — endpoint filters
   for devices, gateway filters for users of the AI Gateway — since that determines
   whose content can appear in an event; and, where a gateway is in use, which
   providers and MCP servers it forwards to.
4. State the two surprising fields up front, MAC addresses and location.
5. Confirm whether session recording is enabled anywhere.
6. Decide whether server usage statistics stay on, and say so.
7. Confirm which AI provider is configured and whether the AI assistant is enabled, and
   for whom; §8 says what it receives.
8. Give the reviewer §1, §3 and §8 verbatim. They are the sections that decide approval.

If the reviewer asks something not answered here, do not infer. Say it needs
confirmation, and follow `12-escalation-package.md`.

---

## 8. Data flows by feature

One row per feature, so a reviewer can follow each kind of data from where it is
collected to where it is deleted. "Not stated" means this file does not document it:
say it needs confirmation rather than filling the gap.

**Networking — device metadata and posture (§2)**

| | |
|---|---|
| Collected | on the device, at login and on every sync |
| Stored | the peer record on the management server (the customer's server when self-hosted; Netzilo's on Cloud) |
| Sent to | the management server only |
| Retained | while the peer exists; the latest values overwrite the earlier ones |
| Deleted | by deleting the peer, or the user who owns it; events that mention the peer remain |

**AI inspection — AI events and detections (§3)**

| | |
|---|---|
| Collected | on the device by the AI security layer; prompt and response text only when a rule fires |
| Stored | as activity events on the management server |
| Sent to | the management server, batched about every thirty seconds; event streaming (Integrations → Event Streaming), when configured, copies events to the customer's S3 or MinIO bucket |
| Retained | like all activity events: until deleted, no automatic limit |
| Deleted | not per user (see §6); narrowing or removing the rule stops new capture |

**AI behaviour snapshots**

| | |
|---|---|
| Collected | on the device, at the gateway or in the browser: the sequence of actions an AI agent took (observations: what was called, not the text, unless a guardrail matched) |
| Stored | on the management server, viewable per peer, per gateway and per browser source by admins; a regular user sees their own sessions only |
| Sent to | the management server |
| Retained | 7 days (observations); an AI Gateway session's observations as long as its usage records (90 days by default); the session views are rebuilt from them |
| Deleted | by the AI data retention job, every six hours (`02-server-operations.md` §20); no per-user deletion |

**Browser extension — AI events, network log and browser sessions (`49-browser-extension-aidr.md`)**

| | |
|---|---|
| Collected | in the browser, by the same engine as on a device, for the signed-in user: (1) AI events for prompts, answers and tool calls on the web AI apps and the LLM APIs a page calls — the triggering content only when a guardrail matches, as in §3; (2) a **network log** of the tab's requests: host, path, method and content type, **never request or response bodies** (none in Safari, which gives the extension no network log); (3) behaviour observations per browser tab and site — what happened (a prompt, an answer, a request, a tool call) with content **references** (sizes, hashes, hosts), not the prompt text, unless a guardrail matched |
| Stored | events as activity events on the management server; observations in the management server's behaviour store, as one browser source per user and browser (`kind: browser`), visible to that user and to admins |
| Sent to | the management server only, as the signed-in user: events in batches, observations in paced batches (per-user limits, `49` §7); nothing goes to the AI site that the page did not send itself, except a redacted prompt in place of the original |
| Retained | events: like all activity events; observations: **7 days** |
| Deleted | observations by the AI data retention job, every six hours (`02` §20); events as in §6 |

Say to a reviewer: the extension reads what the page sends to and receives from the AI
sites in order to judge it; what leaves the browser for management is the event metadata
of §3, the triggering content when a rule fires, the hosts and paths the tab requested,
and the behaviour observations without prompt text. When the desktop client governs the
browser, the extension stands down and reports nothing (`49` §3).

**AI Gateway — LLM and MCP traffic (`27-ai-gateway.md`)**

| | |
|---|---|
| Collected | on the customer's gateway host: the prompt, the answer, MCP tool calls and results pass through it and are evaluated by the guardrails there |
| Stored | not on the gateway's disk. On the management server: the **captured conversation** of each model call (after the guardrails, §3), each text once, with the session it belongs to; and a matching rule's activity event with the triggering content, as on a device |
| Sent to | the upstream provider (OpenAI, Anthropic, Azure, …) or MCP server the admin configured under Edge → Providers / Edge → MCP, with the credentials stored for it; the captured conversation and detections to the management server. Administrators read every session's conversation in the Agentic Activity window; through the API a user can read only their own sessions (`09` §2) |
| Retained | captured conversations: as long as the usage records (90 days by default; a message's text one day longer); detection events: like all activity events |
| Deleted | conversations and sessions by the AI data retention job (`02` §20) and with the account; events as in §6 |

**AI Gateway — usage telemetry**

| | |
|---|---|
| Collected | on the gateway, one record per model request (user, the user's groups at that moment, gateway name, agent, provider, model asked for and served, streamed or not, status, tokens by kind, cost, latency, the tool calls the answer asked for) and per MCP tool call (server, tool, status, latency, argument and result sizes). No prompt, answer, argument or result text |
| Stored | on the management server: raw records, the sessions built from them, hourly totals |
| Sent to | the management server in batches every 15 seconds; shown on the dashboard home (Agentic Activity panel and window, Tokens tile) and in the **AI Usage** report |
| Retained | raw records and sessions 90 days, hourly totals 400 days (defaults; self-hosted servers set them, `02` §20) |
| Deleted | by the AI data retention job every six hours, and with the account |

**AI Gateway — users' MCP sign-ins, header values, the admin's shared sign-in and provider keys**

| | |
|---|---|
| Collected | what a user enters in the Workplace to connect an MCP server (an OAuth sign-in, or header values such as an API key), per user and per server; the admin's shared OAuth sign-in for a server; the provider API keys the admin enters under Edge → Providers |
| Stored | in the management database as plain JSON, **without field-level encryption** (the server applies no encryption key to them); masked in the API's answers and never shown again in the dashboard |
| Sent to | every gateway of the account pulls them **in clear** with its service token, to present them to the MCP server or provider on the user's behalf |
| Retained | while the connection, server or provider exists |
| Deleted | the user disconnects the server (their own sign-in); the admin deletes the server or provider |

Say this to a reviewer as it is: a user's MCP credential and the account's provider keys
are readable by anyone who can read management's database or hold a gateway's service
token. The controls are database access, the service token's custody and the gateway
host's.

**AI Gateway — the Workplace "AI Gateway" token**

| | |
|---|---|
| Collected | a personal access token the user creates in the Workplace's Agentic Access section for their agents (90 days, scope `mcp`) |
| Stored | the token itself in the user's **browser localStorage** on the Workplace's origin; its record (name, expiry, scope) on the management server like any access token |
| Sent to | the AI Gateway as `Authorization: Bearer` by the user's agents, and from the Workplace to probe the gateway cards |
| Retained | in the browser until the site data is cleared or it expires; the record until deleted |
| Deleted | the user deletes it under Access Tokens (the browser copy then stops working); clearing the browser's site data removes the copy only |

**AI assistant conversations**

| | |
|---|---|
| Collected | what the person types, and everything the assistant does to answer: its API calls, device tool calls and the results that come back (configuration, device diagnostics, log excerpts, command output) |
| Stored | as the session's history on the management server; the person sees their own sessions, and the account's admins can open any session in the account as a read-only audit log |
| Sent to | the AI support worker (on self-hosted, a container on the customer's own server; on Cloud, Netzilo's), and the AI provider the account configured, with the account's own credentials. Tool results are part of what the provider receives |
| Retained | not stated; plan as for activity events |
| Deleted | a person deleting a chat removes it from their own list; it stays in the admins' audit log, marked deleted |

Tell a reviewer plainly: whatever the assistant reads to answer a question — including a
device's logs — reaches the configured AI provider. Choosing that provider, and who may
use the assistant (Settings → Permissions), is how the customer controls it.

**Session recordings (Enterprise Workspace, Enterprise Browser)**

| | |
|---|---|
| Collected | on the device, only where recording is enabled in the profile |
| Stored | in the customer's S3 or MinIO bucket configured under Integrations → Event Streaming |
| Sent to | that bucket; admins view recordings from Activity |
| Retained | as the bucket's own lifecycle rules decide |
| Deleted | in the bucket |

**Escalation to Netzilo Level 3**

| | |
|---|---|
| Collected | a written case summary; from a harness, optionally a redacted diagnostic package (`12-escalation-package.md`) |
| Stored | with Netzilo, for the case |
| Sent to | Netzilo's Level 3 service, only after an admin approves it; bundles are always redacted first |
| Retained | not stated |
| Deleted | not stated; ask Netzilo |

