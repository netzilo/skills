---
id: '14'
title: What Netzilo Collects — Data Handling, Privacy and Security Review
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 8629
sections:
- id: '1'
  title: The short answer
  chars: 1052
- id: '2'
  title: What every device reports to the management server
  chars: 1751
- id: '3'
  title: What the AI security layer collects
  chars: 1735
- id: '4'
  title: Session recordings and behaviour snapshots
  chars: 394
- id: '5'
  title: Server usage statistics
  chars: 858
- id: '6'
  title: Answers to the questions reviewers actually ask
  chars: 1447
- id: '7'
  title: Preparing for a security review
  chars: 863
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
| Does Netzilo see my AI prompts? | Only when an AI-security rule matches. Normal prompts are inspected on the device and discarded. When a rule fires, the event that is sent includes the content that triggered it. See §3. |
| What does every device report about itself? | Hardware and OS identity, network addresses including MAC, and device posture. Full list in §2. |
| Where does it go? | To the management server. On self-hosted that is the customer's own server. On Cloud it is Netzilo. |
| Can any of it be turned off? | Posture data is only collected for checks in use. Server usage statistics can be disabled. Device metadata cannot be disabled; it is how peers are identified. See §6. |

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

### 2.1 Posture data is collected for the checks in use

File checks report only the paths named in a posture check. Location is reported so that
geolocation checks and the peer region display can work. If the customer uses no posture
checks, the posture block is still reported by the client but nothing consumes it. There
is no per-field switch.

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
why something was blocked. Sizes are recorded for every call, contents are not.

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
| Can Netzilo staff read our traffic? | No. Peer traffic is end-to-end encrypted and the control plane holds no tunnel keys. |
| Can our own admins read employee traffic? | Not network traffic. Admins can see AI security events including triggering content, session recordings where enabled, and all activity events. |
| Is anything sent to a third party? | Self-hosted sends only the usage counts in §5, and nothing if disabled. AI risk analysis of discovered tools calls the AI provider the customer configured, using the customer's own credentials. |
| Where is data stored? | Self-hosted: on the customer's server, in their database and volumes. Cloud: in Netzilo's hosted environment. |
| How long is it kept? | Activity events are retained until deleted; there is no automatic retention limit and no configurable retention period. Account statistics are pruned after ninety days. Plan database growth accordingly. |
| Can we export or delete a person's data? | Users, their devices and their events are removed when the user is deleted. Activity can be exported from the dashboard a page at a time or through the API. |
| Is there an audit trail of admin actions? | Yes. Every administrative change is an activity event attributed to a user. |
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
7. Give the reviewer §1 and §3 verbatim. They are the two sections that decide approval.

If the reviewer asks something not answered here, do not infer. Say it needs
confirmation, and follow `12-escalation-package.md`.
