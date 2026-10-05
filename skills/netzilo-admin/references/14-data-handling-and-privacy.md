---
id: '14'
title: What Netzilo Collects — Data Handling, Privacy and Security Review
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 13616
sections:
- id: '1'
  title: The short answer
  chars: 1330
- id: '2'
  title: What every device reports to the management server
  chars: 1924
- id: '3'
  title: What the AI security layer collects
  chars: 1938
- id: '4'
  title: Session recordings and behaviour snapshots
  chars: 394
- id: '5'
  title: Server usage statistics
  chars: 858
- id: '6'
  title: Answers to the questions reviewers actually ask
  chars: 2153
- id: '7'
  title: Preparing for a security review
  chars: 996
- id: '8'
  title: Data flows by feature
  chars: 3494
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
| Does Netzilo see my AI prompts? | Prompt and response text leaves the device only when an AI-security rule matches; then the event includes the content that triggered it. Every AI call also produces an event with metadata and sizes, and MCP tool calls carry their arguments. See §3. The dashboard's AI assistant is separate: what is typed into it goes to the configured AI provider (§8). |
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

**On the device, not sent:** the TLS-inspecting proxy decrypts AI traffic locally, parses
it, and evaluates rules locally. Prompts and responses that match nothing are not
transmitted and are not stored.

**Sent when something happens:**

| Event | What it carries |
|---|---|
| An AI request or response passes through | Operation, tool name, server name and URL, request, session and user identifiers, duration, **size in bytes** of input and output, status, the calling process identifier, and tool call arguments |
| A scanner rule matches | Everything above, plus the action taken, the rule name, description and severity, the detection count, and a detection record |
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
| Can our own admins read employee traffic? | Not network traffic. Admins can see AI security events including triggering content, session recordings where enabled, all activity events, and every AI assistant session in the account as a read-only audit log (§8). |
| Is anything sent to a third party? | Self-hosted sends Netzilo the usage counts in §5 (nothing if disabled), and an escalation only when an admin approves it (§8). Every AI feature — the assistant, risk analysis of discovered tools, smart search, scanner rule generation, prompt scanning — calls the AI provider the account configured under Integrations → Artificial Intelligence, with the account's own credentials; what it sends that provider is described in §8. |
| Where is data stored? | Self-hosted: on the customer's server, in their database and volumes. Cloud: in Netzilo's hosted environment. |
| How long is it kept? | Activity events are retained until deleted; there is no automatic retention limit and no configurable retention period. Account statistics are pruned after ninety days. Plan database growth accordingly. Per-feature retention is in §8. |
| Can we export or delete a person's data? | Deleting a user removes the user, their devices (peers) and their access tokens, and records a deletion event. It does **not** delete their activity history: events they initiated or that name them stay in the audit trail. Do not promise otherwise. Activity can be exported from the dashboard a page at a time or through the API. |
| Is there an audit trail of admin actions? | Yes. Administrative changes are recorded as activity events attributed to the user or service account that made them. |
| What if a device is offline? | Nothing is reported until it reconnects. Events queue on the device. |

---

## 7. Preparing for a security review

Do this before the customer's reviewer asks, not after.

1. Confirm the deployment model, because the answer to "where does data go" differs
   entirely between self-hosted and Cloud.
2. List which posture checks are enabled, since that determines which device attributes
   are actually used.
3. List which AI scanners are bound to which groups, since that determines whose content
   can appear in an event.
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
| Collected | on the device: the sequence of actions an AI agent took |
| Stored | on the management server, viewable per peer by admins |
| Sent to | the management server |
| Retained | not stated |
| Deleted | not stated |

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

