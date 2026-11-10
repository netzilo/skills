---
id: '47'
title: 'Admin Skill — The Workplace: AI Workspace, Agentic Access, applications and devices'
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 35225
sections:
- id: '0'
  title: The Workplace at a glance
  chars: 1752
- id: '1'
  title: What the user sees
  chars: 1991
- id: '2'
  title: The LLM gateway dialog
  chars: 2948
- id: '3'
  title: The MCP server dialog
  chars: 2724
- id: '4'
  title: What a regular user can do, through the API or the assistant
  chars: 696
- id: '5'
  title: Diagnosis — "my agent cannot use the gateway"
  chars: 5148
- id: '6'
  title: What to tell employees
  chars: 1477
- id: '7'
  title: The AI Workspace (chat)
  chars: 6214
- id: '8'
  title: Applications, devices and private access
  chars: 3097
- id: '9'
  title: 'Where the Workplace runs: dashboard, desktop app, extension'
  chars: 7699
---
# Admin Skill — The Workplace: AI Workspace, Agentic Access, applications and devices

**Dashboard:** `/workplace`, for every user, regular users included. Regular users land
there; admins and owners open it from the company logo in the dashboard header and return
with **Dashboard** in the Workplace menu. The same Workplace is also the **Netzilo desktop
app**'s window and the **Netzilo extension's Workplace page** (the Enterprise Browser's new
tab); §9 covers the three hosts, the workplace picker and when the Workplace shows this
computer's devices. The gateways and MCP servers are the **Gateways &
MCP Servers** panel of the **AI Workspace** section (`/workplace#gateways` opens it).
**API the page uses:** `GET /api/users/current/ai-access`,
`/api/users/current/mcp-connections…`, `POST /api/users/{id}/tokens` (scope `mcp`),
`GET /api/getsecdata`, `GET /api/users/current/published-apps`.
**Admin side:** `27-ai-gateway.md`, `29-edge-filters.md` §2.2, `45`, `46`.

This file is what to tell a user, in their words, and what to check when "my agent
cannot reach the gateway" or "the AI Workspace does not answer". The AI Workspace (with
its panel) exists only for a user to whom a gateway filter grants at least one gateway
address or one MCP server or bundle; it stays hidden for everyone else, which is the first
thing to check. §0 is the page as a whole, §7 the AI Workspace chat, §8 the Applications
section and the Devices panel, §9 where the Workplace runs.

---

## 0. The Workplace at a glance

Three parts, no header:

- **The menu** (left rail, icons; the menu button expands it with labels and the company
  logo, the button next to the logo collapses it, remembered per browser in
  `netzilo.workplace.rail`): **Applications**, **AI Workspace** (only when something is
  granted, see above), **Dashboard** (owners and admins whose role does not block the
  dashboard view, permission `dashboard_view`), and at the bottom **AI
  Assistant** (`42`, `25` permissions) and the user menu (Profile Settings, **Display
  Status**, sign out).
- **The section**: Applications (§8) or AI Workspace (§7). The last one used is remembered
  (`workplaceSection`); a link with `#gateways`, `?connect=<slug>`, `?mcp_connected` or
  `?mcp_error` opens the AI Workspace and, for `connect`, that server's dialog.
- **The panel** on the right belongs to the section: **Devices** next to Applications
  (starts collapsed), **Gateways & MCP Servers** next to the AI Workspace (starts open on
  a wide screen). Collapsed, a panel is a strip of at most 8 marks with status dots (online
  first) and "+N" for the rest; open/closed is remembered per panel.

Responsive: from 1024 px a panel sits beside the section; narrower, an open panel covers
the section as a drawer (closed by its button, a tap outside, or Escape) and panels start
collapsed. Below 768 px the expanded menu also covers the page and folds after a choice.
The Onboarding Progress / System Errors button sits in the bottom-right corner (Windows,
macOS, iOS only, `17` §3 row "System Errors"; in the dashboard only, never in the desktop
app or the extension's page). The previous layout (header, tabs
Applications | Devices | Agentic Access) stays at **`/my`**.

---

## 1. What the user sees

Workplace → **AI Workspace** → the **Gateways & MCP Servers** panel: a search box
(gateways by name and address; servers by name, description and slug) and two sections,
each with its count. (In the previous layout at `/my`, the same lists are the **Agentic
Access** tab as cards.)

**LLM Gateways** — one row per gateway address in the user's filters (the admin's name,
or the host when unnamed), its URL, a status, the providers' icons (hover: each provider
and its models) and a square connect button:

| Pill | Meaning |
|---|---|
| **Online · {n} ms** | the browser's probe of `<url>/v1/models` with the user's own session token answered within 8 s |
| **Offline** | it did not (wrong address, gateway down, the gateway refuses the Workplace's origin, or the browser cannot reach the address at all); re-probed every 30 s while the AI Workspace is on screen and the tab visible — on Applications nothing is probed |
| dot only | first probe not finished |

**MCP Servers** — one row per granted server and bundle (bundles show stacked member
icons; the description, or the members' names), with its status, its authentication state
and a connect button:

| Pill | Meaning |
|---|---|
| **Online** | the server's `tools/list` answered through the first reachable gateway (every 60 s while the AI Workspace is on screen; each check's MCP session is closed with `DELETE` afterwards) |
| **Offline** | it did not |
| **Needs Attention** (orange ring) | the user still has to connect: per-user sign-in or header values missing, the shared sign-in not done by an admin or needing renewal, or a bundle member pending |

The authentication state is **Not Required**, **Needs Sign In**, **Needs Input** or
**Authenticated**. Clicking a row opens its dialog; the connect button opens the
**Connect** tab directly. **Use in code** (top of the AI Workspace) opens the **Connect**
tab of the gateway serving the chosen model, with that model in every snippet (§7.6).

---

## 2. The LLM gateway dialog

Tabs **Connect | Models | Guardrails | Details**. The Details tab lists Status, Latency,
**OpenAI API** `<gateway>/v1`, **Anthropic API** `<gateway>/anthropic`, **MCP**
`<gateway>/mcp/…`. Models lists what the gateway answered (or, when unreachable, what the
filters grant), each with a copy button. Guardrails lists the guardrails that apply to
the user's traffic.

**Connect** has one tab per client; each shows three steps:

1. **Gateway address** — `<gateway>/v1` for the OpenAI clients (Python, Node.js, Cursor),
   `<gateway>/anthropic` for Claude Code and the Anthropic SDK, `<gateway>` for curl.
2. **Access token** — **Create Access Token**: the page creates a personal access token
   named **AI Gateway**, valid **90 days**, scope `mcp` (it can only identify the user to
   gateways, nothing else on the API). The value is kept in this browser only
   (`localStorage`), shown masked as `nzl_******`, and the copy button copies the real
   value. In another browser the user creates another token; the old one stays valid
   until it expires or is deleted under Profile Settings → Access Tokens. Failure toast:
   "The access token could not be created."
3. The client-specific snippet, with the token filled in once it exists
   (`<your access token>` before).

| Client | What the snippet does |
|---|---|
| **Claude Code** | `export ANTHROPIC_BASE_URL="<gateway>/anthropic"`, `export ANTHROPIC_AUTH_TOKEN="<token>"`, `export ANTHROPIC_MODEL="<model>"`, then `claude` |
| **Python** (OpenAI SDK) | `OpenAI(base_url="<gateway>/v1", api_key="<token>")` + `chat.completions.create(model=…)` |
| **Node.js** (OpenAI SDK) | `new OpenAI({ baseURL: "<gateway>/v1", apiKey: "<token>" })` |
| **Anthropic SDK** | `anthropic.Anthropic(base_url="<gateway>/anthropic", auth_token="<token>")` — `auth_token`, not `api_key` (§5) |
| **Cursor** | Settings → Models: OpenAI API Key = token, Override OpenAI Base URL = `<gateway>/v1`, Model = `<model>` |
| **curl** | `curl <gateway>/v1/chat/completions -H "Authorization: Bearer <token>" …` |
| **Claude Desktop** (no tab in the dialog; set up in Claude itself) | endpoint **`<gateway>/anthropic`** (exactly), then **Sign in with your organization** — no token needed: Claude shows a code, the browser opens the approval page, the user checks the code and presses **Allow** (`46` §6.2). Alternatively the access token above as the API key |

`<model>` is the first model the gateway listed for the user. Any OpenAI-compatible
client works the same way: base URL `<gateway>/v1`, API key = the token. Any
Anthropic-compatible client: base URL `<gateway>/anthropic`, the token as a **Bearer**
(auth token), model names as the admin's provider lists them. Claude Desktop's
organization sign-in works only with the `<gateway>/anthropic` endpoint: `/v1` serves no
sign-in, and the bare address signs in but cannot serve Claude's requests (they belong
under `/anthropic`).

---

## 3. The MCP server dialog

Tabs **Overview | Connect | Tools | Guardrails**. Overview shows a status panel and the
rows Endpoint `<gateway>/mcp/<slug>`, Transport "Streamable HTTP", Authentication,
Servers (bundles), Documentation. The panel is where a user connects:

| Situation | Panel | Action |
|---|---|---|
| Per-user OAuth, not connected | "Connect your {name} account to use its tools" | **Connect** → the provider's sign-in opens in a popup ("Complete the sign-in in the window that opened", Cancel); success toast "The server is connected for you." |
| Per-user OAuth, expired | "Your {name} connection expired" | **Reconnect** |
| Per-user headers | one password input per declared header name | **Connect** / **Reconnect**; refused values: "Could not connect" + `the server refused these values (HTTP 401)` |
| Shared OAuth, admin not signed in | "An admin has not connected this server yet." | the admin signs in (`46` §2) |
| Bundle with a pending member | "Finish setting up {names} to use all of its tools." | connect those servers first |
| Connected | "{n} tools · Connected {at}" | **Disconnect** (per-user auth only) |

Failure toasts: "Could not connect" with "The sign-in was not completed within 10
minutes." / "The browser blocked the sign-in window. Allow pop-ups for this site and try
again." / the server's own text.

**Connect** tab, per client (`<name>` is the slug with dashes replaced by underscores;
`<endpoint>` is `<gateway>/mcp/<slug>`):

| Client | Steps |
|---|---|
| **Claude Code** | Access token → `claude mcp add --transport http <name> <endpoint> --header "Authorization: Bearer <token>"` → `claude mcp list` |
| **Cursor** | Access token → **Add to Cursor** (one-click deep link) → or `~/.cursor/mcp.json`: `{"mcpServers":{"<name>":{"url":"<endpoint>","headers":{"Authorization":"Bearer <token>"}}}}` |
| **VS Code** | Access token → **Add to VS Code** → or `.vscode/mcp.json`: `{"servers":{"<name>":{"type":"http","url":"<endpoint>","headers":{"Authorization":"Bearer <token>"}}}}` |
| **Claude Desktop** | Settings → Connectors → Add custom connector → paste `<endpoint>` → "Sign in with your Netzilo account when asked" (no token: the connector signs in through OAuth, `46` §6, and the user approves on the consent page) |
| **curl** | `curl <endpoint> -H "Authorization: Bearer <token>" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'` |

**Tools** lists the server's tools as a gateway reports them ("Tools appear once the setup
is finished." / "No gateway answered yet; tools appear when one does." / "The gateway did
not list tools for this server."). **Guardrails** lists the guardrails that apply.

---

## 4. What a regular user can do, through the API or the assistant

With their own token (no admin): `GET /api/users/current/ai-access` (their gateways,
models, MCP servers with connection state, bundles, guardrails),
`GET /api/users/current/mcp-connections`, the connect/complete/headers/disconnect calls
of `46` §4, `POST /api/users/{own id}/tokens` and `DELETE` of their own tokens,
`GET /api/users/{own id}/gateway-sessions`. They cannot read filters, providers, limits
or servers as objects: what they get is the Workplace's view. An assistant session with a
regular user (`39-end-user-self-service.md`) can read those and tell the user what they
are granted; it cannot change grants.

---

## 5. Diagnosis — "my agent cannot use the gateway"

| Symptom | Check | Cause → fix |
|---|---|---|
| No **AI Workspace** in the Workplace menu (no **Agentic Access** tab at `/my`) | `GET /api/users/current/ai-access` as the user: `gateways` and `mcp` empty? | no gateway filter targets a group the user is in, or it has no Gateways entry and no MCP grant → admin: `29` §2.2. It also needs the filter **enabled** |
| Gateway **Offline**, `curl <gateway>/v1/models -H "Authorization: Bearer <token>"` from the same machine works | the gateway refuses the browser's origin | gateway started without `--workplace-url https://go.netzilo.com` (Cloud) / the dashboard's address (self-hosted) → `27` §4 |
| Gateway **Offline**, curl fails too | the address in the filter's Gateways list is not reachable from the user's network (a tunnel address needs the client connected and a policy to the gateway peer; a published address needs the user in the application's groups) | `27` §5 |
| 401 `a Netzilo credential is required` from the agent | token mistyped, expired (90 days), deleted under Access Tokens, or of another account | create a new token in the dialog |
| 401 from the **Anthropic SDK or Claude Desktop** while curl works | the key was given as `api_key` → sent as `x-api-key`, which the gateway does not accept | pass it as the **auth token** (`ANTHROPIC_AUTH_TOKEN`, `auth_token=`), base `<gateway>/anthropic` |
| 405 `Method Not Allowed` on `/v1/messages` | the Anthropic base URL lacks `/anthropic` | `ANTHROPIC_BASE_URL=<gateway>/anthropic`; Claude Desktop endpoint `<gateway>/anthropic` |
| Claude Desktop: `gateway SSO discovery failed: 401` or `Gateway returned HTTP 405 … /v1/messages` | the endpoint in Claude: `/v1` and `/openai` serve no sign-in (401 at discovery); the bare address signs in but the Anthropic API is under `/anthropic` (405) | endpoint exactly `<gateway>/anthropic`, then **Sign in with your organization** |
| Claude Desktop: `gateway SSO metadata invalid: token_endpoint: must be same-origin as inferenceGatewayBaseUrl` / `gateway SSO: server does not advertise device_authorization_endpoint` / `gateway SSO device init failed: HTTP 400` | `GET <gateway>/anthropic/.well-known/oauth-authorization-server`: endpoints on the gateway's origin with a `device_authorization_endpoint`? | the gateway, the reverse proxy in front of a published address, or management is older than the device sign-in → admin upgrades (`27` §10) |
| Claude shows a code; the approval page says "That code was not found or has expired" | the code as typed; more than 10 minutes since Claude showed it | retype (letters only, `XXXX-XXXX`); start the sign-in again in Claude |
| **Allow** pressed, Claude keeps waiting | Claude polls every 5 s; the approval must be collected within 5 minutes | wait a few seconds; else sign in again (`46` §6.2) |
| Claude Desktop signed in once, now refuses or uses a stale sign-in | the token `Claude (MCP)` under Profile Settings → Access Tokens (revoked or expired: 1 day, refresh 30 days) | sign in again in Claude; as a last resort on macOS reset Claude's remembered sign-in (below) |
| 400 (older gateways 403) `no model is granted to this user` / `model X is not granted to this user` | Models tab of the dialog lists what they may use | ask for the model, or the admin grants it (`29` §2.2) |
| 429 / 402 | a limit (`45` §2.2) | wait for the window, or the admin raises it |
| 400 `type: netzilo_policy` with a reason (older gateways 403) | a guardrail blocked the prompt, answer or tool call; the Guardrails tab names the rules that apply | expected; the event in Activity names the rule |
| MCP tool answers `Connect <server> in your Workplace…` | `GET /api/users/current/mcp-connections` → `not_connected` / `needs_reauth` | connect in the dialog (§3) |
| MCP server **Needs Attention** after it worked | `needs_reauth`: the stored sign-in could not be renewed | **Reconnect** |
| Claude Desktop connector asks to sign in, then fails | the consent page was denied, or management is not reachable under its dashboard host | retry, Allow; `46` §6 |
| "The access token could not be created." | the user may not create tokens (blocked user), or the request failed | `GET /api/users/{id}/tokens` as the user; Profile Settings → Access Tokens |
| Everything works for the admin, not for a user | the admin's filters differ; the user's groups | compare `GET /api/edge/filters/effective?type=gateway&user=<id>` for both (admin token) |

**Resetting Claude Desktop's remembered sign-in** (macOS, last resort): quit Claude; its
gateway-mode data is under `~/Library/Application Support/Claude-3p/`; the remembered
sign-in is the key `custom3pGatewaySso` in `config.json` there (remove the key, keep a
backup); the gateway settings are in `configLibrary/` (move it aside to get the setup
screen back). Other OSes: the equivalent application-data folder.

**Evidence to collect** before escalating: the dialog's Details tab values, the exact
error body (no token), `GET /api/users/current/ai-access` as the user, and the gateway's
`gateway ai: refused …` or `cannot identify …` log line (`27` §9.2).

---

## 6. What to tell employees

- The gateway is how your AI tools reach the company's models and tools. Point the tool
  at the gateway address shown in the Workplace's AI Workspace, with the access token the
  page creates for you. The token is yours; do not share it, and delete it under Profile Settings →
  Access Tokens if it leaks.
- Your prompts and the tools' results are checked against the company's guardrails on
  the way; a refused request says why. What is recorded about your use: which model or
  tool you used, when, how many tokens and what it cost, and the conversation itself —
  your prompts, the answers and the tools' arguments and results — as it passed the
  guardrails; text a guardrail redacted stays redacted (`14-data-handling-and-privacy.md`
  §3). The AI Workspace is recorded the same way.
- "Needs Attention" on an MCP server means you still have to connect it: open it and
  press Connect.
- In Claude Desktop, set the endpoint to the gateway address followed by `/anthropic`
  and choose **Sign in with your organization**; no token to paste. Claude shows a code
  and opens an approval page: check that the page shows the same code, then press
  **Allow** and return to Claude.
- The AI Workspace is the company's own chat over the same gateway, with your Workplace
  sign-in. In **Manual** nothing runs without you: read a tool's request before you allow
  it. Your chat history stays in this browser and is removed when you sign out.

---

## 7. The AI Workspace (chat)

Workplace → **AI Workspace**: a chat with the models the user's gateways serve them, and
the tools of the MCP servers they attach. It is an ordinary client of the gateway: model
grants, limits (`45`) and guardrails (`28`) apply, and the gateway records the traffic as
it records every client's (`14` §3, `30`).

### 7.1 What it sends, and as whom

- **Model calls**: the browser posts `<gateway>/v1/chat/completions` (OpenAI format,
  `stream: true`, `tools` from the attached servers) to the gateway serving the chosen
  model, with `Authorization: Bearer <the user's dashboard session token>` — the same
  credential the panel's probes use, so no access token is created for it. The gateway
  must accept the Workplace's origin (`--workplace-url`, `27` §4), exactly as for the
  probes.
- **Tools**: per attached server an MCP streamable-HTTP session on
  `<gateway>/mcp/<slug>` (`initialize`, `tools/list`, `tools/call`; re-initialized once
  when the server answers 404 for an expired session; ended with `DELETE` when the server
  is detached). Tool calls time out after 120 s, other calls after 30 s.
- **No system prompt**: the model receives only the conversation, the attached files and
  the tool descriptions. Images go as `image_url` data URLs; text files are inlined in the
  user message as a fenced block under the file name.
- A turn the gateway refused (an error and no text) is left out of later requests
  together with the prompt before it, so one refusal does not poison the conversation.

### 7.2 Choosing a model

The picker lists the models of every gateway that answers `/v1/models`, grouped by
gateway (when more than one) and provider, searchable by model, provider or gateway. The
choice is `{gateway, model}` and is remembered per browser (`netzilo.playground.model`);
the chat goes to that gateway. While that gateway misses a probe, the choice stays and
**Send** is disabled with "No gateway answers right now."; it moves to another model only
when the gateway is no longer granted or no longer serves the model.

### 7.3 Attachments

The **+** button: **Add files** (images ≤ 5 MB, text ≤ 200 KB — `text/*`, `.json`, `.md`,
`.csv`, `.yaml`, `.yml`, `.log`, `.xml`; a larger file is silently not added) and one switch
per granted MCP server and bundle. A server in **Needs Attention** has a connect button
instead of a switch (opens its dialog's **Connect** tab, §3). The composer shows "{n} MCP
server(s) · {m} tool(s)", or "The tools of {name} could not be loaded." when `tools/list`
failed. Function names are the MCP tool names reduced to `[A-Za-z0-9_-]`, at most 64
characters, with `_2`… on a clash, assigned in server-id order so they stay stable.

### 7.4 Tool calls: Manual and Autopilot

Under the message box, **Manual | Autopilot**; **Manual** on every page load (not
remembered).

| Mode / button | Effect |
|---|---|
| Manual: card "Allow the model to use {tool} from {server}?" with **Request** (the arguments) | waits for the user per call |
| **Allow once** | runs this call |
| **Allow for this chat** | runs it and every later call of the same tool of the same server in this conversation (keyed by server id + MCP tool name); a new or reopened chat asks again |
| **Deny** | not run; the model receives "The user did not allow this tool call." as the result |
| **Autopilot** | runs every call without asking; switching it on runs the waiting calls; after **10** consecutive rounds without the user the next calls wait again (reset by a send or a manual decision) |
| **Stop** (square button, while a reply streams or a tool runs) | aborts the stream and running tool calls (marked **Failed** with "Stopped."); nothing continues on its own until the user sends or decides |

The model continues once every call of its turn is decided. Each call then shows as a row
(server mark, tool, server, **Running** / check / **Failed** / **Denied**) that expands to
**Request** and **Response**.

### 7.5 History and what the browser keeps

The history button: **New chat**, **Search chats...** (title, model, message text, tool
and server names), the conversations. Kept in the browser only, per user
(`localStorage` `netzilo.playground.<userId>`): the last **20** conversations with text,
tool calls and results; images are kept as names only; when the browser's quota is
reached the oldest go first. The dashboard's sign-out removes every `netzilo.playground.*`
key. Reopening a chat restores its model (when its gateway still serves it) and its
attached servers, not its **Allow for this chat** permissions. Starting or opening a chat
stops a reply still running for the previous one; that reply never lands in the other
chat. Images in model answers render as links and are never fetched.

### 7.6 Use in code

**Use in code** opens the gateway dialog's **Connect** tab (§2) with the chosen model as
`<model>` in every snippet.

### 7.7 Diagnosis

| Symptom | Check | Cause → fix |
|---|---|---|
| "No gateway answers right now." and Send disabled | the panel's gateway status | the probe fails from this browser: §5 rows "Gateway **Offline**" |
| Model list says "No models" | `/v1/models` with the user's token | the gateway answers but grants no model → `29` §2.2; or no gateway answers |
| "Refused: …" | the text after "Refused:" — the gateway's error message | same causes as §5 (model not granted, 429/402 limits, `netzilo_policy` guardrail, 401); a network failure also shows here as "Failed to fetch" |
| "The response was blocked by a content filter." | — | the stream ended with `finish_reason: content_filter` and no text |
| "The tools of {name} could not be loaded." | the server's status in the panel | `tools/list` failed through the gateway: `46` §8 |
| A tool call **Failed** | expand it: the Response | the server's error, `unknown tool …` (the server was detached), "Stopped." (the user pressed Stop), or a 120 s timeout |
| Calls wait in Autopilot | — | 10 rounds in a row ran without the user; allow or deny to continue |
| An image gets no answer about it | the model | the model does not take images |
| A chat is gone | — | another browser, a sign-out, more than 20 chats, or the browser's storage quota |

---

## 8. Applications, devices and private access

### 8.1 Applications

Tiles from the extension profiles' bookmarks (`26`), the Enterprise Browser's bookmarks when
opened there, published applications (`44`) and the client's shortcuts (Enterprise
Workspace). Header: greeting, "{n} apps", **Grid view** / **List view** (remembered,
`viewMode`), search (name and address), filters **All** (the page opens on it every
time) / **Recent** (the 5 last opened in this browser) / **Shortcuts** (web tiles) / one
per profile with client shortcuts. Tiles have a fixed size; opened > 5 times in this
browser = 2 wide, > 10 = 2 × 2 with "Last used: {date}" (`apps_history`); on a phone
every tile is one cell.

**Status pill** (web tiles: bookmarks and published applications with an `https://` or
scheme-less address): the browser sends `HEAD` with `mode: no-cors`, no credentials and
no cache, 8 s timeout, at most 6 at a time, on load and every 60 s while the page is
visible. Any answer (a sign-in page, 401, 403, 404) = **Online**; no answer = **Offline**.
It measures this browser's reach: an app behind Netzilo is Online only while this
computer's client or this browser's private access is connected. **No pill** for an
`http://` address (an https page may not request http — the browser blocks it before it
leaves; no workaround from the page) and for client shortcuts. To get a status, serve the
app over HTTPS or publish it (`44`).

### 8.2 Devices panel

Reads the local Netzilo client (websocket `localhost:41336`/`41337`) — this computer's
client only, and only when that client is the signed-in user's own connected device on
the same server (§9.3); any other client shows as not signed in, with no devices. Collapsed by default: up to 8 device marks (online first, green/red dot),
"+N"; with no device one status mark ("Netzilo client not reachable", "Retrieving your
devices...", "No devices"). Open: **Search devices...** (name, IP), the count (from
10,000 shortened, e.g. 12.3K; exact on hover), dots with online/total, **All | Online**,
rows (FQDN, IP, Online/Offline, latency badge, **P2P** / **Relayed**) with an **IP** button
(copies the IP) and a copy button (copies the domain), 200 rows at a time as the list
scrolls. A row opens the device dialog: Connection Status (Status, Connection Type),
Network Information (Hostname, IP Address, Local/Remote Candidate), Performance (Latency,
Quality Excellent/Good/Fair/Poor). For the first 5 minutes after the page opens an empty
or all-offline list keeps "searching".

### 8.3 Private access

Without a connected client, when the Netzilo extension in this browser routes through a
gateway, the panel shows a **Private access** section in place of the devices: one row
**This browser** with the gateway and **Online** / **Suspended**; its dialog shows Gateway,
Session, Address, Connected, Extension and, when suspended, the extension's reason in
parentheses. A globe mark stands for it on the collapsed strip. The data is the
extension's own answer, asked every 15 s while the page is visible
(`43-clientless-access-gateway.md` §3).

---

## 9. Where the Workplace runs: dashboard, desktop app, extension

### 9.1 Three hosts, one Workplace

The Workplace of §0–§8 is one page shown in three places. What it shows and does is the
same everywhere; how the user gets there and signs in differs.

| Host | How the user opens it | Signed out | Signed in with |
|---|---|---|---|
| The dashboard, `https://<dashboard>/workplace` (Netzilo Cloud: `https://go.netzilo.com/workplace`) | the address; regular users land there after sign-in | the dashboard's own sign-in | the dashboard session |
| The **Netzilo desktop app** (macOS, Windows, Linux): its window | the app opens with its window; tray menu → **Open...**; starting the app again; on macOS the Dock icon (`06` §5) | the workplace picker (§9.2) | the Netzilo client's own sign-in: no second sign-in |
| The **Netzilo extension's Workplace page** | the **Workplace** button (grid icon) at the top of the extension popup opens it in a new tab. In the **Enterprise Browser** the same page is the new tab and home page | the workplace picker (§9.2) | the extension's sign-in (the Enterprise Browser's own) |

Differences by host:

- **Onboarding Progress / System Errors** (§0) shows in the dashboard only.
- **Dashboard** in the menu shows for owners and admins whose role does not block the
  dashboard view; in the desktop app and the extension's page it opens the dashboard in
  the browser.
- **Enterprise Browser:** its bookmarks join the Applications (§8.1), and the Devices
  panel reads its built-in client.
- **Desktop app:** the Devices panel skips the ownership check of §9.3: the app signs the
  Workplace in with its own client's sign-in, so it is the same user on the same server.

### 9.2 The workplace picker (desktop app and extension page, signed out)

Heading **Welcome Back!**, text "Pick a workplace and press "Connect" to continue.", and a
list: **Default Workplace** first (it cannot be forgotten), then the workplaces the user
added, the most recently used first. Each row shows the name and address and a
**Connect** button; added rows have a ⋮ menu with **Forget workplace**. Below the list,
"or define a new workplace" and **Add Workplace** open **Add a workplace**: one address
field and **Next**. After **Connect**: **Redirecting...** "Taking you to your identity
provider for authentication." with **Cancel**. The Enterprise Browser also shows
**Logging in...** and **Logging out...** cards, each with **Cancel**, while it signs in or
out.

| | Desktop app | Extension (in the user's own browser) | Enterprise Browser |
|---|---|---|---|
| **Default Workplace** | the deployment's `NETZILOSRV` value, else the management server the client service was set up with, else Netzilo Cloud | Netzilo Cloud (`https://go.netzilo.com`); with the managed lock, the locked workplace | the tenant from the installer (`TENANT` / `--netzilo-tenant`, `48` §13.1); Netzilo Cloud when none was set |
| Add asks for | **Management server URL** (placeholder `https://srv.your-company.com`) | **Workplace URL** (placeholder `https://your-workspace.netzilo.com`) | **Workplace URL** |
| An address is accepted when | the server's API answers at it (`GET <address>/api/users` returns 401 or 403 without a token, within 8 s) | `https://<address>/.well-known/netzilo.json` answers as a Netzilo Server (https only) | same as the extension |
| **Connect** does | signs the computer's Netzilo client in at that server and connects it: the client then belongs to that server until the user connects another | signs the extension in at that workplace; the sign-in opens in the same tab | signs the browser in at that workplace |
| The list is kept in | the user's config folder: `~/Library/Application Support/Netzilo/workplaces.json` (macOS), `%AppData%\Netzilo\workplaces.json` (Windows), `~/.config/Netzilo/workplaces.json` (Linux) | the extension's workplace registry (`43-clientless-access-gateway.md` §3.4a) | the browser's own list |
| Managed lock | — | with the extension's managed policy `lockPortal` + `activePortal` the picker shows only that workplace, with no Add and no Forget | installed with `FORCETENANT=1`: the picker lists only the tenant, with **Connect**, no Add and no Forget, also after a logout, and signing in elsewhere is refused (`48` §13.5) |

The name on a row comes from the workplace's `/.well-known/netzilo.json` (§9.4); without
one the row shows the address. The desktop app learns the name after the first sign-in.

Errors under the address field or on the picker:

| Message | Cause | Fix |
|---|---|---|
| "Enter a valid https address." | the text is not an `https://` address | type the address as `https://<host>` |
| "This address is not a Netzilo workplace." | the extension: `https://<address>/.well-known/netzilo.json` did not answer as a Netzilo Server (wrong address, a dashboard older than the file, a proxy blocking `/.well-known/`, the address not reachable from this computer). The desktop app: the management API did not answer 401/403 at that address (a dashboard address given instead of the management address, or not reachable) | `curl -s https://<address>/.well-known/netzilo.json` (extension) or `curl -sS -o /dev/null -w "%{http_code}\n" https://<address>/api/users` → `401` (desktop app) from the same computer |
| "Sign-in did not complete." | the identity provider's sign-in was cancelled, failed or timed out | Connect again; for the desktop app the client's sign-in messages are in `07-client-troubleshooting.md` §2 |

### 9.3 This computer's devices: only the user's own client

The Devices panel (§8.2) and the client shortcuts (§8.1) come from the Netzilo client on
the computer the Workplace is open on. The Workplace shows them only when that client is
**the signed-in user's own device, connected to the same server**: it asks management
`GET /api/users/current/device?key=<the client's WireGuard public key>`, which answers
with the device's peer id when the caller registered that device and it is connected to
this server now, and 404 otherwise. The answer is kept for 60 s per user, key and server.

Any other client shows as a client that is not signed in: **No devices** in the Devices
panel, no client shortcuts, and, with Display Status on, the System Errors panel reports
the management connection as down. That happens when:

- the client on this computer is signed in as **another user**;
- the client was enrolled with a **setup key** (the peer has no user);
- the client is connected to **another server** (another account or another Netzilo
  Server) than the Workplace;
- the client is **not connected** (signed out, login expired, service stopped).

Check with an admin token: the device in `GET /api/peers` (search by name), its `user_id`
against the user's id and `connected: true`. Fix by signing the client in as that user on
that server (`netzilo up` or the desktop app's **Connect**), or accept it: a shared or
setup-key machine never shows its devices in a personal Workplace. The desktop app skips
this check (§9.1).

### 9.4 The workplace's name

The dashboard serves `/.well-known/netzilo.json` with `"product": "netzilo-server"`, the
API and management addresses, `"name"` and `"client_auth": ["pkce"]`. `name` is what the
desktop app, the extension and its connect confirmation show for the workplace; it comes
from the dashboard container's environment variable `NETZILO_WORKPLACE_NAME` and is empty
when that is unset (the picker then shows the address). Self-hosted: set it in the
dashboard's environment (`02-server-operations.md` §5) and recreate the dashboard
container. `client_auth` tells the Netzilo client that the dashboard can hand its sign-in
over (`04-identity-and-sso.md` §10).
