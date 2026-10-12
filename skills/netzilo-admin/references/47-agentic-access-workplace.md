---
id: '47'
title: 'Admin Skill — Agentic Access: what users do at the Workplace'
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 14734
sections:
- id: '1'
  title: What the user sees
  chars: 1578
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
  chars: 5050
- id: '6'
  title: What to tell employees
  chars: 1037
---
# Admin Skill — Agentic Access: what users do at the Workplace

**Dashboard:** Workplace → **Agentic Access** (`/workplace#gateways`), for every user,
regular users included. **API the page uses:** `GET /api/users/current/ai-access`,
`/api/users/current/mcp-connections…`, `POST /api/users/{id}/tokens` (scope `mcp`).
**Admin side:** `27-ai-gateway.md`, `29-edge-filters.md` §2.2, `45`, `46`.

This file is what to tell a user, in their words, and what to check when "my agent
cannot reach the gateway". The tab exists only for a user to whom a gateway filter
grants at least one gateway address or one MCP server or bundle; it stays hidden for
everyone else, which is the first thing to check.

---

## 1. What the user sees

Workplace → **Agentic Access**: the counts "{n} gateway(s) · {m} MCP server(s)", a search
box, and two sections.

**LLM Gateways** — one card per gateway address in the user's filters (the admin's name,
or the host when unnamed), its URL with a copy button, the providers' icons (hover: each
provider and its models), a status pill and a square **Connect** button:

| Pill | Meaning |
|---|---|
| **Online · {n} ms** | the browser's probe of `<url>/v1/models` with the user's own session token answered within 8 s |
| **Offline** | it did not (wrong address, gateway down, the gateway refuses the Workplace's origin, or the browser cannot reach the address at all); re-probed every 30 s |
| dot only | first probe not finished |

**MCP Servers** — one card per granted server and bundle (bundles show stacked member
icons and the members' names):

| Pill | Meaning |
|---|---|
| **Online** | the server's `tools/list` answered through the first reachable gateway (15 s, every 60 s) |
| **Offline** | it did not |
| **Needs Attention** (orange ring) | the user still has to connect: per-user sign-in or header values missing, the shared sign-in not done by an admin or needing renewal, or a bundle member pending |

List view adds the authentication state: **Not Required**, **Needs Sign In**, **Needs
Input**, **Authenticated**. Clicking a card opens its dialog; the Connect button opens the
**Connect** tab directly. The empty state reads "No gateway yet — When an AI gateway is
granted to you, it appears here with its models and MCP servers."

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
| No **Agentic Access** tab | `GET /api/users/current/ai-access` as the user: `gateways` and `mcp` empty? | no gateway filter targets a group the user is in, or it has no Gateways entry and no MCP grant → admin: `29` §2.2. The tab also needs the filter **enabled** |
| Card **Offline**, `curl <gateway>/v1/models -H "Authorization: Bearer <token>"` from the same machine works | the gateway refuses the browser's origin | gateway started without `--workplace-url https://go.netzilo.com` (Cloud) / the dashboard's address (self-hosted) → `27` §4 |
| Card **Offline**, curl fails too | the address in the filter's Gateways list is not reachable from the user's network (a tunnel address needs the client connected and a policy to the gateway peer; a published address needs the user in the application's groups) | `27` §5 |
| 401 `a Netzilo credential is required` from the agent | token mistyped, expired (90 days), deleted under Access Tokens, or of another account | create a new token in the dialog |
| 401 from the **Anthropic SDK or Claude Desktop** while curl works | the key was given as `api_key` → sent as `x-api-key`, which the gateway does not accept | pass it as the **auth token** (`ANTHROPIC_AUTH_TOKEN`, `auth_token=`), base `<gateway>/anthropic` |
| 405 `Method Not Allowed` on `/v1/messages` | the Anthropic base URL lacks `/anthropic` | `ANTHROPIC_BASE_URL=<gateway>/anthropic`; Claude Desktop endpoint `<gateway>/anthropic` |
| Claude Desktop: `gateway SSO discovery failed: 401` or `Gateway returned HTTP 405 … /v1/messages` | the endpoint in Claude: `/v1` and `/openai` serve no sign-in (401 at discovery); the bare address signs in but the Anthropic API is under `/anthropic` (405) | endpoint exactly `<gateway>/anthropic`, then **Sign in with your organization** |
| Claude Desktop: `gateway SSO metadata invalid: token_endpoint: must be same-origin as inferenceGatewayBaseUrl` / `gateway SSO: server does not advertise device_authorization_endpoint` / `gateway SSO device init failed: HTTP 400` | `GET <gateway>/anthropic/.well-known/oauth-authorization-server`: endpoints on the gateway's origin with a `device_authorization_endpoint`? | the gateway, the reverse proxy in front of a published address, or management is older than the device sign-in → admin upgrades (`27` §10) |
| Claude shows a code; the approval page says "That code was not found or has expired" | the code as typed; more than 10 minutes since Claude showed it | retype (letters only, `XXXX-XXXX`); start the sign-in again in Claude |
| **Allow** pressed, Claude keeps waiting | Claude polls every 5 s; the approval must be collected within 5 minutes | wait a few seconds; else sign in again (`46` §6.2) |
| Claude Desktop signed in once, now refuses or uses a stale sign-in | the token `Claude (MCP)` under Profile Settings → Access Tokens (revoked or expired: 1 day, refresh 30 days) | sign in again in Claude; as a last resort on macOS reset Claude's remembered sign-in (below) |
| 403 `no model is granted to this user` / `model X is not granted to this user` | Models tab of the dialog lists what they may use | ask for the model, or the admin grants it (`29` §2.2) |
| 429 / 402 | a limit (`45` §2.2) | wait for the window, or the admin raises it |
| 403 `type: netzilo_policy` with a reason | a guardrail blocked the prompt, answer or tool call; the Guardrails tab names the rules that apply | expected; the event in Activity names the rule |
| MCP tool answers `Connect <server> in your Workplace…` | `GET /api/users/current/mcp-connections` → `not_connected` / `needs_reauth` | connect in the dialog (§3) |
| MCP card **Needs Attention** after it worked | `needs_reauth`: the stored sign-in could not be renewed | **Reconnect** |
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
  at the address on your Agentic Access card, with the access token the page creates
  for you. The token is yours; do not share it, and delete it under Profile Settings →
  Access Tokens if it leaks.
- Your prompts and the tools' results are checked against the company's guardrails on
  the way; a refused request says why. What is recorded about your use: which model or
  tool you used, when, how many tokens and what it cost; the text of a prompt only when
  a guardrail matched it (`14-data-handling-and-privacy.md` §3).
- "Needs Attention" on an MCP server means you still have to connect it: open it and
  press Connect.
- In Claude Desktop, set the endpoint to the gateway address followed by `/anthropic`
  and choose **Sign in with your organization**; no token to paste. Claude shows a code
  and opens an approval page: check that the page shows the same code, then press
  **Allow** and return to Claude.
