---
id: '49'
title: Admin Skill — The browser extension as an AI enforcement point
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 19649
sections:
- id: '1'
  title: Model
  chars: 2355
- id: '2'
  title: How policy reaches it
  chars: 1529
- id: '3'
  title: Sign-in and the stand-down rule
  chars: 1788
- id: '4'
  title: '`fail_mode` (managed policy)'
  chars: 714
- id: '5'
  title: What users see
  chars: 1459
- id: '6'
  title: Browsers and distribution
  chars: 1234
- id: '7'
  title: The behaviour graph side
  chars: 2654
- id: '8'
  title: Events
  chars: 1070
- id: '9'
  title: API
  chars: 1146
- id: '10'
  title: Diagnosis
  chars: 3493
- id: '11'
  title: Limits to state before a customer discovers them
  chars: 1359
---
# Admin Skill — The browser extension as an AI enforcement point

**Audience:** admins who want AI use in the browser governed without a desktop client
on every device, and the support agent helping an end user whose browser extension
"is not doing anything" or "changed what the AI answered". Read with
`10-ai-security-aidr.md` (the device engine, hooks, SDK), `29-edge-filters.md`
(how policy is bound) and `28-edge-guardrails.md` (the rules themselves).

**Dashboard:** Edge → **Filters** (an endpoint filter whose Operating Systems include
**Browser**), Activity → **Events** (category AI Edge, source `extension`). **API:**
`/api/edge/filters?os=browser`, `/api/aidr/sources`, `/api/aidr/sessions`,
`/api/aidr/observations`. **Who:** admins bind policy; every signed-in user's browser
reads its own filters and uploads its own sessions.

---

## 1. Model

The Netzilo browser extension (Chrome, Edge, Firefox, Safari, the Enterprise Browser)
runs **the same governance engine as the Netzilo client and the AI Gateway**, built for
the browser. One engine, one rule language, one behaviour graph: a guardrail written for
a device applies in the browser unchanged, and what the browser records lands in the same
sessions and `ai.*` events as everything else. Rules are cloud data; the extension does
not need a release for a new guardrail.

It is a full AIDR source: guardrails (allow, detect, redact, block), the behaviour graph
(tab sessions and observations uploaded to management), and AI events.

**What it governs in the page** (requests the page makes: fetch, XHR, WebSocket,
EventSource):

| Traffic | Examples | Governed as |
|---|---|---|
| The web AI apps | ChatGPT (signed-in **and logged-out**), claude.ai, Gemini, Perplexity | prompts (`llm_request`) and answers (`llm_response`), including streamed answers |
| Direct API calls from a page | a web app or an in-page script calling the OpenAI, Anthropic or Google AI APIs, and the other LLM hosts the engine knows (Perplexity, Cohere, NVIDIA, Bedrock runtime, Cursor, a local Ollama on `localhost:11434`) | the same surfaces |
| MCP over WebMCP | a page using the browser's `navigator.modelContext` | tool calls and results, while governance is active |
| The tab's HTTP requests | every request the tab makes | a **network log**: host, path, method and content type — **never bodies**; feeds rules on the `http` surface and the graph |
| Conversation history | ChatGPT, claude.ai and Gemini reloading a conversation | governed again when shown, so a redaction applies on reload too; history loads are not recorded as new answers |

**Capabilities per browser.** The extension announces to the engine what the browser
lets it see: `session`, `llm`, `tool`, `skill`, and `http` only where the browser
provides a network log (Chrome, Edge, Firefox). **Safari has no network log**: a rule
that `requires: http` is skipped there and reported as skipped in the popup's status
(§10). Everything on the `llm` and `tool` surfaces works in Safari.

What it does not do: it governs nothing outside the browser, and it never inspects the
desktop client's traffic. On a device where the desktop client governs the browser it
stands down (§3).

---

## 2. How policy reaches it

- The extension reads `GET /api/edge/filters?os=browser` with the signed-in user's own
  credentials. The answer is the enabled **endpoint** filters whose Operating Systems
  list contains **Browser** and whose groups contain the user, guardrails expanded.
- The OS value is `browser`. A desktop OS (Windows, Darwin, Linux, Android, iOS) never
  matches the extension, and a filter with only **Browser** never reaches a desktop
  client. A filter can list both, e.g. Windows + Browser, and then serves both.
- Matching is by the **user's groups** (the browser is not a peer). The group **All**
  matches everyone.
- The filter's **Agents** list is not used by the extension at all: process paths mean
  nothing in a browser. Leave it empty on a browser-only filter; on a mixed filter it
  still steers desktop processes on Windows and macOS.
- Guardrails are optional on the filter, but a browser filter without any judges
  nothing (`29` §1). Several matching filters are merged into one rule set.
- Refresh: the extension loads its filters at sign-in and refreshes them from management
  afterwards; the popup's **Refresh** button forces it. After changing a filter or a
  guardrail, ask the user to press Refresh and read the popup's filters count and rules
  version (§10) rather than waiting.

Confirm the dashboard label before quoting it: in the filter dialog's **Operating
Systems** picker the entry is shown as **Browser**; a customer's build may word it
differently, and theirs wins.

---

## 3. Sign-in and the stand-down rule

**Standalone sign-in.** The user opens the popup and presses **Login**, which opens the
tenant picker at `<your Workplace address>`; signing in there signs the extension in.
The extension keeps the cloud address and its token in its own storage and refreshes
filters from management. The popup shows **Protection: Active** or **Protection:
Inactive** (with a reason when protection is paused), and **Logout**. A refused token
whose renewal failed shows a Login button again: the user is not signed in for real
until they do.

**Stand-down.** When the Netzilo desktop client on the same device governs the browser,
the extension stands down: it neither judges nor reports, so nothing is governed twice.
The rule, so you can predict which side acts:

1. The client **claims the browser** only when the browser process is intercepted by it
   (its executable is in an endpoint filter's Agents, Windows and macOS) **and** the AI
   web hosts (chatgpt.com, claude.ai, gemini.google.com) are within its TLS inspection —
   that is, not on the client's skip list (`10` §3, §11).
2. Before standing down the extension **confirms with management** (`GET /api/peers`)
   that the user has a connected device. If management cannot confirm it, the extension
   stands down only under `fail_mode` open (§4); under `closed` it keeps governing.
3. **Linux:** the desktop client does not steer browser traffic, so the extension is the
   browser enforcement point there even with the client installed.

The popup's status names the state: "the desktop client governs this browser" when
stood down. Both sides produce the same `ai.*` events; only the `source` differs
(`mitm` from the client, `extension` from the browser), so Activity shows which side
acted.

---

## 4. `fail_mode` (managed policy)

A browser-policy setting (`chrome.storage.managed`, key `fail_mode`) decides what
happens while the engine cannot judge a request: it is starting or restarting,
management is unreachable, or the request cannot be read.

| Value | Behaviour |
|---|---|
| `open` (default) | traffic passes unchanged while the engine cannot judge it |
| `closed` | such requests **on AI endpoints** are stopped with an error until the engine can judge them |

Scope: fail-closed applies only to the LLM hosts (§1); every other site always passes.
Set it through the browser's managed-extension policy (the same mechanism as the
force-install policy, §6). There is no dashboard field for it.

---

## 5. What users see

| Verdict | In the page |
|---|---|
| **Redact** | the matched text is replaced by the rule's `replace` token (for example `[CARD-REDACTED]`) — in the prompt as it is sent, in the model's answer as it is shown, and in the copies the app renders from (history, re-renders) |
| **Block** on a prompt | a refusal in the chat. ChatGPT shows an error with the rule's reason; claude.ai and Gemini show the answer **"Netzilo Guardrail: Blocked by rule: <rule name>"** — the model is asked to say exactly that, and the engine enforces the refusal in the answer whatever the model does |
| **Detect** | nothing in the page; an `ai.detected` event |
| **Streamed answers** | the engine releases streamed text about **1 KB behind** the model so a match can be redacted before it is shown: long answers appear with a short delay, short answers appear at once at the end. The same holds on the client and the gateway |
| **Reload** of a signed-in ChatGPT conversation | the messages are briefly hidden until the governed history has loaded, then shown redacted where a rule matches |
| **Reload** of a **logged-out** ChatGPT conversation | **known gap:** the server renders the page and the extension cannot redact it; new prompts and answers in that conversation are governed |

Tell a user who reports "the AI answered with a Netzilo text" that this is the block
verdict of a guardrail, and read the rule's name from the answer or the event.

---

## 6. Browsers and distribution

| Browser | Package | Notes |
|---|---|---|
| Chrome | Chrome Web Store id `kdcpnkonhjcknlkjmjapclhpoamlckji` | force-install: `ExtensionInstallForcelist` = `kdcpnkonhjcknlkjmjapclhpoamlckji;https://clients2.google.com/service/update2/crx` |
| Edge | Edge Add-ons id `efflopncanncclcfnddajplbnmhoebml` | force-install: `efflopncanncclcfnddajplbnmhoebml;https://edge.microsoft.com/extensionwebstorebase/v1/crx` |
| Firefox ≥ 128 | `netzilo-secure-browser` | network log available |
| Safari | the **Netzilo Secure Browser** app, App Store `6740890085`; the Safari extension inside it is named **Netzilo Browser** | enable it under Safari → Settings → Extensions and allow it on all websites; **no network log** (§1) |
| Netzilo Enterprise Browser | bundled | policy from Enterprise Browser profiles; the AI engine as above (`10` §6) |
| Enterprise Browser Android | Firefox-based, ≥ 140 | bundled |

Version line: 5.1.x; the popup shows the installed version. The Netzilo client writes the
force-install policy itself when an **Enterprise Browser Extension** profile applies to
the device and removes it on `service uninstall` (`10` §6); otherwise deploy the policy
with your browser management.

---

## 7. The behaviour graph side

- **Sessions:** one session per browser tab per site (a tab session); a browser session
  is the parent. Conversation reloads stay in the tab's session.
- **Upload:** observations are uploaded in batches to management as the signed-in user
  (`POST /api/aidr/browser/observations`), with the browser's own device
  id. Management records them on that device and for that user only, whatever the batch
  names.
- **Source:** the browser appears in `GET /api/aidr/sources` with `kind: browser`, a
  device (the user's peer when the browser runs on an enrolled device, otherwise the
  browser's own id) and its capabilities.
- **"Session snapshot":** the first time a session shows behaviour, management records
  one activity entry — `aidr.graph`, shown as **Session snapshot**, "Session snapshot is
  available for <program> in the browser" — with the session id, program, device and
  source `extension`; the row opens the session's behaviour graph. Devices no longer
  create these entries; their AI sessions are found in Activity → AI Sessions.
- **Who sees what:** regular users see only their own browser sessions (`GET
  /api/aidr/sources` and `/api/aidr/sessions` answer their own browser sources and their
  own peers); admins see all.
- **Upload limits per user** (management): 2 uploads per second with a burst of 20;
  past that, HTTP 429 `too many uploads, retry later` with `Retry-After: 1`; the
  extension keeps the batch and uploads it again. At most 5000 observations per batch and at most 64
  **new** sessions per batch; observations older than retention or more than 5 minutes
  in the future are dropped, and the answer reports the `dropped` counts by cause
  (`kind`, `time`, `foreign`, `new_sessions`). Session snapshot entries are capped at 60,
  then 120 per hour per user; sessions past the cap are stored but not announced.
- **Rule state:** scripted rules run in the extension as on a device — background
  (`mode: async`) rules, session verdicts and holds included, and `system_one()` through
  management. The state rules keep per session (`32`, "Session State") is saved with the
  extension's own session data, so it survives the browser stopping and restarting the
  extension's worker — but only while a session's whole rule state is at most **32 KiB**,
  and for the 32 most recently changed sessions. A larger state is not saved and starts
  over after a restart.
- **Retention:** observations are kept **7 days** on management (pruned hourly). The
  account's engine keeps up to 50,000 sessions in memory; older ended sessions are
  reloaded from stored observations when opened.

---

## 8. Events

Every verdict is an `ai.blocked`, `ai.redacted`, `ai.redirected` or `ai.detected` event
with:

| Field | Value from the browser |
|---|---|
| `source` | `extension` |
| `agent_name` | the site: `claude.ai`, `chatgpt.com`, `gemini.google.com`, … |
| `program` | the site's origin |
| `session_id` | the tab's session |
| `surface`, `engine`, rule, filter, `content` | as for every source (`30` §1) |

The Activity page phrases them "**<site> in the browser for <user>**: prompt to … —
blocked by rule … | redacted | matched", where a device row would say "<agent>
on <peer> for <user>". A conversation reload that is redacted produces an `ai.redacted`
event with the same tab session and program as the original answer.

A clean call is not an event. Extension 5.2.577 and later records each model call in the
user's AI session (point `browser`), as devices and gateways do, so its calls count in
the AI Agent Activity and AI Usage reports (`30` §2). An older extension records no
sessions; the `ai.allowed` events it sends are dropped by the server.

---

## 9. API

Read-only facts for the agent; nothing here needs to be posted by hand.

```
GET  /api/edge/filters?os=browser                       (any user, own credentials: the endpoint filters that apply to them)
GET  /api/edge/filters ; PUT /api/edge/filters/{id}     (admin: "os":["browser"] on an endpoint filter)
GET  /api/aidr/sources                                  → {sources:[{… kind:"browser", device, capabilities …}]}
GET  /api/aidr/sessions?scope=source:<browser source id>
GET  /api/aidr/observations?scope=session:<session id>
GET  /api/events/paginated?code=ai.blocked&user=<email>  (filter the JSON on source "extension")
POST /api/aidr/browser/observations                     (the extension's own upload; answer {accepted, received, dropped, seq, source})
```

A browser-only endpoint filter:

```json
{"name":"Finance browser AI","enabled":true,"type":"endpoint",
 "os":["browser"],"groups":["<group-id>"],"agents":[],
 "guardrails":["<guardrail-id>"]}
```

`/api/edge/filters/effective?type=endpoint&peer=` answers for a peer; the browser is not
a peer, so judge a browser filter by the user's groups and `os` instead.

---

## 10. Diagnosis

Ask the user for the popup's status first (Debug tab): **state** (ready / booting /
failed / idle), **Protection** Active / Inactive, stand-down, **rules version**,
**filters** count, **rules loaded / failed / skipped** with names, **capabilities**,
browser, active tabs, and the **unmapped** counters. That one screen answers most of the
table.

| Symptom | Cause | Fix |
|---|---|---|
| Not governing: prompts pass, no events | not signed in; no enabled endpoint filter with OS **Browser** for one of the user's groups; filters count 0 | sign in from the popup; add **Browser** to the filter's Operating Systems and the user's group to its groups; Refresh |
| **Protection: Inactive** | no session, or filters known to be empty, or stood down | the status says which; sign in, fix the filter, or see the next row |
| Stands down, but the desktop client does not inspect the AI sites | the client claimed the browser (browser executable in Agents) while the AI hosts are outside its inspection (skip list) — nobody governs them | remove the browser executable from the filter's Agents so the extension governs the browser, or let the client inspect those hosts (`10` §11) |
| Stands down although Peers shows no connected device for the user | a local client claimed the browser and management could not confirm a connected device; under `fail_mode` open the extension stands down anyway (the log says so) | check why the device is not connected (Peers, `07`); set `fail_mode` `closed` where the browser must stay governed in that case |
| Rule **failed** in the status | the guardrail did not compile (regex, YAML); it never fires | fix the guardrail, save, Refresh; the client log reports the same rule as failed |
| Rule **skipped** in Safari | the rule `requires: http` and Safari has no network log | expected; the rule works in Chrome/Edge/Firefox; govern the `llm` surface instead |
| HTTP 429 on uploads in the extension log | more than 2 uploads/s (burst 20) for the user | the extension uploads the batch again later; nothing to do unless it persists, then check for many tabs on AI sites |
| Answer appears late, or all at once | the streamed-answer hold (about 1 KB behind) | expected; say so before a user reports it |
| Reload shows raw (unredacted) text in a **logged-out** ChatGPT conversation | the server renders it; known gap (§5) | sign in to ChatGPT, or accept; new prompts and answers are governed |
| Reload briefly hides messages (signed-in ChatGPT) | the governed history is loading | expected |
| **unmapped** counters rising | traffic on AI endpoints the engine could not read: the site changed its protocol | report to Netzilo with the site and the counters; blocks on the `http` surface still apply |
| Events show `source: mitm`, not `extension`, for browser prompts | the desktop client governs the browser (stand-down) | expected on Windows/macOS when the browser is in Agents |
| Works in Chrome, nothing in Safari | the Netzilo Browser extension not enabled or not allowed on all websites | Safari → Settings → Extensions |
| User sees "Netzilo Guardrail: Blocked by rule: …" as the AI's answer | a block verdict | expected; the rule name is in the text and in the event |

Before escalating: the popup's status screen (state, rules version, filters, failed and
skipped rules, capabilities, unmapped counters), the browser and extension version, one
`ai.*` event's raw JSON, and whether the desktop client is installed on the device.

---

## 11. Limits to state before a customer discovers them

- **A logged-out ChatGPT conversation reopened by reload is not redacted** (server
  rendered); new prompts and answers are.
- **Safari has no network log**: rules on the `http` surface are skipped there and the
  graph has no HTTP requests from Safari.
- **Streamed answers are held about 1 KB behind the model**; users notice a short delay.
- **Fail-closed covers AI endpoints only**, and it is a browser-policy setting, not a
  dashboard one. The default is fail-open.
- **The browser is not a peer**: no posture, no network policy, and
  `/api/edge/filters/effective?peer=` does not describe it; judge by groups and `os`.
- **Observations are kept 7 days**; events are kept like every activity event (`14`).
- **Rule state over 32 KiB per session is not kept** across the extension worker's
  restarts (above); rules that follow a session should keep compact state.
- **Upload pacing is per user** (2/s, burst 20, 64 new sessions per batch, 5000
  observations per batch); a user with many AI tabs sees retries, not loss, unless the
  pace persists.
- **One side governs a browser at a time**: when the desktop client inspects the
  browser, the extension stands down; when the client inspects the browser but not the
  AI hosts, nobody governs those sites until the filter's Agents are corrected.
