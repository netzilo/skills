---
id: '27'
title: Admin Skill — Edge Tools (MCP servers) and Discovered Tools
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 7605
sections:
- id: '1'
  title: Model
  chars: 1145
- id: '2'
  title: Field reference (Add / Edit Tool)
  chars: 2127
- id: '3'
  title: API
  chars: 1114
- id: '4'
  title: Procedures
  chars: 1293
- id: '5'
  title: Diagnosis
  chars: 1425
---
# Admin Skill — Edge Tools (MCP servers) and Discovered Tools

**Dashboard:** Edge → **Tools** (`/ai-edge/tools`, tabs **Approved** / **Discovered**).
**API:** `/api/edge/tools`, `/api/edge/tools/catalog`, `/api/edge/discovered-tools`.
**Licence:** Enterprise.

Tools are the MCP servers (and their tool functions) that AI agents may call. Approved
tools are bound to devices through **Filters** (`29-edge-filters.md`); everything else
can be observed as **Discovered** and approved or blocked.

---

## 1. Model

- **Catalog** = global tools provided by Netzilo (badge **Premium**, read-only) + the
  account's own tools.
- A **tool** has a transport: `stdio` (command + args + env, launched locally by the
  gateway), `sse`, or `streamable_http` (URL + optional HTTP headers).
- A **filter** lists tool IDs; the special entry **Unsanctioned Tools** (wildcard) matches
  any MCP tool not explicitly approved — use it to block or record shadow MCP usage.
- **Discovered Tools**: MCP servers seen by devices but not approved, with status
  **Pending Review** → **Approved** or **Blocked**; each shows first seen, usage (peers,
  users, allowed/blocked calls), tool functions observed, users/groups, and an AI risk
  assessment (requires an OpenAI or Anthropic integration).
- Disabling a tool blocks it everywhere immediately; deleting requires that no filter
  uses it.
- Devices reach approved tools either directly (MCP over HTTPS intercepted by the client)
  or via the local MCP gateway on `http://127.0.0.1:41338/mcp` (`/sse`), which the
  Workplace → Tools → **Use Tools** button configures for Cursor, VS Code and generic
  clients.

---

## 2. Field reference (Add / Edit Tool)

Tabs **General** → **Details** → **Name & Description** (later tabs unlock when the
previous one is valid).

| Tab | Field | UI help | Rules |
|---|---|---|---|
| General | Icon | "Provide an icon URL for this tool (required)." | URL, e.g. `https://www.google.com/s2/favicons?domain=example.com` |
| General | Categories | "Group tools by functionality or domain (optional)." | at least one is required on save ("At least one category is required"); type + Enter |
| General | Enable Tool | "Use this switch to enable or disable the tool." | disabled tool = blocked for everyone |
| Details | Type | "Select stdio for command-line tools or http for web services." | `stdio`, `sse`, `streamable_http` |
| Details (http) | URL | "The HTTP endpoint URL for this tool (required for HTTP-based tools)." | |
| Details (http) | HTTP Headers (optional) | "Optional HTTP headers to include with requests to this tool." | name/value (e.g. `Authorization`) |
| Details (stdio) | Command | "Command is required, like: npx -y @modelcontextprotocol/server-postgres" | |
| Details (stdio) | Arguments (optional) / Environment Variables (optional) | | |
| Name & Description | Tool Name / Description | "Set an easily identifiable name for your tool." | both required |

Table (Approved): Name (icon, description), Active toggle (Premium: disabled), Type
pill, Category, **Used by** (n Filters), Edit / Delete (disabled while used: "This tool
is used by n filter(s) and cannot be deleted."). Filter by transport.

Discovered table: Name (favicon, server name, URL, transport), First Seen, Usage (peers,
users), Risk (Unknown / Low / Medium / High; **Analyze** when an AI integration exists;
otherwise "Connect AI providers using Integrations section to get risk analysis on this
tool"), Status (Pending Review / Approved / Blocked), **Approve**, dismiss (trash).
Detail modal tabs: General (status, URL, transport, first seen, peers, users, allowed
calls, blocked calls), Tools (observed tool functions with call/blocked counts), Users
(groups and users), Security (risk assessment and factors).

---

## 3. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/edge/tools ; GET /api/edge/tools/catalog ; GET/PUT/DELETE /api/edge/tools/{id}
GET /api/edge/discovered-tools ; POST /api/edge/discovered-tools/{id}/sanction {"tool_id":"…"}
POST /api/edge/discovered-tools/{id}/block ; POST /api/edge/discovered-tools/{id}/analyze ; DELETE /api/edge/discovered-tools/{id}
```
Tool body:
```json
{"name":"github","transport":"streamable_http","description":"GitHub MCP",
 "url":"https://api.githubcopilot.com/mcp/","env":{"Authorization":"Bearer …"},
 "categories":["Developer Tools"],"icon":"https://www.google.com/s2/favicons?domain=github.com","enabled":true}
```
stdio: `{"transport":"stdio","command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","/data"],"env":{"KEY":"value"}}`.
For HTTP transports the headers are stored in `env`.

---

## 4. Procedures

### 4.1 Approve what your teams already use
1. Roll out a filter with **Unsanctioned Tools** in **report** posture first (scanners in
   report mode) so usage is recorded without blocking.
2. Edge → Tools → **Discovered**: review each server (Users tab shows who), **Analyze**
   for risk, **Approve** (pre-fills a tool from the server URL; add categories and icon),
   or dismiss.
3. Add the approved tools to the relevant filters (Filters → Tools tab).
4. Switch the filters' scanners to block where appropriate; keep **Unsanctioned Tools**
   in the filter so new shadow servers are blocked and still recorded.

### 4.2 Register a private MCP server
Add Tool → `streamable_http` or `sse`, URL, headers for auth → categories → name. Then
bind in a filter. Devices see it in Workplace → Tools; Cursor/VS Code get it through the
local gateway config.

### 4.3 Local stdio server for developers
Add Tool `stdio` with the command the gateway should launch (e.g. `npx -y @mcp/server-postgres`),
environment variables for credentials. The command runs on the developer's machine
through the client's gateway.

### 4.4 Ban a server outright
Discovered → **block** (API `…/block`), or approve then disable. Blocked calls appear as
`tool.explicitly_blocked` / `tool.blocked`.

---

## 5. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Nothing appears under Discovered | no filter applies to the devices, or AI traffic is not intercepted (Linux, app not in filter Agents) | `29-edge-filters.md` §5, `10-ai-security-aidr.md` §9 |
| Approved tool still blocked | tool not in the device's matching filter; tool disabled; scanner rule blocks the call (`tool.blocked` event names the rule) | add to filter; enable; adjust scanner |
| "Unsanctioned tools are not allowed" violations | filter contains the wildcard and the server is not approved | approve or accept the block |
| Analyze button missing | no OpenAI/Anthropic integration | Integrations → Artificial Intelligence |
| Cannot delete a tool | used by filters | remove from filters first |
| Premium tool cannot be edited/disabled | read-only catalog item | create your own tool with the same endpoint if you need changes |
| Tool saves but Continue disabled | icon URL or category missing; URL/command missing for the transport | fill the required fields |
| Cursor/VS Code cannot connect to the gateway | client not running; port 41338 in use | start the client; `netzilo up --mcp-gateway-port <p>` |
| Headers not sent | stored under `env` for HTTP tools — confirm via `GET /api/edge/tools/{id}` | re-enter |

Events: `tool.created/updated/deleted`, `tool.allowed`, `tool.blocked`, `tool.detected`,
`tool.sanctioned`, `tool.explicitly_blocked`.
